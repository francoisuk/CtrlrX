# Le format PCG du KRONOS : tout ce qu'il faut pour lire et fabriquer des banques

*Le grand livre du KRONOS : dossier de travail `04_Outils\PCG\data`. Version du 6 octobre 2026, 14 h 30.*

Ce document rassemble ce qui a été établi pour lire, comprendre et **écrire** des fichiers PCG du KRONOS. Chaque affirmation marquée ✅ a été **vérifiée sur les fichiers d'usine** (voir § 10). Celles marquées ⚠️ sont des hypothèses ou des points encore ouverts.

---

## 0. Contenu du dossier `data`

| Dossier | Contenu |
|---|---|
| `00_RECAPITULATIF_FORMAT_PCG.md` | ce document |
| `01_MIDI_implementation_Korg\` | la documentation SysEx officielle de Korg (contenu de `KRONOS_MIDIimp.zip`, version 1.27 d'octobre 2016) : tables octet par octet des programmes, des combinaisons, des effets, des kits, des Set Lists et du Global, plus le PDF de l'implémentation MIDI |
| `02_Tables_parametres\` | ces tables converties en CSV (ouvrables dans Excel, séparateur « ; ») et en JSON : `Programme_EXi_commun`, `Programme_HD-1`, `Moteur_<moteur>` (×8), `Combinaison`, `Effets_liste`, `Effets.json` |
| `03_Scripts\` | les scripts Python (§ 9) |
| `04_Analyses_usine\` | résultats sur les fichiers d'usine : arborescence et DIV1 de chaque PCG (`Structure_fichiers_usine.md`), inventaires des programmes et des combinaisons, blocs d'effets par défaut (`Effets_blocs_par_defaut.json`) |
| `05_Voice_Name_Lists\` | texte extrait des Voice Name Lists (EFGSJ2 = mai 2011, EFGSJ3 = oct. 2014 / OS 3.0, EFGSJ4 = fév. 2015, M2 = KRONOS 3, déc. 2025), avec la liste des multi-échantillons ROM. Les PDF sont dans `04_Outils\PCG\` |

Les fichiers d'usine analysés sont dans `04_Outils\PCG\FACTORY*` :

| Dossier | Fichier | OS (octet 7) | Ce que c'est |
|---|---|---|---|
| `FACTORY` | `PRELOAD.PCG` (avril 2011) | 0 = OS 1 | sons d'usine du premier KRONOS |
| `FACTORY` | `INIT.PCG` (2014) | 0 | banques remplies de « Init Program » (HD-1), « Init EXi Program » (AL-1), « Init Combi » ; objets au format OS 1 |
| `FACTORY_V2` | `PRELOAD_V2.PCG` (2013) | 1 = OS 2 | sons d'usine OS 2 |
| `FACTORY_V3.1` | `PRELOAD.PCG` = `PRELOAD_V3.PCG` (2016) | 2 = OS 3 | sons d'usine **OS 3.0/3.1** (KRONOS 2) ; banques jusqu'à U-BB |
| `FACTORY_V3.1` | `PRELOAD_KRONOSX.PCG` | 2 | même contenu, rangé pour un KRONOS X |
| `FACTORY_V3.1\EXs_Extras` | `EXs2/EXs3/EXs4 … .PCG` | 2 | **PCG d'une seule banque écrits par Korg** : la référence pour un PCG partiel |
| `FACTORY_V3.2\FACTORY` | `PRELOAD.PCG` (déc. 2025) | 2 | sons d'usine **OS 3.2 / KRONOS 3** : 17 banques de programmes (U-CC, U-DD, U-EE en plus), 6 de combinaisons |
| `FACTORY_V3.2\Extra Sound Data` | `KRS-06*.PCG` (2024) | 1 | autre PCG d'une banque écrit par Korg (EXi, U-G), avec un bloc `DPI1` en plus |

✅ **L'OS 3.2 n'a pas changé le format** : mêmes blocs, mêmes versions d'objets (programmes v5, combinaisons v3, kits v3, séquences d'ondes v1, Global v2). Les nouveautés sont des **valeurs** : modèle EP-1 n° 6 (Tine EP I Early), types de pianos SGX-2 72 à 79, effets jusqu'au n° 197.

---

## 1. Vue d'ensemble

Un PCG est une **arborescence de blocs** (*chunks*), comme des dossiers :

```
en-tête (16 octets)
PCG1                       le fichier entier
├── DIV1                   quelles banques sont présentes (§ 3)
├── INI1 / INI2 / INI3     (OS 1 seulement)
├── SLS1                   Set Lists
│   ├── SLD1                 données communes
│   └── STL1                 les 128 Set Lists
├── PRG1                   programmes
│   ├── MBK1 …               banque de programmes EXi
│   └── PBK1 …               banque de programmes HD-1
├── CMB1                   combinaisons
│   └── CBK1 …
├── DKT1                   kits de batterie       └── DBK1 …
├── WSQ1                   séquences d'ondes      └── WBK1 …
└── GLB1                   réglages Global
```

`INIT.PCG` contient en plus `PRG2`, `CMB2`, `DKT2`, `WSQ2`, `STL2` (⚠️ rôle non établi ; absents des PRELOAD OS 2 et OS 3, donc inutiles pour écrire).

Un PCG **partiel** (Save PCG avec quelques banques cochées) ne contient que les blocs concernés : c'est le cas des fichiers du livre.

---

## 2. En-tête et blocs ✅

**En-tête, 16 octets :**

| Octets | Valeur | Sens |
|---|---|---|
| 0-3 | `KORG` | signature |
| 4 | `68` | famille KRONOS (même code que la réponse *Device Inquiry*) |
| 5 | `00` | |
| 6 | `02` | type de fichier : PCG |
| 7 | `00` / `01` / `02` | version d'OS qui a écrit le fichier : OS 1 / OS 2 / OS 3.x |
| 8 | `01` | |
| 9-15 | `00` | |

**Bloc :** `id` (4 caractères) | `taille` (u32 gros-boutiste, corps seul, sans ces 12 octets) | `champ` (u32) | `corps`.

**Le champ de 4 octets :**
- conteneurs (`PCG1`, `PRG1`, `CMB1`, `DKT1`, `WSQ1`, `SLS1`, `SLD1`, `STL1`) : `version << 16 | 0x0400` ;
- banques (`MBK1`, `PBK1`, `CBK1`, `DBK1`, `WBK1`) et `GLB1` : `version << 16 | somme8` ;
- **`somme8` = somme de tous les octets du corps du bloc (catalogue de 12 octets compris), modulo 256.** ✅ Vérifié : les cinq fichiers d'usine sont reconstruits **à l'octet près** en recalculant toutes les sommes.

**Catalogue d'une banque** (12 premiers octets du corps) : `n` (nombre d'éléments) | `taille d'un élément` | `numéro de banque`, trois u32 gros-boutistes. Puis `n` éléments de taille fixe.

