#!/usr/bin/env python3
"""Compose the PDINN/NDI poster using Pillow, without Blender dependencies.

All coordinates use a 4096-pixel-wide reference canvas and scale with --width.
PNG body/icon renders may be transparent or on white. Default fitting preserves
aspect ratio and never crops the body. SVG typography remains editable text.
"""
from __future__ import annotations
import argparse
import base64
from html import escape
from math import isfinite
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
BASE_WIDTH = 4096
NAVY = '#061A4A'
GREY = '#737781'
TEXTS = {
    'title': 'PDINN / NDI型聚合物共混示意图',
    'subtitle': 'PDINN : NDI型聚合物 = 1 : 0.3',
    'pdinn': 'PDINN 小分子',
    'ndi': 'NDI型聚合物',
    'footer': '概念示意，非实际化学结构或实测形貌',
}


def font_path(weight='Bold'):
    for p in (ASSETS / f'PDINNPosterSansSC-{weight}.otf',
              ASSETS / f'NotoSansCJK-{weight}.ttc',
              Path('/usr/share/fonts/opentype/noto') / f'NotoSansCJK-{weight}.ttc'):
        if p.is_file():
            return p
    raise FileNotFoundError('Missing bundled poster font; run prepare_typography_assets.py')


def get_font(size, weight='Bold'):
    p = font_path(weight)
    return ImageFont.truetype(str(p), max(1, round(size)), index=2 if p.suffix == '.ttc' else 0)


def rect_arg(value):
    try:
        values = tuple(float(v) for v in value.split(','))
        if len(values) != 4 or not all(isfinite(v) for v in values) or values[2] <= values[0] or values[3] <= values[1]:
            raise ValueError
        return values
    except ValueError as e:
        raise argparse.ArgumentTypeError('Expected x0,y0,x1,y1 with positive width/height') from e


def body_crop_arg(value):
    """Parse explicit L,T,R,B crop bounds in source pixels or source fractions."""
    mode = None
    if ':' in value:
        mode, value = value.split(':', 1)
        if mode not in ('px', 'frac'):
            raise argparse.ArgumentTypeError('Crop unit must be px: or frac:')
    bounds = rect_arg(value)
    if mode is None:
        mode = 'frac' if all(0 <= v <= 1 for v in bounds) else 'px'
    if min(bounds) < 0 or (mode == 'frac' and max(bounds) > 1):
        raise argparse.ArgumentTypeError('Fractional crop bounds must be within 0..1; pixel bounds must be nonnegative')
    return mode, bounds


def crop_body(image, crop):
    """Apply exactly the requested source-image rectangle, never content detection."""
    mode, bounds = crop
    if mode == 'frac':
        l, t, r, b = bounds
        bounds = (l*image.width, t*image.height, r*image.width, b*image.height)
    l, t, r, b = bounds
    if not (0 <= l < r <= image.width and 0 <= t < b <= image.height):
        raise ValueError(f'Body crop {bounds} lies outside source image {image.width} × {image.height}')
    pixels = tuple(round(v) for v in bounds)
    if pixels[2] <= pixels[0] or pixels[3] <= pixels[1]:
        raise ValueError('Body crop is less than one pixel after rounding')
    return image.crop(pixels)


def trim_image(image, threshold=7):
    """Remove transparent or near-white margins, with a small protective border."""
    im = image.convert('RGBA')
    alpha = im.getchannel('A')
    if alpha.getextrema()[0] < 255:
        bounds = alpha.getbbox()
    else:
        white = Image.new('RGB', im.size, 'white')
        difference = ImageChops.difference(im.convert('RGB'), white)
        r, g, b = difference.split()
        mask = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda p: 255 if p > threshold else 0)
        bounds = mask.getbbox()
    if not bounds:
        return im
    pad = max(2, round(max(im.size) * .007))
    l, t, r, b = bounds
    return im.crop((max(0,l-pad), max(0,t-pad), min(im.width,r+pad), min(im.height,b+pad)))


