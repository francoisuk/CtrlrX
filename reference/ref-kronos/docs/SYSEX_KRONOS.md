# Messages MIDI / SysEx du KRONOS utilisés par Kronos Kontrol

Source des identifiants : MIDI Implementation officiel (`KRONOS_MIDIimp.zip`, dossier `C:\Korg\Manuals Kronos 3.2.x`).
État : **T** = testé sur le KRONOS (OS 3.2.3, Live 12, 16 oct. 2026, ou v3.2.3 le 12 oct.) ; **D** = d'après la doc, non testé.
Notation des octets : hexadécimal ; `g` = canal global − 1 (canal 1 → `30`).

## Formats

| Fonction | Message | Remarque |
|---|---|---|
| 43 Parameter Change | `F0 42 3g 68 43 TYP SOC SUB PID IDX vH vM vL F7` | valeur 21 bits, complément à 2 : `vH = (v>>14)&7F`, `vM = (v>>7)&7F`, `vL = v&7F` |
| 4E Mode Change | `F0 42 3g 68 4E mm F7` | mm : 0 Combination, 2 Program, 4 Sequencer, 6 Sampling, 7 Global, 8 Disk, 9 Set List |
| 12 Mode Request | `F0 42 3g 68 12 F7` | le KRONOS répond 42 Mode Data `… 42 mm oo ss dd ee F7` |
| 24 Reply | `F0 42 3g 68 24 cc F7` | cc : 0 OK, 1 type incorrect pour le mode, 2 id inconnu, 3 message tronqué, 4 objet absent, 6 valeur hors limites, 65 protégé |
| Banque + programme | `Bn 00 MSB`, `Bn 20 LSB`, `Cn pp` | Bank Map KORG, MSB avant LSB |

## Bank Map KORG (MSB.LSB)

INT-A…F `00.00`–`00.05` · INT-G (Combi) et GM (Program) `121.00` · g(1)…g(9) `121.01`–`121.09` · g(d) `120.00` ·
USER-A…G `00.08`–`00.14` · USER-AA…GG `00.15`–`00.21` (Program seulement).  **T** (I-A, I-B, I-C, U-A, GM000)

## Paramètres (TYP SOC SUB PID IDX)

| Commande | Mode | TYP | SOC | SUB | PID | IDX | Valeurs | État |
|---|---|---|---|---|---|---|---|---|
| Effet n Switch (IFX1-12 = 0-11, MFX1-2 = 12-13, TFX1-2 = 14-15) | Program | 6 | n | 0 | 0 | 0 | **inversée** : 0 = On, 1 = Off | T (IFX1, IFX2) |
| Effet n Switch | Combi | 23 | n | 0 | 0 | 0 | inversée | D |
| Timbre t Volume (t = 0-15) | Combi | 4 | t | 0 | 2 | 0 | 0-127 | T |
| Timbre t Pan | Combi | 4 | t | 0 | 1 | 0 | 0 RND, 1-127 L…R, 64 C | T |
| Timbre t Mute | Combi | 4 | t | 0 | 14 | 0 | 0/1 | D |
| Master Volume | Combi | 24 | 0 | 0 | 12 | 0 | 0-127 | D |
| OSC1 / OSC2 Patch Level (HD-1) | Program | 9 / 10 | 3 | 0 | 6 | 0 | 0-127 | T (OSC1) |
| EXi1 / EXi2 Patch Level (EXi) | Program | 11 / 12 | 3 | 0 | 6 | 0 | 0-127 | D |
| OSC / EXi Panpot | Program | 9-12 | 3 | 0 | 3 | 0 | 0 RND, 1-127 | D |
| OSC / EXi Mute | Program | 9-12 | 3 | 0 | 7 | 0 | 0/1 | D |
| Drum Track On | Program | 0 | 0 | 0 | 10 | 0 | 0/1 | T |
| Drum Track Volume | Program | 0 | 0 | 0 | 39 | 0 | 0-127 | T |
| Drum Track Mute | Program | 0 | 0 | 0 | 40 | 0 | 0/1 | T |
| Master Volume | Program | 7 | 0 | 0 | 12 | 0 | 0-127 | D |
| KARMA GE Number | Program | 1 | 0 | 0 | 0 | 0 | 0-3583 (vM = n / 128, vL = n % 128) | D |
| KARMA Module A-D GE Number | Combi | 3 | 0-3 | 0 | 0 | 0 | 0-3583 | D |

## CC utilisés (canal de la piste)

Filter Freq 74 · Reso 71 · Filter EG 79 · EG Release 72 · Knob Mod 1-4 : 17, 19, 20, 21 · LFO1 Speed 76 · LFO1 Depth 77 ·
Ribbon 16 · Port Time 5 · ENV A/D/S/R 73, 75, 70, 72 · KARMA Sliders 1-8 : 22-29 · KARMA On/Off 14 · Latch 31 · Scene 30 ·
KARMA Switches 1-8 : 102-109 · SW1/SW2 80/81 · Vector X/Y 118/119.  Filter Freq : **T** ; les autres : hérités, à tester.

## Reliquats à ne pas reprendre

Le device contient encore deux messages hérités du M3 (`F0 42 30 75 41 …`, modèle 0x75, envoyés par MODULE CTRL) :
ils ne s'adressent pas au KRONOS. Pour MODULE CTRL, chercher la fonction 6D (KARMA Parameter Change) dans
`KRONOS_MIDI_SysEx.txt` et `KARMA_GE_RTP.txt`.

## Autres fonctions utiles (doc, non utilisées)

72 Object Dump Request / 73 Object Dump (sons complets), 44 Parameter Change binaire, 41 Sequencer Parameter Change,
6D KARMA Parameter Change, 6E Drum Track Parameter Change, 71 Set Current Object, 7F KARMA Control.
Voir `KRONOS_MIDI_SysEx.txt` (liste des fonctions en tête du fichier).