**Versions des objets (2 octets hauts du champ) :**

| Bloc | OS 1 | OS 2 | OS 3.0/3.1 |
|---|---|---|---|
| MBK1 (programmes EXi) | 3 | 5 | 5 |
| PBK1 (programmes HD-1) | 4 | 5 | 5 |
| CBK1 (combinaisons) | 3 | 3 | 3 |
| DBK1 (kits) | 2 (22 040 o) | 3 (38 424 o) | 3 |
| WBK1 (séquences d'ondes) | 0 (1 192 o) | 1 (2 216 o) | 1 |
| GLB1 | 1 | 1 | 2 |

La documentation MIDI de Korg décrit les objets « Object Version 5 » (programmes) et « 3 » (combinaisons) : **c'est le format à écrire**, valable de l'OS 2 à l'OS 3.1.4 (et, ⚠️ selon le livre et Korg, lu aussi par l'OS 3.2).

---

## 3. DIV1 : le sommaire des banques ✅ (partiellement)

Corps de 44 octets, u16 gros-boutistes :

```
00000000
[masque bas, nb] [masque haut, nb]   programmes     (nb = 0x15)
[masque bas, nb] [masque haut, nb]   combinaisons   (nb = 0x0E)
[masque bas, nb] [masque haut, nb]   kits           (nb = 0x0F)
[masque bas, nb] [masque haut, nb]   séq. d'ondes   (nb = 0x0F)
[masque, nb]                         Set Lists      (OS 3 : 0001 0001)
[ffff, 0000]                          ⚠️ sens inconnu (OS 2 : 0001 0000)
```

