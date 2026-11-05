# Kronos Kontrol — user manual (source)

User-facing manual for **Kronos Kontrol 1.0i** (VST3 plug-in + standalone EXE for
the Korg KRONOS, OS 3.2.3), written from the panel definition
(`panels/KronosKontrol/KronosKontrol_1.0i.panel`) and its Lua scripts
(`lua/kkMain.lua`, `kkEd.lua`, `kkEdGui.lua`, `kkPcg.lua`, `data/kronos_full.lua`).

Structure follows Diátaxis: tutorials / how-to guides / explanation / reference.

## Build locally (MkDocs Material)

```bash
pip install mkdocs-material
cd user-manual
mkdocs serve        # preview at http://127.0.0.1:8000
mkdocs build        # static site in user-manual/site/
```

Deployment target is a local folder for now; `mkdocs build` output can be copied
anywhere (no hosting required). All pages are plain Markdown under `docs/`.
