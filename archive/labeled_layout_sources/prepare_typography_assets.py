#!/usr/bin/env python3
"""Make portable Simplified-Chinese font subsets for this scientific poster."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
TEXT = 'PDINN / NDI型聚合物共混示意图PDINN : NDI型聚合物 = 1 : 0.3PDINN 小分子NDI型聚合物概念示意，非实际化学结构或实测形貌'
TEXT += ''.join(chr(i) for i in range(32, 127))
SOURCE = Path('/usr/share/fonts/opentype/noto')
try:
    from fontTools import subset
    from fontTools.ttLib import TTFont
except ImportError:
    for weight in ('Bold', 'Regular'):
        shutil.copy2(SOURCE / f'NotoSansCJK-{weight}.ttc', ASSETS)
else:
    for weight in ('Bold', 'Regular'):
        font = TTFont(SOURCE / f'NotoSansCJK-{weight}.ttc', fontNumber=2)
        options = subset.Options()
        options.name_IDs = ['*']
        options.name_legacy = True
        options.name_languages = ['*']
        options.notdef_glyph = True
        options.notdef_outline = True
        sub = subset.Subsetter(options=options)
        sub.populate(text=TEXT)
        sub.subset(font)
        # A distinct subset family name prevents collisions with full installed Noto.
        for record in font['name'].names:
            replacement = {1:'PDINN Poster Sans SC', 2:weight,
                3:f'PDINNPosterSansSC-{weight}-Subset-20261009',
                4:f'PDINN Poster Sans SC {weight}',
                6:f'PDINNPosterSansSC-{weight}',
                16:'PDINN Poster Sans SC', 17:weight}.get(record.nameID)
            if replacement:
                record.string = replacement.encode(record.getEncoding(), errors='replace')
        if 'CFF ' in font:
            cff = font['CFF '].cff
            cff.fontNames[0] = f'PDINNPosterSansSC-{weight}'
            cff.topDictIndex[0].FamilyName = 'PDINN Poster Sans SC'
            cff.topDictIndex[0].FullName = f'PDINN Poster Sans SC {weight}'
        output = ASSETS / f'PDINNPosterSansSC-{weight}.otf'
        font.save(output)
        print(output.name, output.stat().st_size, 'bytes')
license_path = Path('/usr/share/doc/fonts-noto-cjk/copyright')
if license_path.is_file():
    shutil.copy2(license_path, ASSETS / 'Noto-CJK-Copyright-and-OFL.txt')