- Le **masque** a un bit par banque présente, dans l'ordre d'index du § 4 (bit 0 = I-A…). Exemple ✅ : PRELOAD OS 3 = `6fff` → I-A à I-F, U-A à U-F, U-AA, U-BB (pas U-G).
- Pour les combinaisons : `000f` = I-A à I-D.
- Champ du bloc DIV1 : `00010000` (OS 2 et 3).
- ✅ La fonction `kpcg.div1()` régénère exactement les masques programmes et combinaisons du PRELOAD OS 3.
- ✅ Pour un PCG sans Set Lists, Korg écrit `0000 0000` (PCG EXs) : c'est ce que fait `kpcg.div1()`. Le fichier du livre a **le même en-tête, le même DIV1 et le même catalogue** que `EXs2 Concert Grand.PCG` de Korg.

---

## 4. Numéros de banque : trois numérotations

| Banque | Numéro dans le fichier (catalogue) | Index DIV1 | « Bank Number » dans un timbre de combinaison | MIDI MSB/LSB |
|---|---|---|---|---|
| I-A … I-E | 0 … 4 | 0 … 4 | 0 … 4 | 0 / 0 … 4 |
| I-F | 0x8000 | 5 | 5 | 0 / 5 |
| GM, g(1)…g(9), g(d) | (absentes du fichier) | — | 6 … 16 | 121/… |
| U-A … U-G | 0x20000 … 0x20006 | 6 … 12 | 17 … 23 | 0 / 8 … 14 |
| U-AA … U-GG | 0x20007 … 0x2000D | 13 … 19 | 24 … 30 | 0 / 16 … 22 (⚠️ voir le livre, V.4) |

Combinaisons : I-A … I-G = 0 … 6 ; U-A … U-G = 0x20000 … 0x20006 (index DIV1 7 … 13).

**Type de banque :** une banque de programmes est soit EXi (`MBK1`), soit HD-1 (`PBK1`). Le type est fixé par banque (Global › Set Program Bank Type). En chargeant, la banque de destination (**To**) doit être du même type. Les deux blocs ont la même taille d'élément : **4 960 octets**.

---

## 5. Le programme (4 960 octets) ✅

### 5.1 Règles de codage

- Les champs sont **empaquetés au bit près**. Un champ peut déborder sur l'octet suivant : les bits sont pris **poids faible d'abord** (le morceau du premier octet forme les bits bas de la valeur). ✅
- Les valeurs sur 16 bits (`FF39~00C7`, tempo `0FA0~7530`…) sont **petit-boutistes** (octet bas d'abord). ✅
- Les valeurs négatives sont en **complément à deux sur la largeur du champ** (ex. −99 sur 8 bits = `9D`).
- Les valeurs sont **brutes** : « 5.0 » peut être stocké 50, un tempo de 120.00 est stocké 12000.
- **Validation** : sur les 1 792 programmes du PRELOAD OS 3, en lisant chaque paramètre selon ces règles, **aucune valeur n'est hors des limites documentées** dans les blocs moteurs, et 52 seulement dans les parties communes (types d'effets ajoutés après 2015 et quelques « Start Seed » KARMA). ✅

### 5.2 Carte d'un programme EXi (`Programme_EXi_commun.csv`)

