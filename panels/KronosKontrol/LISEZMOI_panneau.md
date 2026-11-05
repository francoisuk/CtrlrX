# Kronos Kontrol — panneau « rack » (maquette, puis panneau CTRLR)

*Design finalise le 16 octobre 2026, 15 h 35 (auteur : François Rossi).
Chemins mis a jour le 24 oct. 2026 apres la recolte des projets
precedents. **Le rack est maintenant implemente** : c'est le panneau
CTRLR `KronosKontrol.panel` (version complet-0.96) — voir
`PROJECT_LAYOUT.md` et `REPRISE.md`.*

Ce dossier contient la maquette du panneau du device **Kronos Kontrol**,
dessinee en façade de rack 19″ 3U (1500 × 414 px). Elle est l'interface
du device Max for Live `reference\ref-kronos\m4l\Kronos Kontrol
OS3.2.3_FR.amxd` (et `_EN`, `_ES`), et le modele repris tel quel par
le panneau Ctrlr `KronosKontrol.panel`.

## Contenu (fichiers actuels, 24 oct. 2026)

| Fichier | Rôle |
|---|---|
| `..\..\GUI_pic\panneau_rack\kronos-kontrol-rack.svg` / `.png` | La maquette (texte converti en tracés dans le SVG). |
| `..\..\GUI_pic\kronos-kontrol-rack-final.svg` / `.png` | La maquette finale, version aplatie. |
| `..\..\scripts\panneau_rack\kontrol.py` | **Script principal** : dessine le panneau (SVG) puis le PNG dans `maquettes\` (dossier a creer a cote du script). |
| `..\..\scripts\panneau_rack\rack.py` | Briques graphiques reprises du rack KRONOS : encodeurs a anneau bleu OLED, textes, curseurs. |
| `..\..\scripts\panneau_rack\k3vec.py` | Dessin vectoriel du KRONOS 3 (seule `screen_setlist` est utilisée, par `rack.py`). |
| `..\..\scripts\panneau_rack\txt2path.py` | Convertit les `<text>` en tracés (polices Inter et DejaVu Sans Mono). |
| `..\..\scripts\panneau_rack\fond_device.py` | Fond sans les parties actives → `rack_fond.png` (1500 × 414), recopie dans ce dossier pour `sources\build_panel.py`. |
| `rack_fond.png` | Le fond du panneau, integre au `KronosKontrol.panel` par le generateur. |
| `KronosKontrol.panel` | **Le panneau CTRLR implemente** (complet-0.96), commandes posees aux coordonnees de cette maquette. |

Ancien emplacement (avant la recolte du 24 oct.) : les scripts etaient
dans `sources\` du projet vst3, l'art dans `maquettes\` et
`reference\`. Les originaux restent dans
`C:\Korg\Manuals Le grand livre du KRONOS\04_Outils\produits-inclus\`.

Régénérer le dessin : `python scripts\panneau_rack\kontrol.py` (Python 3,
`pip install cairosvg fonttools pillow`). Sous Windows, cairosvg demande
la bibliothèque Cairo, et `FONT_DIR` doit désigner un dossier contenant
les fichiers Inter-*.otf et DejaVuSansMono.ttf (variable dans
`txt2path.py`). Détails : `..\..\scripts\panneau_rack\README.md`.

## Unités et grandes zones (unités du dessin : façade 1500 × 414, oreilles de rack 0–46 et 1454–1500)

| Zone | x | Contenu |
|---|---|---|
| Gauche | 46–468 | 16 encodeurs en 2 groupes de 8 (colonnes x = 115, 205, 295, 385), chacun avec une bande OLED bleue de noms. |
| Centre | 468–948 | PROGRAM, U-A/AA, BANK SELECT, logo, FX SWITCHES, pavé X-Y, TRACK SELECT. |
| Droite | 948–1454 | Section KARMA, 8 encodeurs KARMA SLIDERS, voyants MODULE, POWER. |

## Commandes (décisions de l'auteur, 16 oct. 2026)

**Gauche**
- Groupe 1 (rangées y = 54 et 146, OLED y = 82) : encodeurs 1–4 Filter Freq, Filter Reso, Filter EG, EG Release ;
  encodeurs 5–8 Knob Mod 1–4. Les noms s'affichent dans l'OLED (2 lignes : haut / bas).
- Groupe 2 (rangées y = 236 et 328, OLED y = 264) : 9–12 LFO 1 Speed, LFO 1 Depth, Ribbon, Port Time ;
  13–16 ENV A, ENV D, ENV S, ENV R.
- Supprimés (par rapport au rack KRONOS) : COMBI, PROG, SAMPLING, SEQUENCER, KARMA, DRUM, GLOBAL, MEDIA, MASTER, HEADPHONES.

**Centre** (remplace l'écran Set List du rack)
- PROGRAM : afficheur OLED « 000 », nom du programme (« I-A000 K-Lab: Katja's House »), ▲ ▼ ;
  sur une seule rangée (y = 106) : **COMBI, PROG** (voyant jaune = mode actif), puis **SW1, SW2** à leur droite.
  COMBI remplace le bouton jaune sans nom du device ; la rangée y = 128 ne garde que ▼.
- **Bouton U-A/AA** entre PROGRAM et BANK SELECT : un deuxième appui sur U-A sélectionne la banque U-AA
  (le KRONOS donne accès à U-AA…U-GG par l'écran).
- **BANK SELECT** : 2 rangées de 7 boutons noirs, nom en blanc, comme sur le KRONOS :
  I-A … I-G en haut, U-A … U-G en dessous (I-A allumé = banque sélectionnée).
- Menu GM à droite de BANK SELECT ; logo texte « KRONOS / KONTROL » **décalé à droite**
  (centre x = 864, KRONOS y = 131 corps 27, KONTROL y = 146 corps 8,5), à mi-hauteur entre l'écran GM et FX SWITCHES.
- **FX SWITCHES** (comme le KRONOS : 12 IFX, 2 MFX, 2 TFX), remontés (titre y = 160), 2 rangées (y = 167 et 189) :
  IFX1–IFX6 puis IFX7–IFX12 en dessous (x = 486 + i × 54) ; MFX1–MFX2 au niveau de la rangée haute,
  TFX1–TFX2 au niveau de la rangée basse (x = 827 et 881).
- Pavé X-Y (joystick) sous les FX SWITCHES (titre y = 227, pavé 618,234 – 180 × 100), avec flèches et bouton HOLD.
- Les boutons gris 1–8 du device sont supprimés : on garde les 8 encodeurs du bas (1/9 … 8/16), **plus gros**
  (rayon 15 au lieu de 11, y = 377, x = 566 + i × 50).
- Deux boutons empilés **MIXER** (allumé) **et PAN** (x = 486, y = 362 et 383) choisissent la fonction des 8 encodeurs
  (volume ou panoramique des timbres) ; encodeurs numérotés 1 … 8.

**Droite** (remplace les curseurs et le MASTER SLIDER du rack)
- KARMA SWITCHES 1-8 ; GE SELECT (menu « Arpeggio »), ON/OFF, LATCH, MODULE CTRL ; menu du GE
  (« 0 : Arp Model 01 Up/Dn ») ; ▲ ▼ ; marque KARMA (motif générique, pas le logo déposé) ;
  DRUM TRACK : **ON/OFF et MUTE** côte à côte (y = 150, x = 1146 et 1208) ;
  voyants MODULE MASTER, A, B, C, D ; SCENES 1-8.
- KARMA SLIDERS : 8 encodeurs **en dessous** (une rangée), avec bande OLED « SLIDER 1 … 8 ».
- La molette NAVIGATOR/VALUE du rack a été retirée pour faire de la place ; POWER reste en haut à droite.

**Style** : identique au rack KRONOS (face anthracite, boutons noirs à libellé blanc et voyant bleu, anneaux et OLED bleus #1ea7ff).

## Historique de la maquette
- 16 oct. : première version (BANK SELECT façon device : 7 INT + 4 US / 10 US).
- 16 oct. : BANK SELECT refait façon KRONOS (I-A…I-G / U-A…U-G) + bouton U-A/AA.
- 16 oct., 14 h 40 : logo décalé à droite ; COMBI ajouté, SW1/SW2 à droite de COMBI/PROG ;
  FX SWITCHES en 2 rangées (IFX1–12, MFX1–2, TFX1–2) ; pavé X-Y abaissé et raccourci (hauteur 100 au lieu de 112).
- 16 oct., 14 h 45 : 8 encodeurs du bas agrandis ; TRACK SELECT → boutons TRACK et MIXER ; bouton SOLO à côté de DRUM TRACK ON/OFF.
- 16 oct., 15 h 35 : TRACK → PAN, SOLO → MUTE, encodeurs 1–8 ; logo KRONOS / KONTROL (KORG retiré), agrandi.

## Device Max for Live et panneau CTRLR
- Le device (`reference\ref-kronos\m4l\Kronos Kontrol OS3.2.3_FR.amxd`,
  `_EN`, `_ES`) reprend ce rack tel quel dans une fenêtre de 1500 × 414 px
  (1 unité = 1 px), ouverte par le bouton « OUVRIR LE RACK » de la bande du
  device. Détails : `reference\ref-kronos\m4l\docs_dev\REPRISE.md`.
- **Le panneau CTRLR** (`KronosKontrol.panel`, complet-0.96) reprend la
  même maquette : fond `rack_fond.png`, commandes aux coordonnées
  ci-dessus. Testé sur le KRONOS le 16 oct. 2026 (complet-0.95) ; les
  corrections de complet-0.96 sont à tester — journal : `REPRISE.md`.

## Pistes pour la suite
- Lecture de l'état du KRONOS au chargement du panneau.
- Export VST3 du panneau (CTRLR File › Export) et test dans Live 12.
- Mode d'emploi FR/EN/ES du panneau.
- (La correspondance CC / SysEx de chaque commande est faite :
  `parameter_map.csv`, 124 lignes.)
