Fonts used by the EDITOR / Main panel drawing scripts (sources_Editor, sources_Main).

Inter (Thin to Black, .otf)        - main UI font. SIL Open Font License 1.1 - see LICENSE_Inter.txt (https://github.com/rsms/inter)
DejaVu Sans Mono (.ttf)            - status line. Bitstream Vera / DejaVu free license - see LICENSE_DejaVu.txt
Michroma 400 (.woff2)              - OASYS OMNI titles. SIL Open Font License 1.1 (Google Fonts)
Montserrat 300 / 600 (.woff2)      - NAUTILUS NAVIGATOR titles. SIL Open Font License 1.1 (Google Fonts)

The scripts find these files on their own (txt2path.py: FONT_DIR, else this folder; txt2path_ext.py: EXTRA_FONT_DIR,
else this folder). Nothing to install in Windows: text is converted to vector paths before rendering.
To view the _maquette.svg files with live text in a browser or Inkscape, install Inter and DejaVu Sans Mono in Windows.
