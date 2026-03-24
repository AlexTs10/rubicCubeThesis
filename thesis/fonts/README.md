Vendored font files for thesis reproducibility.

The serif and sans-serif files are referenced from [main.tex](/Users/alextoska/Desktop/rubicCubeThesis/thesis/main.tex) via `Path=fonts/` so Tectonic resolves them from the repository instead of macOS absolute system-font paths.

The current build uses the vendored Times/Arial/Courier files to preserve the thesis look while avoiding absolute-path font access warnings. The remaining Courier-related font-shape chatter is filtered in the LaTeX preamble because it comes from unused NFSS fallback shapes rather than missing rendered glyphs. The STIX files remain as an open-font alternative that was evaluated during the warning-reduction pass.

The Times/Arial/Courier files were copied from the local macOS system font directory for build reproducibility in this workspace. Review redistribution/license constraints before publishing them outside this environment.

Files:
- `Times New Roman.ttf`
- `Times New Roman Italic.ttf`
- `Times New Roman Bold.ttf`
- `Times New Roman Bold Italic.ttf`
- `Arial.ttf`
- `Arial Italic.ttf`
- `Arial Bold.ttf`
- `Arial Bold Italic.ttf`
- `Courier New.ttf`
- `Courier New Italic.ttf`
- `Courier New Bold.ttf`
- `Courier New Bold Italic.ttf`
- `STIXGeneral.otf`
- `STIXGeneralItalic.otf`
- `STIXGeneralBol.otf`
- `STIXGeneralBolIta.otf`
