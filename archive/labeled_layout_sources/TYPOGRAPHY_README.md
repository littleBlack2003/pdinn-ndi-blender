# PDINN / NDI poster typography and composition

## Files

- `compose_poster.py`: standalone Pillow compositor. It does not edit the Blender scene.
- `typography_overlay.svg`: transparent, editable SVG text overlay; portable subset fonts are embedded.
- `typography_overlay_outlined.svg`: the same overlay with outlined glyphs for applications that ignore embedded SVG fonts.
- `assets/PDINNPosterSansSC-Bold.otf` and `assets/PDINNPosterSansSC-Regular.otf`: renamed, Simplified-Chinese Noto Sans CJK subsets, approximately 30 KB each.
- `assets/Noto-CJK-Copyright-and-OFL.txt`: source copyright and SIL Open Font License.
- `prepare_typography_assets.py`: repeatable subset-generation script, using local Noto Sans CJK SC face index 2. Requires fontTools; otherwise copies the original TTC files.
- `typography_preview.png`: typography preview only, with simple schematic fallback color keys; the body area is intentionally blank.
- `typography_overlay_preview.png`: small transparent text-only preview.

## Compose a final render

Run from this folder:

```sh
python compose_poster.py \
  --body renders/body.png \
  --orange-icon renders/pdinn_icon.png \
  --chain-icon renders/chain_icon.png \
  --output PDINN_NDI_poster_4096.png \
  --svg typography_overlay.svg \
  --svg-paths typography_overlay_outlined.svg
```

The only runtime dependency for PNG composition is Pillow. FontTools is needed only to regenerate fonts or export outlined SVGs. The provided `.otf` fonts make PNG composition portable without system CJK fonts.

The body and icon inputs may be RGBA or full-white PNGs. The canvas is white by default. Image fitting preserves the input aspect ratio; it does not stretch molecular artwork. Icons have transparent/near-white padding trimmed automatically. Use `--body-crop L,T,R,B` to remove explicitly chosen source-image margins before fitting; no automatic content-based cropping occurs with this option. The older opt-in `--crop-body-margins` automatic-trim option is separate and cannot be combined with `--body-crop`. Neither crop method is enabled by default. Use rendered Blender icons in the final poster; if icon paths are omitted, the script displays simple flat schematic color keys.

## Layout

The default PNG is **4096 × 2731**, the nearest whole-pixel 3:2 size. `--width` changes the output size while preserving this aspect ratio. All CLI coordinates remain in 4096-wide reference units and scale automatically.

- Title: centered horizontally, visible ink begins at y = 80; 128 px bold
- Subtitle: centered horizontally, visible ink begins at y = 225; 112 px bold
- Body image box: `(0, 420, 4096, 2130)`; aspect-preserving contain fit
- Legend: label ink begins at y = 2370; 104 px bold
- Footer: centered horizontally, ink begins at y = 2620; 58 px regular
- Dark navy: `#061A4A`; footer grey: `#737781`

Optional layout controls:

```sh
# Give the gel a taller body box if needed:
python compose_poster.py --body renders/body.png --body-box 0,370,4096,2280 --output poster.png

# When the Blender render is already framed as the full poster canvas:
python compose_poster.py --body renders/full_canvas.png --render-is-poster --output poster.png

# A transparent, text-only overlay at arbitrary width:
python compose_poster.py --width 2048 --transparent --no-icons --output text_only.png
```

### Explicit source-image cropping

`--body-crop L,T,R,B` specifies the left, top, right, and bottom bounds **in the input body image**, before resizing to the poster body box. Right and bottom are exclusive pixel edges. It never guesses where the slab begins or ends.

- If all four values are in `0..1`, they are interpreted as fractions of the source width/height
- Otherwise, values are source-image pixel bounds
- Prefix `frac:` or `px:` to make the unit explicit, including an unusual one-pixel crop
- Fractional edges are multiplied by the corresponding source dimension, then rounded to whole pixels
- Out-of-bounds or empty crops are rejected rather than silently padded or clamped
- The default remains no crop; fitting then preserves aspect ratio
- Crop fractions scale with any body-render resolution. Pixel crops refer to the input resolution and do not scale with output `--width`

```sh
# Illustrative fractional crop: retain the central 90% width and 70% height.
# Inspect the body render first and choose margins that do not cut off the gel.
python compose_poster.py --body renders/body.png \
  --body-crop 0.05,0.15,0.95,0.85 --output poster.png

# Explicit source-pixel bounds for a 4096 × 2458 body render:
python compose_poster.py --body renders/body.png \
  --body-crop px:128,300,3968,2140 --output poster.png
```

A 1:0.60 body render has an uncropped aspect ratio of approximately 1.667. The default poster body box is approximately 2.395, so a contain fit may have substantial horizontal whitespace unless source top/bottom margins are removed or `--body-box` is made taller. Select a crop by inspecting the rendered slab; do not crop real geometry merely to match an aspect ratio.

Additional controls: `--body-fit contain|cover|stretch`, `--title-y`, `--title-size`, `--subtitle-y`, `--subtitle-size`, `--legend-y`, `--footer-y`. `cover` introduces an additional centered fit crop, so use the default `contain` when you want **only** your explicit source crop. `stretch` intentionally changes aspect ratio and should normally be avoided.

## Wording and scientific limits

The exact labels are:

- `PDINN / NDI型聚合物共混示意图`
- `PDINN : NDI型聚合物 = 1 : 0.3`
- `PDINN 小分子`
- `NDI型聚合物`
- `概念示意，非实际化学结构或实测形貌`

This is a conceptual blend illustration. Its molecular motifs, film geometry, colors, spacing, packing, and depth do **not** claim actual chemical structures or measured morphology. The ratio label **1 : 0.3** is retained as requested; it is **not an object-count ratio**, and no mass, molar, volume, or repeat-unit interpretation is asserted. The number of rendered molecules or polymer segments must not be treated as quantitative evidence for that ratio.

The font subsets cover all requested labels plus printable ASCII. If the Chinese wording changes, regenerate the subsets after adding new text to `TEXT` in `prepare_typography_assets.py`, or use a full Noto CJK font.
