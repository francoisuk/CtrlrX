# Kronos Kontrol — notes de développement (état au 16 oct. 2026, 16 h 00 — projet terminé)

## Fichiers
- `Kronos Kontrol OS3.2.3_FR.amxd`, `…_EN.amxd`, `…_ES.amxd` : **le device**, interface = rack (`panneau_rack\maquettes\kronos-kontrol-rack.png`, maquette finale).
  Les trois ne diffèrent que par le bouton de la bande (OUVRIR LE RACK / OPEN RACK / ABRIR EL RACK, `KK_LANG` dans fix6.py).
- `Kronos Kontrol v3.2.3.amxd` : ancienne version (interface d'origine), testée et fonctionnelle. Ne pas la réécrire.
- `Manuels\` : guides d'utilisation Word FR / EN / ES.
- `sources\build.py` reconstruit les trois .amxd : passes `edit_kk.py`, `fix2.py` … `fix5.py`, puis **`fix6.py`** (interface rack).
  Entrées : `base\kronos_kontrol_v1.json`, `base\conteneur.json`, `base\rack_fond.png`, `names.json`, `ge_kronos.json`.
- `base\rack_fond.png` est produit par `panneau_rack\sources\fond_device.py` (la maquette sans les parties actives).
  Si la maquette change : `python fond_device.py ..\..\sources\base\rack_fond.png` puis `python build.py`.
- Avec Live 12, aucun .maxpat externe : tout le SysEx sort par `midiout` (fix5).

## Architecture du device (fix6.py)
- Bande du device (169 px, largeur 232) : KRONOS / KONTROL · KORG, nom du son, bouton « OUVRIR LE RACK »
  (`live.text` → `t b` → `open` → `pcontrol` → `[p KronosKontrolRack]`).
- `[p KronosKontrolRack]` : fenêtre 1500 × 414 en présentation, `fpic rack_fond.png` au fond, les commandes
  existantes déplacées aux coordonnées de la maquette (1 unité = 1 px).
  **Ordre d'affichage : dans le JSON, le premier objet de la liste est devant** (le fond est donc en dernier).
- Chaque cordon qui traverse la frontière sous-patch / patch principal est remplacé par `s ---kkN` / `r ---kkN`
  (203 paires, locales au device) ; les `s` sont placés à la position de l'ancienne destination pour garder l'ordre.
- Boutons : les `live.toggle` / `live.text` sont transparents, le fond dessine le bouton ; état allumé = voile bleu
  (jaune pour COMBI/PROG et SCENES).
- BANK SELECT : 14 `live.text` (clic → message k) + U-A/AA → `pak` → `expr $i1 + ($i1 >= 7) * $i2 * 7` → ancien
  `live.tab` obj-14 (21 banques, caché, garde toute la logique). Affichage : obj-14 → `expr $i1 - ($i1 >= 14) * 7` →
  `== k` → 14 voyants `live.toggle` (ignoreclick) exactement sous les boutons ; obj-14 → `>= 14` → `set` du U-A/AA.
- FX : IFX1–12 = index SysEx 0–11, MFX1–2 = 12–13, TFX1–2 = 14–15 (`sxformat 240 66 48 104 67 6|23 idx …`).
  IFX6–12 et TFX2 ajoutés sur le modèle d'IFX1.
- **Bug corrigé** : les `gate 2` des FX et de Drum Track avaient leurs entrées inversées (le bouton allait sur l'entrée
  de contrôle, le mode sur l'entrée de données) : les FX n'envoyaient pas la bonne valeur. Désormais mode → gauche,
  bouton → droite.
- Retirés : boutons gris 1–8, logos (fpic), `udpsend` (patch externe), fichiers embarqués inutiles.
- Sources : KRONOS_MIDIimp.zip (C:\Korg\Manuals Kronos 3.2.x), fonction 43 = Parameter Change
  `F0 42 30 68 43 TYP SOC SUB PID IDX vH vM vL F7`.
- FX : Switch = TYP 6 (Program) / 23 (Combi), SOC 0–15 ; marqué « → bypass, Invert Value » → `!- 1` avant le gate.
- 8 encodeurs du bas : MIXER / PAN s'excluent (`== 0`, `prepend set`) ; PAN → `+ 1` → gate 2 « fonction »
  (`loadmess 1` = volume) → gate 2 « mode » (obj-613/614) →
  Program volume : OSC1 Patch Level (TYP 9 HD-1 / 11 EXi, SOC 3, PID 6), OSC2 (10 / 12), Drum Track Volume (0 0 0 39),
  Master Volume (7 0 0 12) sur les encodeurs 1, 2, 3, 8 ; Program pan : OSC1/OSC2 Panpot (PID 3) ;
  Combi : Timbre Volume (TYP 4, SOC = timbre 0–7, PID 2) ou Timbre Pan (PID 1).
- MUTE : Drum Track Mute (Program, TYP 0, PID 40). Le KRONOS n'a pas de « solo » de Drum Track.

## Tests
- v3.2.3 : testée par l'auteur sur le KRONOS : fonctionne.
- OS3.2.3 (rack) : **fonctionnelle** — testée dans Live 12 avec le KRONOS le 16 oct. (15 h 30–15 h 45) : PROG/COMBI, banques I-A,
  I-B, U-A (noms corrects), IFX1 On / IFX2 Off (valeur inversée confirmée), MIXER Combi (timbre 1 → 0, timbre 2 ≈ moitié),
  PAN Combi (timbre 3 → R127), MIXER Program (OSC1, Drum Track), MUTE Drum Track.
  Non vérifiés : KARMA, GE, X-Y, encodeurs CC (déjà testés en v3.2.3 pour Filter Freq).

## Reste à faire
1. Tester KARMA (après Reset Controller MIDI Assign › CC Default), GE, X-Y, et un Program EXi pour MIXER.
3. Détails visuels : voyants MODULE (objets `led`) encadrés de blanc ; numéro de programme « 0 » et non « 000 ».
4. 384 GE supplémentaires (3200–3583) absents du menu GE.
5. Idée : afficher les noms du PCG de l'utilisateur (pcgtoolkit sait les lire).

## À régler sur le KRONOS (rappel)
- CC KARMA « Off » d'usine : GLOBAL › Reset Controller MIDI Assign › To: CC Default, puis Write Global Setting.
- Bank Map KORG, Enable Exclusive, canal global 1. Le moteur audio de Live doit tourner.