| Octets | Contenu |
|---|---|
| 0-23 | nom (latin-1, complété par des 00) |
| 24-87 | paramètres de l'IFX 1 (64 octets, mise en page selon le type d'effet, `Effets.json`) |
| 88-96 | IFX 1 : type (88) ; octet 89 : canal (bits 0-5), interrupteur (bit 6, stocké comme « bypass » : valeur inversée), chaîne (bit 7) ; puis Chain To, pan, bus, Send 1/2, Rec Bus |
| 24 + 74×(n−1) / 88 + 74×(n−1) | IFX n (n = 1 à 12) : paramètres / type |
| 912-975, 976 | MFX 1 : paramètres, type |
| 980-1043, 1044 | MFX 2 |
| 1048-1051 | réglages MFX communs |
| 1052-1115, 1116 | TFX 1 |
| 1120-1183, 1184 | TFX 2 |
| 1190-1205 | LFO communs des effets |
| 1206-1251 | Vector Control |
| 1252-1291 | contrôleurs, entrées audio |
| 1292-1302 | Drum Track (commun) |
| 1304-2474 | KARMA (commun et modules) |
| 2558-2579 | **Common** : Assign Mode Poly/Mono, Key Priority, Legato, **Unison** (voix, Detune, Thickness), bus, **Category** (2568), **Scale Type/Key/Random** (2569-2571) |
| 2572-2577 | contrôleurs assignables |
| 2580-2585 | Track EQ |
| 2586-2683 | **Tone Adjust** |
| 2684-2687 | EXi 1 / EXi 2 Common |
| 2688-2689 | Drum Track Program : numéro, banque (code du § 4) |
| 2718-2733 | Common LFO |
| 2734-2747 | Common Keyboard Track 1 et 2 |
| 2748-2852 | Common Step Sequencer |
| **2857** | **EXi 1 : moteur** (0 Off, 2 AL-1, 3 CX-3, 4 STR-1, 5 MS-20EX, 6 PolysixEX, 7 MOD-7, 8 SGX-2, 9 EP-1) |
| 2860-2907 | EXi 1 : sortie, AMS Mixers 1-2 |
| **2908-3908** | **EXi 1 : bloc du moteur** (table `Moteur_<moteur>`, offset + 2908) |
| **3909** | **EXi 2 : moteur** |
| 3912-3959 | EXi 2 : sortie, AMS Mixers |
| **3960-4959** | **EXi 2 : bloc du moteur** (offset + 3960) |

Les huit moteurs EXi (nombre de paramètres) : AL-1 609, CX-3 151, STR-1 707, MS-20EX 512, PolysixEX 322, MOD-7 1 108, SGX-2 23, EP-1 183.

### 5.3 Le programme HD-1

- 3 706 octets utiles (table `Programme_HD-1`), rangés dans une case de 4 960 : les 1 254 derniers octets ne sont pas lus (⚠️ ils contiennent parfois des restes ; on les recopie tels quels).
- Effets et parties communes aux mêmes offsets que l'EXi jusqu'à 2 857 environ ; ensuite oscillateurs 1 et 2, filtres, EG, LFO, AMS Mixers propres au HD-1.

### 5.4 Ce qui a changé d'un OS à l'autre ✅

- **OS 1 → OS 2** (objets v3/v4 → v5) : les programmes AL-1, MS-20EX, PolysixEX et EP-1 sont **identiques octet pour octet** ; MOD-7, STR-1, SGX et CX-3 ont changé dans leur bloc moteur ; tous les programmes HD-1 ont changé (vers 2 775-3 620). Un fichier OS 1 est converti au chargement par le KRONOS, mais **on ne peut pas recopier un objet OS 1 dans un fichier OS 2/3**, sauf pour l'AL-1, le MS-20EX, le PolysixEX et l'EP-1.
- **OS 2 → OS 3** : même format v5. Seuls changent les octets 2688-2689 (Drum Track Program), parce que l'OS 3 a déplacé les programmes de batterie d'usine de I-F vers U-BB.
- **OS 3.1 → OS 3.2** (⚠️ à vérifier avec le PRELOAD du KRONOS 3) : nouveaux modèles EP-1, nouveaux types de pianos SGX-2, nouvelles banques EXs. D'après Korg et le livre, le format ne change pas et un PCG du KRONOS 3 se charge sur un KRONOS en OS 3.1.4, qui remplace Tine EP I Early par Reed EP 200A.

