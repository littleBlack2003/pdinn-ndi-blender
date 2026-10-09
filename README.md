# PDINN / NDI Blender archive

Private archive of the current editable jelly model, two presentation GLB variants, transparent renders and the recovered source scripts.

## Current files

- `pdinn_jelly.blend`: canonical editable Blender model, Library v11; SHA256 `8dec516fb834651ab3ea52e99382c1d191b5adc9dcb67abbfcdfc754de04b82a`
- `exports/PDINN_NDI_PowerPoint_3D.glb`: self-contained presentation model with a lightly alpha-blended jelly shell
- `exports/PDINN_NDI_PowerPoint_Matte_Boundary_Copy.glb`: separate copy with an opaque blue-grey perimeter outline; molecular geometry/materials are preserved
- `renders/PDINN_Jelly_Final_4K_Transparent.png`: 3840×2304 transparent 16-bit RGBA master
- `renders/PDINN_Jelly_Final_4K_Transparent_8bit.png`: 8-bit delivery copy
- `renders/views/`: top, low-side, opposite-oblique and intentionally cropped close-up views
- `renders/Matte_Boundary_Copy_Preview.png`: preview of the matte export
- `scripts/`, `assets/` and the validation JSONs: recovered procedural sources, user reference images, font subsets/license and milestone evidence

The model contains 135 PDINN motifs and 141 NDI cores in 8 curved chains and 4 depth layers. PDINN is #F0B47C; NDI is #BE7A9A. Current view is 42° elevation/24° azimuth. The seven-ring PDINN and four-ring NDI icons, including the requested upper/lower NDI connectors, are conceptual. They omit full atom labels, bond orders, carbonyls and copolymer detail. Counts are not stoichiometry; this is not a measured morphology or complete chemical structure.

## Open, render and use

Open `pdinn_jelly.blend` with Blender 4.3.2 or a compatible newer build. The restored scene was opened and checked in 4.3.2. It has no required missing external assets; two unused legend images are packed despite stale historical source paths.

The saved project is ready to render. To use the recovered rendering scripts, work in a copy of the repository, from its root:

```sh
blender -b -t 8 --python scripts/render_final_4k.py
blender -b -t 8 --python scripts/render_quality.py
```

The final script saves its scene/checkpoint and writes the named 4K master and validation JSON. It uses Cycles CPU, adaptive max 512/min 64 samples, threshold 0.01, 16 total/12 transmission/16 transparent bounces. The delivered master had no denoising; another Blender build may enable supported OpenImageDenoise, so rerenders need not be pixel-identical. The quick script renders 1200×720 with 48 samples without overwriting the saved 4K scene configuration. Current rendering needs Blender's Python modules and the Python standard library. Historical typography scripts additionally use Pillow/fontTools; the Noto license is retained.

For presentation use, insert the desired `.glb` as a local 3D model. Both exports are self-contained and were reimport-checked in Blender, but were not tested inside PowerPoint. Standard alpha blending in the jelly GLB does not reproduce Blender's true transmission/refraction; the matte variant gives a clearer opaque boundary. Some material names retain legacy blue/orange wording; actual PBR colors are the current palette.

The exact post-v9 GLB exporter and alternate-view scripts were lost after the source archive was saved. The deliverable binaries and recorded camera/export settings are retained in `docs/RECORDED_DERIVATIVE_SETTINGS.json`; that file is a settings record, not a recovered exporter. Do not blindly run historical incremental modeling scripts over the current model.

## Integrity and history

Run `python3 tools/verify_archive.py` or `sha256sum -c SHA256SUMS` at repository root. `ARCHIVE_MANIFEST.json` records each file's bytes and SHA256. Original source identities and explicit omissions are under `provenance/`. The source ZIP itself, seven old .blend checkpoints and duplicate temporary previews are retained in Library ZIP v9 instead of duplicated here. No original source/model/render bytes were modified for this archive; the top-level README and archive notes are new.

See `docs/VERSION_HISTORY.md`. The repository remains private. The bundled Noto font license applies to its font assets; no new project-wide open-source license has been assigned.
