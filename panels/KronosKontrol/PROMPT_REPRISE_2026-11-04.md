# Prompt — reprise du panneau « Kronos Kontrol » après 1.0h (4 nov. 2026)

*À coller tel quel au début d'une nouvelle session reliée au PC de l'auteur.*

---

Bonjour. On reprend le panneau CTRLR « Kronos Kontrol » là où `REPRISE_CODAGE_1.0h.md` s'est arrêté.
Réponds en français, phrases courtes, petites étapes testées — mes crédits sont limités.

## 1. Lecture (dans cet ordre)

1. `panels/KronosKontrol/PROMPT_NOUVELLE_SESSION_CTRLR.md` (les règles ; il fait foi).
2. `REPRISE_CODAGE_1.0h.md` (état + « To resume » § 2).
3. `panels/KronosKontrol/PROJECT_LAYOUT.md`, `BUILD_EXPORT.md`, `CTRLRX_MIGRATION.md`.
4. `PR337_ANALYSIS.md` (la sonde CtrlrPanelProbe du PR #337).

L'étiquette d'intégrité de `C:\Korg\kronos-corpus` est réglée : tout tourne dans l'arbre, plus besoin de copier hors du corpus.

## 2. Tâche 1 — exports 1.0h (avec moi devant le PC)

Suivre `REPRISE_CODAGE_1.0h.md` § 2, dans l'ordre :

1. Après le redémarrage, lancer **CtrlrX seul** (pas REAPER en même temps), ouvrir `KronosKontrol_1.0h.panel`.
2. `.\Prepare_Exe_Export.ps1`, puis Export restricted instance, licence = `panels/KronosKontrol/licence/EULA.txt` → `panels\KronosKontrol\exe\Kronos Kontrol 1.0h_restricted.exe`.
3. Relancer le script, lancer le .exe une fois, puis `-Check`. Sur I-A000, vérifier encodeurs / sliders / MIXER-PAN = 127 / 112 / 127.
4. REAPER avec **uniquement le VST3 CtrlrX** dans le projet : `.\Prepare_VST3_Export.ps1`, charger le panneau 1.0h, Export restricted + EULA → `panels\KronosKontrol\vst3\KronosKontrol_1.0h_restricted.vst3`, re-scan, charger, `-Check`.
5. Mettre à jour `BUILD_EXPORT.md` : la réponse à « attach a license » est maintenant **Oui** + EULA.txt (le doc dit encore « No » pour les builds de test).

## 3. Tâche 2 — points ouverts de la migration 5.6.36 (`CTRLRX_MIGRATION.md`)

- `panelVersionMajor/Minor` (encore 0.1) → 1.0.
- `kkU` (`lua/kkEdGui.lua:17-20`) : sous 5.6.36 les chaînes Lua sont lues en UTF-8 ; vérifier le texte accentué dans l'éditeur, et neutraliser `kkU` s'il abîme les accents.
- `getValue()` renvoie un décimal depuis 5.6.32 : passer en `getValueInt()` partout où la valeur sert d'index ou d'octet SysEx.

## 4. Tâche 3 — la sonde CtrlrPanelProbe (PR #337) — APRÈS la tâche 1, jamais avant

Ne pas la lancer tant que les exports 1.0h ne sont pas faits. Ensuite (`PR337_ANALYSIS.md` § 4.3) :

1. Copier depuis `build/CtrlrX-pr337/` les `Tests/probe_*` et le bloc +53 lignes de `Tests/CMakeLists.txt` sur le clone épinglé `build/CtrlrX-damiensellier/CtrlrX` (tag v5.6.36), puis `cmake --build build --target CtrlrPanelProbe`.
2. Écrire un petit harnais Python d'assertions : lancer la sonde, lire le rapport JSON, comparer `deviceMidiOut` octet par octet avec `scripts/kronos_sysex.py`, comparer `finalState` avec `parameter_map.csv`. **La sonde rapporte, ne juge pas** : c'est le harnais qui compare.
3. Baseline sur le panneau 1.0h (5 boutons du rack, encodeurs, MIXER/PAN, puis chemin d'écriture éditeur), puis étendre à chaque tranche suivante — même rythme que les fiches hardware.
4. La sonde tourne dans le corpus ; penser au cache de ressources `%APPDATA%\Kronos Kontrol` (les scripts Prepare le vident).

## 5. Règles permanentes

- Un seul auteur à la fois sur `lua/kkMain.lua` et `sources/build_panel.py`.
- Reconstruire par `python sources/build_panel.py` ; ne jamais éditer le .panel généré à la main.
- Règle de lettre de version (`EDITOR_PLAN.md` § 5) ; `VERSION` uniquement dans `sources/build_panel.py`.
- Ne jamais sauvegarder le panneau en mode édition (bogue amont signalé dans PR #337).
- À chaque étape : mettre à jour `parameter_map.csv`, `PROJECT_LAYOUT.md` et la note REPRISE.