---

## 6. Les effets ✅

- 198 types (0 = No Effect … 197 = Rotary Speaker Pro CX Custom), dont la mise en page de chaque bloc de 64 octets est dans `Effets.json` (même codage au bit près).
- Validation : 16 922 paramètres d'IFX 1, 15 143 de MFX 1, etc., lus sans une seule valeur hors limites dans le PRELOAD OS 3.
- **Changer de type d'effet ne remet pas ses paramètres à zéro dans le fichier** : il faut écrire un bloc complet. `Effets_blocs_par_defaut.json` donne, pour 135 types, le bloc le plus fréquent dans les sons d'usine OS 2/3 (et le son d'où il vient). Pour les 63 autres, partir d'un réglage écrit à la main d'après `Effets.json`.

---

## 7. La combinaison (7 810 octets) ✅

- 0-23 : nom ; effets, KARMA, contrôleurs comme pour un programme ;
- 16 timbres de 188 octets à partir de l'octet **4 802** (timbre n : 4 802 + 188 × (n−1)) :
  - +0 : numéro de programme (0-127) ;
  - +1 : banque (code « Bank Number » du § 4) ;
  - +2 : canal MIDI (bits 0-4, 16 = Global) et statut (bits 5-7 : 0 Off, 1 ⚠️, 2 Int, 3 ⚠️, 4 Ext2 ; Korg : « Off~External2 ») ;
  - +5 Volume, +6 Bend Range, +7 Transpose, +14 Pan, +15/16 Send 1/2, +37/38 Key Window Top/Bottom, +40/41 Velocity Window High/Low… (table `Combinaison.csv`).
- Validation sur les 512 combinaisons du PRELOAD OS 3 : 14 valeurs hors limites (Start Seed KARMA).
- **Au chargement avec .PCG Contents → To**, le KRONOS corrige les références des combinaisons vers la banque de destination des programmes, à condition que les programmes et les combinaisons soient chargés ensemble (Quick Start, « Correction automatique de renvois »).

---

## 7 bis. Listes de valeurs utiles (énumérations) ✅

Les tables de Korg ne donnent que la première et la dernière valeur d'une liste. Ordres établis (Parameter Guide EN3, définitions d'instrument de MIDI Quest, et contrôle sur les sons d'usine) ; ils sont dans `03_Scripts\fabrication\ams_lists.json` et `livre_lib.py` :

| Liste | Ordre (valeur stockée) |
|---|---|
| Sources AMS de l'AL-1 (53) | 0 Off, 1-2 AMS Mixer 1-2, 3 Step Seq, 4 Common Step Seq, 5 EG1, 6 EG2, 7 EG3, 8 EG4, 9 Amp EG, 10-13 LFO1-4, 14 Common LFO, 15 Filter KT, 16 Amp KT, 17-18 Common KT 1-2, 19 Note Number, 20 Velocity, 21 Exp. Velocity, 22 Poly AT, 23 After Touch, 24 JS X, 25 JS+Y, 26 JS-Y, 27-28 JS±Y & AT/2, 29 Foot Pedal, 30 Ribbon, 31 Value Slider, 32-35 Knob Mod.5-8, 36-39 Knob Mod [+], 40 Damper, 41 Porta SW, 42 Sostenuto, 43 Soft, 44 SW1 Mod., 45 SW2 Mod., 46 Foot Switch, 47 CC#83, 48-51 VJS ±X ±Y, 52 Tempo |
| Sources AMS des autres moteurs | même « queue » (Note Number … Tempo), précédée des sources propres au moteur (PolysixEX 16, MS-20EX 19, STR-1 26, MOD-7 30, CX-3 7, EP-1 8 dont Release Velocity, HD-1 15) |
| Sources Dmod des effets (38) | 0 Off, 1 Gate1, 2 Gate1+Damper, 3 Gate2, 4 Gate2+Damper, 5 Note Number, 6 Velocity, 7 Exp. Vel., 8 After Touch, 9 JS X, 10 JS+Y, 11 JS-Y, 12 Foot Pedal, 13-14 FX Control 1-2, 15 Ribbon, 16 Value Slider, 17-24 Knobs, 25 Damper, 26 Porta, 27 Sostenuto, 28 Soft, 29 SW1, 30 SW2, 31 Foot Switch, 32 CC#83, 33-36 VJS, 37 Tempo |
| Source audio d'un EXi (Input Source Bus) | 0 Off, 1 Audio In 1/2, 2 USB, 3 S/P DIF, 4 L/R, 5-8 Indiv 1/2…7/8, 9-10 REC, **11 FX Control 1**, 12 FX Control 2, **13-24 IFX 1-12**, 25-26 MFX, 27-28 TFX (vérifié sur « Dist.Feedback Guitar VJS ») |
| Bus Select (programme, timbre, IFX) | 0 L/R, 1-12 IFX 1-12, 13-20 sorties 1-8, 21-24 paires, **25 Off** |
| Statut d'un timbre de combinaison | 0 Off, **1 INT**, 2 EXT… (448 timbres d'usine sur 512 en 1 / canal 16 = Gch) |
| Catégories (par défaut) | 0 Keyboard, 1 Organ, 2 Bell/Mallet, 3 Strings, 4 Vocal/Airy, 5 Brass, 6 Woodwind/Reed, 7 Guitar/Plucked, 8 Bass, 9 Slow Synth, 10 Fast Synth, 11 Lead Synth, 12 Motion Synth, 13 SE, 14 Hit/Arp, 15 Drums, 16 Orchestral, 17 User |
| Gammes (Scale Type) | 0 Equal, 1 Pure Major, 2 Pure Minor, 3 Arabic, 4 Pythagoras, 5 Werkmeister, 6 Kirnberger, 7 Slendro, 8 Pelog, 9 Stretch, 10 User All Notes, 11-26 User Octave 00-15 |
| EP-1 Model Type | 0 Tine EP I Late (« Tine EP I » en OS 3.1), 1 Tine EP II, 2 Tine EP V, 3 Tine EP DMP, 4 Reed EP 200, 5 Reed EP 200A, **6 Tine EP I Early (OS 3.2.1+)** ; le Parameter Guide les affiche dans un autre ordre |
| EP-1 pédale (IFX Type) | 0 Off, 1 Small Phase, 2 Orange Phase, 3 Black Phase, 4 Vintage Chorus, 5 Black Chorus, 6 EP Chorus, 7 Vintage Flanger, 8 Red Comp, 9 VOX Wah |
| MS-20EX : sorties du Patch Panel (28) | 0 aucune, 1-2 VCO 1-2, 3 HPF, 4 LPF, 5 Signal, 6 Phones, 7 MG Saw/Tri, 8 MG Square, 9 EG1, 10 EG1 Rev, 11 EG2, 12 S&H, 13 VCA, 14 White Noise, 15 Pink Noise, 16 KBD CV, 17 KBD Trig, 18 Wheel, 19 Momentary SW, 20-21 Mixer 1-2, 22-26 ESP…, 27 ESP EXi Audio In |
| MOD-7 | l'algorithme est un numéro (connexions « normalisées » ; 0 = Blank Patch, aucune ; la fin de la liste, jusqu'à 78, porte les 32 algorithmes DX) ; les `Input Jack` sont des câbles en plus (0 = aucun). ✅ **Valeur d'une prise = source branchée** (relevé sur les ~200 sons MOD-7 d'usine OS 3.1 et 3.2, aucune contradiction pour les oscillateurs) : 0 aucune, 1 PCM OSC, 2 bruit, 3 (Audio In, jamais employé), 4-9 OSC1-6, 10-12 Mixer1-3, 13 Filtre A, 14 Filtre B ; l'entrée 2 d'OSC5 s'appelle « OSC5 B ». Mode d'oscillateur : 0 Off, 1 Sine, 2 Saw, 3 Triangle, 4 Square, 5 Sine+WS, 6 WS, 7 Ring Mod Only ; ✅ relevé sur les sons d'usine : en mode 6 (WS) l'oscillateur tord le signal de ses entrées (« VJS Reed E.Piano » OSC1 ← OSC2 + OSC3, « Rated (P)PG for "Bell" » OSC2 ← OSC1), en mode 7 il multiplie ses deux entrées (« Zombie Choir » OSC1 = PCM × OSC2, « Syn Sitar & Tambura » OSC6 = OSC5 × PCM), Ring Mod. Crossfade 64-100. Ratio < 1 : Coarse 0 + Fine +0,500 ou Coarse 1 + Fine −0,500 (Fine −0,999 à +0,999 ; les deux écritures dans les sons d'usine) ; Coarse 0 + Fine 0 = fréquence fixe (Frequency Offset en Hz). Tone Adjust (2586-2683) : le même dans 128 des 134 sons d'usine OS 3.1 dont l'EXi 1 est un MOD-7 (repris de « Candlelight Pad » par `engine_template`). Mélodie du Step Sequencer : intensité de hauteur 25 demi-tons (brut 128), 4 unités par demi-ton, comme les sons d'usine |
| STR-1 Pluck Table | 0 Ac Guitar 1, 1 Ac Guitar 2, 2 Dark E.Gtr, 3 Bright E.Gtr, 4 Resonant E.Gtr, 5-7 Jazz, 8 Square Pluck, 9 Midrange Pluck, 10 Smooth Pulse, 11 Resonant Pulse, 12-14 Clav, 15 Harpsichord |

**Échelles non linéaires** (`livre_lib.py`) :
- intensité de hauteur ±48.00 sur ±151 : 0,01 jusqu'à 0,50 ; 0,05 jusqu'à 1,00 ; 0,20 jusqu'à 12,00 ; puis 1 demi-ton ;
- fréquence des LFO de voix 0-99 : table du Parameter Guide (0 = 0,014 Hz, 50 = 2,84 Hz, 70 = 5,69 Hz, 99 = 26,25 Hz) ;
- temps du vecteur : 0-195 (0 ms … 60 s ; 55 = 1 s, 80 = 3,5 s) ;
- ratio du compresseur : 0 = 1,0:1, 10 = 2,0:1, 20 = 3,0:1… ; Base Note des effets BPM : 1/32, 1/16(3), 1/16, 1/8(3), 1/8, 1/4(3), 1/4, 1/2(3), 1/2, 1/1 (croche pointée = 1/16 × 3) ; BPM « MIDI » = 3999.
- Le « Delay Start » d'un oscillateur à 97 = **KeyOff** (vérifié sur « 8' Harpsichord + Key Off »).
- Les AMS Mixers des EXi sont dans la partie commune (2868 et 2888 pour l'EXi 1) ; leurs sources (octets +1, +3, +15) sont marquées « fixed » dans la table de Korg mais sont bien stockées là.

---

## 8. Recette pour fabriquer un PCG

1. **Partir d'une vraie fiche** v5 (programme d'usine OS 3 du même moteur, ou « page blanche » préparée), jamais d'une fiche à zéro : des centaines de paramètres ont une valeur par défaut non nulle.
2. **Neutraliser** ce qui ne fait pas partie de la recette : sources AMS sur Off et intensités à 0, effets sur No Effect (ou bloc par défaut du type voulu), KARMA et Drum Track coupés, Tone Adjust vidé.
3. **Écrire** les valeurs de la recette par nom de paramètre (`kprog.Program.set` / `mset`), en valeurs brutes.
4. **Contrôler** chaque valeur écrite contre les limites des tables (`analyse_usine.in_range`).
5. **Assembler** : en-tête OS 3 (`kpcg.HEADER_OS3`), `PCG1` [`DIV1`, `PRG1` [`MBK1`/`PBK1`], `CMB1` [`CBK1`]], banques de 128 éléments, sommes recalculées par `kpcg.build`.
6. **Relire** le fichier avec pcgreader et le relire avec `kpcg.parse` (reconstruction identique).
7. **Tester sur un KRONOS** : ouvrir le fichier en mode Disk, écouter sans charger, puis charger une banque vers une banque du même type.

