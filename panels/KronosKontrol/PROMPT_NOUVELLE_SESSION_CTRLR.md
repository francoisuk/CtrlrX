# Prompt — nouvelle session : panneau CTRLR « Kronos Kontrol » exporté en VST3

*(Préparé le 16 oct. 2026. À coller tel quel au début d'une nouvelle session reliée au PC de l'auteur.)*

> **Mise à jour du 24 oct. 2026 — le § 4 est FAIT.** Le CSV a 124 lignes
> (IFX6-12, TFX2, banques + U-A/AA + GM, MIXER/PAN, Module Control, Drum
> Track Volume/Mute ; FX inversés, GE en fn 6D, Drum Track On en fn 6E,
> colonne Tested renseignée). `PROJECT_LAYOUT.md` a été réécrit (chemins
> `reference\`, périmètre = le rack complet). Le dossier `consolidate\` est
> remplacé par `reference\`. Le fichier vide `New Text Document.txt` a été
> supprimé. Le rack est implémenté : `KronosKontrol.panel` complet-0.96
> (testé 0.95 le 16 oct. ; 0.96 à tester — voir `RESUME.md` à la racine du corpus). Les chemins
> de ce prompt qui citent `04_Outils\bonus\VST3\` sont historiques : tout
> est maintenant dans ce projet (`C:\Korg\kronos-corpus\ctrlr-project`).
>
> **Mise à jour du 24 oct. 2026 (soir) — phase éditeur.** Le panneau est
> passé en **complet-0.97** : onglets RACK (le rack 0.96 inchangé) / EDIT,
> étape E1 de l'éditeur construite (lecture du dump Programme : requête 4A,
> réception 4B, conversion 7 bits, affichage nom / version / catégorie /
> gamme / effets / moteurs EXi). Vérification statique faite (99 contrôles,
> 0 échec) ; **test sur le KRONOS à faire** — fiche `EDITOR_PLAN.md` § 9,
> résultats à noter dans `RESUME.md` (racine du corpus, section « complet-0.97 »). Plan
> complet de l'éditeur (E1-E7) : `EDITOR_PLAN.md`. Le rack 0.96 reste la
> référence ; l'éditeur est un ajout (onglets), pas une réécriture.

---

Bonjour. On démarre la création d'un **panneau CTRLR « Kronos Kontrol »** pour piloter un **Korg KRONOS (OS 3.2.3)**, puis son
**export en plugin VST3** (comme `Tr Rack Editor.vst3`, exporté depuis CTRLR). Réponds en français, phrases courtes ; mes crédits
sont limités : pas de longues explications, travaille par petites étapes testées.

## 1. Accès et lecture (dans cet ordre)

1. Demande l'accès à `C:\Korg\Manuals Le grand livre du KRONOS` (et `C:\Korg\Manuals Kronos 3.2.x` si besoin des guides PDF).
2. Lis dans le projet claude.ai : `claude/v2/REPRISE_M4L.md` (état final du device Max for Live, testé le 16 oct. 2026).
3. Dans `04_Outils\bonus\VST3\` :
   - `reference\kronos_kontrol_export\README.md` puis `SYSEX_KRONOS.md` — **référence SysEx à jour et testée** ;
   - `reference\kronos_kontrol_export\kronos_sysex.py` (lance l'auto-test) et `ctrlr\kronos_sysex.lua` (mêmes fonctions en Lua) ;
   - `reference\kronos_kontrol_export\docs\LISEZMOI_panneau.md` + `panneau_rack\kronos-kontrol-rack.png` — **le design à reproduire** ;
   - `panels\KronosKontrol\PROJECT_LAYOUT.md`, `PHASE_A.md`, `parameter_map.csv`, `CTRLR_IDIOMS.md` — travail d'une session
     antérieure (voir § 4 : à mettre à jour) ;
   - `build\BUILD_README.md`, `panels\PANELS_README.md` — runtime CTRLR et règles.
4. Regarde `reference\kronos_kontrol_export\panneau_rack\kronos-kontrol-rack.png`.

## 2. Objectif

Un panneau CTRLR qui reprend **le rack tel quel** (façade 1500 × 414 px, `rack_fond.png` en image de fond, commandes posées aux
coordonnées de la maquette), avec **les mêmes fonctions que le device Max for Live** :
- 16 encodeurs CC (Filter Freq 74, Reso 71, Filter EG 79, EG Release 72, Knob Mod 1-4 17/19/20/21, LFO1 Speed 76, Depth 77,
  Ribbon 16, Port Time 5, ENV A/D/S/R 73/75/70/72) avec bandes de noms ;
- PROGRAM (numéro + nom du son, ▲▼), COMBI / PROG (SysEx 4E), SW1/SW2 (CC80/81) ;
- BANK SELECT I-A…I-G / U-A…U-G + U-A/AA, menu GM (CC0, CC32, Program Change ; Bank Map KORG) ;
- FX SWITCHES IFX1-12, MFX1-2, TFX1-2 (fonction 43, TYP 6 Program / 23 Combi, **valeur inversée** : 0 = On) ;
- pavé X-Y (CC118/119) + HOLD ;
- MIXER / PAN : 8 encodeurs = volume / pan des timbres 1-8 (Combi) ; OSC1, OSC2, Drum Track, Master (Program) ;
- KARMA : switches 1-8 (CC102-109), GE SELECT + menu des 3 584 GE (fonction 43 TYP 1 / TYP 3 module), ON/OFF (CC14), LATCH (CC31),
  SCENES 1-8 (CC30), KARMA SLIDERS 1-8 (CC22-29), voyants MODULE ; DRUM TRACK ON/OFF + MUTE (fonction 43 TYP 0 PID 10 / 40) ;
- réception : décoder ce que le KRONOS renvoie (43, 4E, 42, 24) pour mettre le panneau à jour, avec un **drapeau de garde**
  contre les boucles (PROJECT_LAYOUT § 8.3).
Ensuite : **export VST3** depuis CTRLR (File › Export › instance, à vérifier dans la version 5.6.23) et test dans Live 12.

## 3. Ce qui fait foi (règles)

1. **SysEx : `reference\kronos_kontrol_export\kronos_sysex.py` et `SYSEX_KRONOS.md`** (octets vérifiés sur le KRONOS le 16 oct. 2026).
   Ils remplacent la règle de PROJECT_LAYOUT § 9.1 (« ne pas partir du MIDI Implementation ») : le device testé a été construit
   avec le MIDI Implementation (`reference\MIDI_implementation\`) et les tests l'ont confirmé.
2. **Lua de CTRLR** : toute méthode utilisée doit être trouvée dans `build\CtrlrX-dnaldoog`, puis `CtrlrX-damiensellier`, puis
   `ctrlr-master` (BUILD_README). Sinon, le dire et s'arrêter. `ctrlr\kronos_sysex.lua` a été écrit sans test : vérifier ses appels
   (`CtrlrMidiMessage`, `panel:sendMidiMessageNow`, `getData():getByte`, `console`, `getModulatorByName`).
3. Une tranche à la fois, testée sur le KRONOS avant la suivante (SAVIHost3 ou Live 12, port KRONOS en entrée ET en sortie).
4. Jamais de Write / Store sur le KRONOS. Ne pas modifier `build\`, ni `panels\TR-Rack-Editor-main\`, ni le device Max for Live.
5. Données statiques : `panels\KronosKontrol\data\kronos_data.lua` (4 233 noms, 3 584 GE) — déjà généré.

## 4. À corriger dans le travail précédent (avant le code)

- `parameter_map.csv` (66 lignes) date d'avant le rack : **ajouter** IFX6-12, TFX2, MFX/TFX Combi complets, BANK SELECT 14 boutons +
  U-A/AA, MIXER/PAN (timbres 1-8, OSC1/OSC2, Drum Track, Master), Drum Track Volume / Mute ; **corriger** les interrupteurs FX
  (valeur inversée, 0 = On) ; GE : valeur 21 bits (vM = n / 128, vL = n % 128), pas « bank / num » ; marquer « Tested » d'après
  `SYSEX_KRONOS.md`.
- `PROJECT_LAYOUT.md` : chemins (`C:\Korg\CTRLR Project\…` → `04_Outils\bonus\VST3\…`), dossier `consolidate\` remplacé par
  `reference\`, périmètre v1 (le rack complet, pas seulement les CC), règle § 9.1 (voir § 3.1 ci-dessus).
- `PANELS_README.md` parle de `panels\TR-Rack\` : le dossier réel est `panels\TR-Rack-Editor-main\` et ne contient qu'un
  `.bpanelz` (panneau compressé) et son `.vst3` exporté. Pour lire ses idiomes, l'ouvrir dans CTRLR et l'enregistrer en `.panel`
  (XML) dans `panels\KronosKontrol\etude_TR-Rack\` (copie de travail).
- Fichier vide `panels\KronosKontrol\New Text Document.txt` : à supprimer par l'auteur.

## 5. Plan proposé

- **Étape 0** : vérifier le runtime (CTRLR 5.6.23 dans SAVIHost3 ou Live 12), ouvrir TR-Rack, relever : callback MIDI entrant,
  recherche d'un modulateur, `setValue` sans renvoi, envoi SysEx, image de fond, export d'instance.
- **Étape 1** : panneau 1500 × 414 avec `rack_fond.png` en fond, un encodeur CC74 et l'afficheur du nom (tranche testée).
- **Étape 2** : PROG/COMBI + banques + nom du son ; **Étape 3** : FX ; **Étape 4** : MIXER/PAN ; **Étape 5** : KARMA, Drum Track,
  X-Y ; **Étape 6** : réception / mise à jour du panneau ; **Étape 7** : export VST3, test dans Live, mode d'emploi FR/EN/ES.
- Sauvegarder à chaque étape `panels\KronosKontrol\KronosKontrol.panel` (XML lisible) et noter l'état dans
  `RESUME.md` à la racine du corpus.

## 6. Réglages du KRONOS (rappel)

GLOBAL › Bank Map KORG ; Enable Exclusive ; Enable Control Change ; canal global 1 ; CC KARMA : Reset Controller MIDI Assign ›
CC Default puis Write Global Setting.
