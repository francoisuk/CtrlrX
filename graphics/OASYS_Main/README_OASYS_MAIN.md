# OASYS OMNI — panneau principal : ce qu'il faut savoir pour le relier à un OASYS

*28 oct. 2026. Complète `..\LISEZMOI.md` (dessin, fichiers, `_layout.json`), qui reste la référence du panneau.*

Sources : `ctrlr-project\reference\ref-oasys` (MIDI Implementation de Korg, travaux pcglib) et le
*Parameter Guide* de l'OASYS v1.3 (`kronos-pcglib\docs\oasys`).

## 1. Pas de SysEx de paramètres publié

La MIDI Implementation de l'OASYS (4 pages) ne donne que les messages de canal, les CC et les messages universels ;
pour le SysEx, Korg renvoie à son revendeur. Le panneau OASYS ne peut donc pas reprendre tel quel le SysEx du KRONOS
(famille 0x68). Ce qui est connu :

- **identification** : réponse à la demande d'identité `F0 7E 0g 06 02 42 70 00 mm 00 vv ww xx 00 F7` —
  **70 = série OASYS** (KRONOS : 68), `mm` = 06 (76 touches) ou 0F (88 touches), `vv ww xx` = version du système ;
- **messages universels** : Master Volume `F0 7F 0g 04 01 vv mm F7`, Balance (04 02), Fine Tune (04 03),
  Coarse Tune (04 04) ;
- **adresses SysEx des paramètres** : retrouvées par pcglib dans une configuration MIDI Quest
  (`ref-oasys\docs\OASYS_SQZ_ANALYSIS.md`, trame `F0 42 68 73 <adr_h> <adr_l> 00 <slot> <page> F7`), mais le lien
  adresse ↔ nom de paramètre reste à établir (point ouvert n° 1 de `OASYS_PANEL_NOTES.md`).

Conséquence : les champs `midi` du `OASYS_OMNI_layout.json` peuvent dès maintenant recevoir les **CC** ci-dessous ;
le SysEx viendra quand la table des adresses sera reliée aux noms.

## 2. Commandes du panneau pilotables par CC (MIDI Implementation, canal global)

| Commande du layout (`id`) | Message OASYS |
|---|---|
| `karma_sliders_1` … `_8` | CC 22 … 29 (KARMA Slider 1-8) |
| `karma_switches_1` … `_8` | CC 102 … 109 (KARMA SW 1-8) |
| `karma_on_off` | CC 14 (KARMA On/Off) |
| `karma_latch` | CC 31 (KARMA Latch) |
| `scenes_1` … `_8` | CC 30 (KARMA Scene ; codage des 8 scènes à vérifier) |
| `xy` (pavé X-Y = joystick vectoriel) | CC 118 (X), CC 119 (Y) |
| `fx_switches_ifx1` … `ifx12` | CC 92 = tous les IFX Off/On (pas de CC par IFX) |
| `fx_switches_mfx1`, `mfx2` | CC 94 = MFX 1/2 Off/On |
| `fx_switches_tfx1`, `tfx2` | CC 95 = TFX 1/2 Off/On |
| `program_up` / `program_down`, `bank_select_*` | Bank Select CC 0 / CC 32 + Program Change (tableau du § 3) |
| encodeurs de « temps réel » (1 à 8, selon l'affectation choisie) | Knob 1 = CC 74 (Cutoff), 2 = CC 71 (Resonance), 3 = CC 79 (Filter EG Int.), 4 = CC 72 (Release), 5-8 = CC 17, 19, 20, 21 (Knob Mod 5-8) |

Autres CC utiles : 1 / 2 (joystick ±Y), 16 (ruban), 18 (Value Slider), 80 / 81 (SW1 / SW2), 110-117 (pads 1-8).

## 3. Banques (Bank Map KORG)

| CC 0, CC 32 | Programme | Combinaison |
|---|---|---|
| 00, 00 … 00, 05 | INT-A … INT-F | INT-A … INT-F |
| 00, 06 | — | INT-G |
| 00, 08 … 00, 0E | USER-A … USER-G | USER-A … USER-G |
| 79, 00 / 79, 01-09 / 78, 00 | G (GM) / g(1)-g(9) / g(d) | — |

**L'OASYS n'a pas les banques U-AA … U-GG du KRONOS.**

## 4. Écarts entre le panneau et l'OASYS (à trancher)

Le panneau OASYS OMNI reprend toutes les commandes du KRONOS KONTROL. Trois ne correspondent à rien sur l'OASYS :

- **DRUM TRACK** (`drum_track_on_off`, `drum_track_mute`) : l'OASYS n'a pas de Drum Track. À retirer, ou à réaffecter
  (par exemple au PAD MODE des pads) ;
- **bouton U-A/AA** (`bank_select_u_a_aa`) : pas de banques U-AA … U-GG ;
- **pads** : l'OASYS a 8 pads (notes et vélocités par programme, CC 110-117, PAD MODE) qui n'ont pas de commande sur
  le panneau ; leurs réglages sont dans l'éditeur (KARMA Common, Chord Pad 1-8).

Rien n'a été modifié dans les images ni dans le `_layout.json` : ces points sont des décisions de conception.