---

## 9. Les scripts (`03_Scripts\`)

| Script | Rôle |
|---|---|
| `kmap.py` | lit les tables de Korg et donne, pour chaque paramètre, sa position au bit près |
| `kprog.py` | lit et modifie un programme par nom de paramètre (`set`, `get` pour la partie commune, `mset`, `mget` pour le moteur d'EXi 1 ou 2) |
| `kpcg.py` | lit et écrit l'arborescence d'un PCG ; numéros de banque ; DIV1 ; sommes de contrôle |
| `pcg.py`, `pcgreader.py` | l'outil du livre (lecture, noms, inventaires) |
| `export_tables.py` | régénère `02_Tables_parametres` |
| `analyse_usine.py` | régénère `04_Analyses_usine` à partir des PCG d'usine |
| `fabrication\` | les recettes du livre et `build_livre.py`, qui fabrique les deux PCG du livre (voir son LISEZMOI) |

Python 3.8 ou plus, sans bibliothèque externe.

---

## 10. Vérifications faites

| Vérification | Résultat |
|---|---|
| Reconstruction des 5 PCG d'usine (sommes recalculées) | identique à l'octet près |
| Paramètres des moteurs EXi du PRELOAD OS 3 (≈ 516 000 lectures) | 0 hors limites |
| Parties communes (programmes EXi et HD-1) | 68 hors limites, tous expliqués (effets post-2015, Start Seed) |
| Blocs d'effets (IFX, MFX, TFX) | 0 hors limites |
| Combinaisons | 14 hors limites (Start Seed) |
| DIV1 régénéré (programmes, combinaisons) | identique au PRELOAD OS 3 |

## 11. Points ouverts

- ⚠️ **Premier chargement réel** d'un PCG fabriqué : c'est le seul test qui fait foi (structure identique aux PCG EXs de Korg, donc confiance élevée).
- ⚠️ Derniers mots de DIV1 (`ffff 0000`), blocs `*2` d'INIT.PCG, bloc `DPI1` des PCG KRS-06 : rôle non établi, inutiles pour écrire.
- ⚠️ Ordre « Up/Down » de l'arpégiateur PolysixEX : la table de Korg (0 Up … 2 Up/Down) et l'affichage du Parameter Guide (UP/DOWN, DOWN, UP) diffèrent ; la table fait foi pour le stockage.

## 12. Références

- Korg, *KRONOS MIDI Implementation* et tables SysEx (`KRONOS_MIDIimp.zip`, v1.27, 2016).
- Korg, *KRONOS Voice Name List* EFGSJ2 (2011), EFGSJ4 (2015), *KRONOS 3 Voice Name List* M2 (2025).
- Korg, *KRONOS Operation Guide* / *Quick Start* : Save PCG, Load, .PCG Contents, To, correction des références.
- Sound Quest, définitions d'instrument MIDI Quest (fichiers .sqz de l'auteur) : ordre de certaines listes de valeurs, relevé pour usage personnel.
- Michel Keijzers, *PCG Tools* (logiciel libre, LGPL v3), bibliothécaire de référence pour les PCG Korg : https://pcgtools.mkspace.nl
- *Le grand livre du KRONOS*, VI.3 « Les fichiers PCG décodés ».