def put_image(canvas, image, box, fit='contain', trim=False):
    image = image.convert('RGBA')
    if trim:
        image = trim_image(image)
    x0, y0, x1, y1 = [round(v) for v in box]
    width, height = x1-x0, y1-y0
    if fit == 'stretch':
        size = (width, height)
    else:
        ratio = (max if fit == 'cover' else min)(width/image.width, height/image.height)
        size = (max(1,round(image.width*ratio)), max(1,round(image.height*ratio)))
    resized = image.resize(size, Image.Resampling.LANCZOS)
    # Clipping occurs only within this layer, so a cover fit cannot cover text.
    layer = Image.new('RGBA', (width,height))
    layer.alpha_composite(resized, ((width-size[0])//2, (height-size[1])//2))
    canvas.alpha_composite(layer, (x0,y0))


def fallback_icon(kind):
    """Simple schematic color keys used only when rendered icon files are absent."""
    from math import cos, sin, pi
    im = Image.new('RGBA', (1000,260))
    d = ImageDraw.Draw(im)
    if kind == 'pdinn':
        d.line([(185,127),(246,148),(291,136),(334,151),(382,137)],fill='#D47B08',width=17,joint='curve')
        d.line([(619,137),(666,151),(710,133),(756,151),(812,107)],fill='#D47B08',width=17,joint='curve')
        for x in [406,501,596]:
            pts=[(x+63*cos(pi/3*i),130+70*sin(pi/3*i)) for i in range(6)]
            d.polygon(pts,fill='#FBAF32',outline='#D77C09',width=8)
            d.line([(x-29,80),(x+29,80),(x+52,121)],fill='#FFE3A4',width=5)
    else:
        pts=[(70,138),(220,119),(375,150),(536,136),(698,110),(852,144),(938,129)]
        d.line(pts,fill='#3275B5',width=22,joint='curve')
        d.line([(x,y-5) for x,y in pts],fill='#87BCEA',width=6,joint='curve')
        for x,y in pts[1:-1]:
            d.rounded_rectangle((x-60,y-43,x+60,y+43),radius=13,fill='#368ED0',outline='#1D649F',width=6)
            d.line([(x-48,y-27),(x+47,y-27)],fill='#B4E3FF',width=5)
    return im


def text_specs(args):
    return [
        dict(key='title',x=2048,y=args.title_y,size=args.title_size,weight='Bold',color=NAVY,anchor='center'),
        dict(key='subtitle',x=2048,y=args.subtitle_y,size=args.subtitle_size,weight='Bold',color=NAVY,anchor='center'),
        dict(key='pdinn',x=1228,y=args.legend_y,size=104,weight='Bold',color=NAVY,anchor='left'),
        dict(key='ndi',x=2976,y=args.legend_y,size=104,weight='Bold',color=NAVY,anchor='left'),
        dict(key='footer',x=2048,y=args.footer_y,size=58,weight='Regular',color=GREY,anchor='center'),
    ]


def draw_text(canvas, spec, scale):
    font = get_font(spec['size']*scale,spec['weight'])
    text=TEXTS[spec['key']]
    box = font.getbbox(text)
    x = spec['x']*scale
    if spec['anchor']=='center':
        x -= font.getlength(text)/2
    # y is the top of visible ink, not a font-dependent ascender or baseline.
    y = spec['y']*scale-box[1]
    ImageDraw.Draw(canvas).text((round(x),round(y)),text,font=font,fill=spec['color'])


def make_svg(args, output, outlined=False):
    """Write a transparent typography overlay, with embedded fonts or paths."""
    width=args.width
    height=round(width*2/3)
    lines=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 4096 {height*4096/width:.6f}">',
        '<title>PDINN / NDI型聚合物共混示意图：文字叠加层</title>',
        '<desc>概念示意，非实际化学结构或实测形貌。配比标签不是可视化对象数量比。</desc>']
    if not outlined:
        lines.append('<defs><style>')
        for weight,num in [('Bold',700),('Regular',400)]:
            path=font_path(weight)
            fontdata=base64.b64encode(path.read_bytes()).decode('ascii')
            lines.append(f"@font-face {{font-family:'PDINN Poster Sans SC';font-style:normal;font-weight:{num};src:url(data:font/otf;base64,{fontdata}) format('opentype');}}")
        lines.append('</style></defs>')
    for spec in text_specs(args):
        text=TEXTS[spec['key']]
        font=get_font(spec['size'],spec['weight'])
        bbox=font.getbbox(text)
        advance=font.getlength(text)
        x=spec['x']-(advance/2 if spec['anchor']=='center' else 0)
        baseline=spec['y']-bbox[1]+font.getmetrics()[0]
        if not outlined:
            lines.append(f'<text id="{spec["key"]}" x="{x:.3f}" y="{baseline:.3f}" font-family="PDINN Poster Sans SC, Noto Sans CJK SC, sans-serif" font-size="{spec["size"]}" font-weight="{700 if spec["weight"]=="Bold" else 400}" fill="{spec["color"]}" textLength="{advance:.3f}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>')
        else:
            from fontTools.ttLib import TTFont
            from fontTools.pens.svgPathPen import SVGPathPen
            path=font_path(spec['weight'])
            tt=TTFont(path,fontNumber=2 if path.suffix=='.ttc' else -1)
            cmap=tt.getBestCmap()
            glyphs=tt.getGlyphSet()
            unit_scale=spec['size']/tt['head'].unitsPerEm
            lines.append(f'<g id="{spec["key"]}" fill="{spec["color"]}" aria-label="{escape(text)}">')
            for index,ch in enumerate(text):
                name=cmap.get(ord(ch),'.notdef')
                pen=SVGPathPen(glyphs)
                glyphs[name].draw(pen)
                d=pen.getCommands()
                if d:
                    xpos=x+font.getlength(text[:index])
                    lines.append(f'<path transform="translate({xpos:.4f},{baseline:.4f}) scale({unit_scale:.7f},{-unit_scale:.7f})" d="{d}"/>')
            lines.append('</g>')
            tt.close()
    lines.append('</svg>')
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text('\n'.join(lines),encoding='utf-8')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--body',type=Path,help='Blender-rendered body image (PNG, RGBA or white background)')
    p.add_argument('--orange-icon',type=Path,help='Optional rendered orange PDINN legend icon')
    p.add_argument('--chain-icon',type=Path,help='Optional rendered blue polymer legend icon')
    p.add_argument('--output','-o',type=Path,default=ROOT/'poster.png')
    p.add_argument('--width',type=int,default=4096,help='Output width; height is round(width * 2 / 3)')
    p.add_argument('--body-box',type=rect_arg,default=(0,420,4096,2130),help='Reference-pixel body box; default 0,420,4096,2130')
    p.add_argument('--body-fit',choices=['contain','cover','stretch'],default='contain')
    crop_options=p.add_mutually_exclusive_group()
    crop_options.add_argument('--body-crop',type=body_crop_arg,help='Explicit source bounds L,T,R,B: pixels or fractions in 0..1; optional px: / frac: prefix')
    crop_options.add_argument('--crop-body-margins',action='store_true',help='Optional automatic transparent/near-white trimming; mutually exclusive with --body-crop')
    p.add_argument('--render-is-poster',action='store_true',help='Body is already framed as the full 3:2 poster; place full-canvas')
    p.add_argument('--no-icons',action='store_true',help='Omit legend icon artwork, retaining its labels')
    p.add_argument('--transparent',action='store_true',help='Transparent canvas instead of white (useful for overlay-only export)')
    p.add_argument('--title-y',type=float,default=80,help='Title visible-ink top, in reference pixels')
    p.add_argument('--title-size',type=float,default=128)
    p.add_argument('--subtitle-y',type=float,default=225)
    p.add_argument('--subtitle-size',type=float,default=112)
    p.add_argument('--legend-y',type=float,default=2370,help='Legend text visible-ink top')
    p.add_argument('--footer-y',type=float,default=2620)
    p.add_argument('--svg',type=Path,help='Also write editable, embedded-font SVG text overlay')
    p.add_argument('--svg-paths',type=Path,help='Also write outlined SVG text overlay (fontTools required)')
    args=p.parse_args(argv)
    if args.width<64:
        p.error('--width must be at least 64 pixels')
    if args.body_crop and not args.body:
        p.error('--body-crop requires --body')
    scale=args.width/BASE_WIDTH
    height=round(args.width*2/3)
    canvas=Image.new('RGBA',(args.width,height),(255,255,255,0 if args.transparent else 255))
    if args.body:
        box=(0,0,args.width,height) if args.render_is_poster else tuple(v*scale for v in args.body_box)
        body=Image.open(args.body)
        if args.body_crop:
            try:
                body=crop_body(body,args.body_crop)
            except ValueError as e:
                p.error(str(e))
        put_image(canvas,body,box,args.body_fit,args.crop_body_margins)
    if not args.no_icons:
        center_y=args.legend_y+54
        icons=[(args.orange_icon,'pdinn',(610,center_y-110,1165,center_y+110)),
               (args.chain_icon,'ndi',(1930,center_y-110,2887,center_y+110))]
        for path,kind,box in icons:
            icon=Image.open(path) if path else fallback_icon(kind)
            put_image(canvas,icon,tuple(v*scale for v in box),'contain',trim=True)
    for spec in text_specs(args):
        draw_text(canvas,spec,scale)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if not args.transparent:
        canvas=canvas.convert('RGB')
    canvas.save(args.output,dpi=(300,300))
    if args.svg:
        make_svg(args,args.svg)
    if args.svg_paths:
        make_svg(args,args.svg_paths,outlined=True)
    print(f'Saved {args.output} ({args.width} × {height})')

if __name__=='__main__':
    main()
