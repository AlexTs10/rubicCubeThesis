Vendored open font files for thesis reproducibility.

The serif and sans-serif files are referenced from [`main.tex`](../main.tex) via `Path=fonts/` so XeLaTeX-compatible tooling and Tectonic resolve them from the repository instead of macOS absolute system-font paths.

The current build uses the vendored STIX files for serif and sans-serif text and the open DejaVu Sans Mono files for code listings. This avoids redistributing proprietary system fonts in the public repository while keeping the Greek XeLaTeX/Tectonic build reproducible.

Do not add copied macOS or Windows system font files here. Prefer open fonts that can be redistributed with the project, or require local system fonts without committing them.

Files:
- `STIXGeneral.otf`
- `STIXGeneralItalic.otf`
- `STIXGeneralBol.otf`
- `STIXGeneralBolIta.otf`
- `DejaVuSansMono.ttf`
- `DejaVuSansMono-Oblique.ttf`
- `DejaVuSansMono-Bold.ttf`
- `DejaVuSansMono-BoldOblique.ttf`
