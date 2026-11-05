# KRONOS KONTROL / OASYS OMNI / NAUTILUS NAVIGATOR — panneaux de contrôle

*26-27 octobre 2026 — base graphique pour le panneau CTRLR / Lua et le futur VST3.*
*Dossier : `ctrlr-project\graphics` (panneaux principaux `*_Main`, fenêtre EDITOR `*_Editor`). Mise à jour du 28 oct. 2026 : dossiers renommés `*_Main`, sources dans chaque dossier `*_Main`, polices fournies.*

Trois panneaux bâtis sur le rack **Kronos Kontrol** (maquette du 16 oct. 2026) : mêmes écrans, mêmes commandes, mêmes coordonnées,
même taille **1500 × 432** (1 unité = 1 pixel ; 1500 × 414 jusqu'au 3 nov. 2026). Seul l'habillage change : couleurs, matières, boutons, afficheurs et logo.

| Panneau | Instrument | Habillage |
|---|---|---|
| **KRONOS KONTROL** | KRONOS | Rack d'origine (noir, afficheurs bleus). |
| **OASYS OMNI** | OASYS | Graphite & TouchView (ancienne proposition B). |
| **NAUTILUS NAVIGATOR** | NAUTILUS | Noir abyssal (ancienne proposition A). |

## Contenu

| Dossier / fichier | Rôle |
|---|---|
| `PLANCHE_EDITORS.png` | Les trois panneaux principaux retenus, l'un sous l'autre. |
| `KRONOS_Main\`, `OASYS_Main\`, `NAUTILUS_Main\` | Pour chaque panneau : `_maquette.png` (panneau complet, pour la relecture), `_fond` (sans parties actives, comme `rack_fond.png` du KRONOS) et `_notext` (même chose que `_fond`, mais afficheurs vides, sans aucun texte : pour des libellés dynamiques écrits par l'éditeur), en PNG 1500 × 432 et PNG @2x (3000 × 864) ; `_layout.json`, l'implantation des commandes (voir plus bas). KRONOS et OASYS : aussi les images des voyants MODULE, `_led_off`, `_led_on`, `_led_strip` (PNG et @2x). Les SVG et la maquette @2x ne sont pas conservés : `GFX_EXTRAS=1 python kt.py` les régénère. |
| `<panneau>_Main\sources_Main\` | Les scripts qui dessinent les panneaux (voir ci-dessous), une copie par panneau. Dans ce dossier, `python kt.py` régénère **ce** panneau dans `<panneau>_Main` ; `python kt.py KRONOS OASYS NAUTILUS` (un ou plusieurs noms) régénère les panneaux nommés, chacun dans son dossier `*_Main`. |
| `KRONOS_Editor\`, `OASYS_Editor\`, `NAUTILUS_Editor\` | La fenêtre EDITOR (pages 0.97i et éditeur complet), avec ses propres scripts (`KRONOS_Editor\sources_Editor`). Lire `KRONOS_Editor\README_EDITOR_KRONOS.md` (en anglais). |
| `EDITOR_WINDOW.md`, `README_EDITOR_0.97i_SPEC.md` | Spécification de la fenêtre EDITOR du panel complet-0.97i et sa note de présentation (en anglais). |
| `OASYS_Main\README_OASYS_MAIN.md` | OASYS : ce qui permet de relier le panneau à un OASYS (pas de SysEx publié, CC de la MIDI Implementation, banques) et les commandes du panneau sans équivalent sur l'OASYS (Drum Track, U-AA). |
| `RECIPE_PANEL_AUTOSCALE.md` | Recette : réduire automatiquement le panneau sur un écran de moins de 1500 px (Ctrlr, Lua, JUCE). |

Scripts de `sources_Main` (identiques dans les trois copies) :

| Fichier | Rôle |
|---|---|
| `kt.py` | Dessine le panneau d'après un thème et écrit le `_layout.json`. |
| `themes.py` | Les thèmes `KRONOS_KONTROL`, `OASYS_OMNI`, `NAUTILUS_NAVIGATOR` (liste `ALL`). Les propositions écartées restent dans le fichier (liste `PROPOSITIONS`), hors génération. |
| `txt2path_ext.py`, `txt2path.py` | Conversion du texte en tracés (Inter, DejaVu Sans Mono, Michroma, Montserrat). |
| `fonts\` | Toutes les polices, avec leurs licences (`README_FONTS.txt`) : Inter, DejaVu Sans Mono, Michroma, Montserrat. Rien à installer dans Windows. |
| `logo_kronoscopie.svg` | Logo Kronoscopie (copie de `logo-web\favicon\favicon.svg`), lu par `kt.py`. |
| `requirements.txt` | Modules Python : `pip install -r requirements.txt` (cairosvg demande aussi la bibliothèque Cairo sous Windows, par exemple le runtime GTK3). |

Contrôle (28 oct. 2026) : les scripts régénèrent des `_layout.json` identiques et des PNG identiques au pixel près aux fichiers de `*_Main`.

Le **fond** retire, comme `fond_device.py` : les encodeurs (seuls leurs numéros restent), les voyants allumés,
les textes variables des afficheurs et menus, la lampe des voyants MODULE (la lunette reste), la croix et les flèches du pavé X-Y.
Les libellés d'exemple des afficheurs (FILTER FREQ / KNOB MOD 1…, SLIDER 1-8, GATE / VELOCITY…) restent gravés dans le fond.

Le **notext** (27 oct. 2026) retire en plus **tous** les textes des afficheurs : bandes des encodeurs, SLIDER 1-8
(ARP / DRUM sur le NAUTILUS), champs PCG et messages. Il sert aux panneaux dynamiques, où l'éditeur écrit lui-même
ces libellés (entrées `display` / `menu` du layout, avec leur `text` d'exemple). Le layout donne les deux fonds :
`background` (`_fond`) et `background_notext` (`_notext`), avec leurs versions @2x.

## Implantation pour l'éditeur : `<panneau>_layout.json` (26 oct. 2026)
Pour construire l'éditeur (CTRLR, VST3) sur l'image de fond, chaque panneau a un fichier `_layout.json`, produit par `kt.py`
en même temps que les PNG (il est donc toujours à jour avec les images). Il contient :
- `width`, `height` (1500 × 432), `background` (`<panneau>_fond.png`) et `background_2x` ;
- `controls` : une entrée par commande, avec
  - `id` unique (ex. `fx_switches_ifx1`, `program_up`, `editor`, `xy`, `encoders_5`), `group` (section du panneau) et `label` ;
  - `type` : `button`, `knob` (encodeur), `display` (afficheur), `menu` (afficheur à menu déroulant ▼), `xy_pad`, `led`, `logo` ;
  - `x`, `y`, `w`, `h` en pixels du PNG 1x, origine en haut à gauche (× 2 pour le PNG @2x) ;
  - encodeurs : `cx`, `cy`, `r` (centre et rayon du bouton ; le rectangle inclut la couronne) ;
  - afficheurs : `text` (libellés d'exemple) et `dynamic` (contenu variable) ;
  - `midi` : vide (`null`), à renseigner avec le paramètre ou le SysEx de la commande.

Nombre d'entrées : KRONOS KONTROL et OASYS OMNI 118, NAUTILUS NAVIGATOR 123 (logo compris).

## Colonne EDITOR / IMPORT / WRITE / PLAY / SAVE / PCG (26-27 oct. 2026)
Présente sur les trois panneaux, au même endroit, sous IFX1 et IFX7, alignée sur leur bord gauche (x = 486).
Petits boutons : **49 × 18**, taille et style des autres boutons ; espacés comme ailleurs, 5 en largeur (pas des IFX)
et 4 en hauteur (IFX1 / IFX7, ▲ / ▼).
- **EDITOR** (ouvre l'éditeur développé dans CTRLR) : largeur d'IMPORT + WRITE, **103 × 32** ; haut au niveau du haut
  du cadre du pavé X-Y (y = 223) ; libellé dans la police, la graisse, la taille et l'espacement des titres de section
  (PROGRAM, BANK SELECT) ;
- **IMPORT** (x = 486) et **WRITE** (x = 540), côte à côte sous EDITOR (y = 259) ;
- **PLAY** sous IMPORT (y = 281) ;
- **SAVE** (y = 308) au-dessus de **PCG** (y = 330) ; PCG avec son champ ;
- à droite de PCG, le champ du nom de la banque chargée (`pcg_bank_name`, 387 × 16, jusqu'au bord droit de TFX2),
  au-dessus des 8 encodeurs du bas : hauteur et taille de police (7,5) de la bande SLIDER, en gras ;
  texte d'exemple : « No PCG loaded » ;
- les libellés restent sur le fond, comme ceux des autres boutons.

Pavé X-Y : **140 × 74** (au lieu de 180 × 100), entre la colonne et HOLD.
HOLD : même taille que TFX2 (**49 × 18**), aligné sur sa droite (x + w = 930).

## Champ des messages SysEx / Lua (27 oct. 2026)
Sous la bande SLIDER 1-8 (ARP / DRUM sur le NAUTILUS) : `messages_sysex_lua`, **474 × 14** (x = 964, y = 378),
fond jaune pâle, texte en DejaVu Sans Mono. Sert à la réception des messages SysEx et aux codes d'erreur Lua.
Texte d'exemple : « Lua: ready | SysEx IN: — » (retiré du fond, comme les autres textes variables).

## Logo Kronoscopie (27 oct. 2026)
À la place de POWER (interrupteur et libellé), en haut à droite : logo Kronoscopie (le favicon de kronoscopie.fr,
copié dans `sources_Main\logo_kronoscopie.svg`), **40 × 40** (x = 1397, y = 17) : même marge (17) en haut et à droite
(bord droit de la face = 1454). Il reste sur le fond.

## Voyants MODULE de KARMA (MASTER, A, B, C, D) — KRONOS KONTROL et OASYS OMNI
Le fond ne porte que la lunette du voyant ; la lampe, allumée ou éteinte, est à poser par l'éditeur. Deux façons :

**1. Avec des images (le plus simple dans CTRLR).** Pour chaque panneau, dans son dossier :
- `<panneau>_led_off.png` et `<panneau>_led_on.png` : 17 × 17, lunette comprise, fond transparent ;
- `<panneau>_led_strip.png` : les deux états l'un sous l'autre (17 × 34 : éteint en haut, allumé en bas), pour un
  composant à images multiples ;
- versions `@2x` (34 × 34, 34 × 68) pour le fond @2x.
On les place aux `x`, `y` du voyant dans le layout (ex. MASTER : 1311,5 ; 53,5 — ×2 pour le @2x : 2623 ; 107), puis on
change d'image selon l'état, depuis Lua ou par la valeur du composant.

**2. En les dessinant (JUCE, ou Lua si le composant le permet).** Chaque voyant du layout a une entrée `render` :
- `bezel` : cercle de rayon 8,5 (`fill`, `stroke`, `stroke_width`) ;
- `lamp` : cercle de rayon 6,5 centré en `cx`, `cy`, rempli d'un dégradé radial ; `on` et `off` donnent ce dégradé :
  centre (`cx` 0,4 ; `cy` 0,35) et rayon (`r` 0,7) en fraction du carré de la lampe (13 × 13), et `stops`
  [position 0-1, couleur] ;
- `state` : état montré sur la maquette (MASTER allumé, les autres éteints).

Exemple JUCE (C++) pour la lampe allumée du KRONOS (centre `cx`, `cy`, rayon 6,5 ; dégradé : centre à 0,4 / 0,35 du
carré, rayon 0,7 × 13 ≈ 9,1) :
```cpp
// dans paint (juce::Graphics& g) ; cx, cy = centre du voyant
const float x0 = cx - 6.5f, y0 = cy - 6.5f, d = 13.0f;
juce::ColourGradient grad (juce::Colour (0xffff8a80), x0 + 0.40f * d, y0 + 0.35f * d,
                           juce::Colour (0xff8a0000), x0 + 0.40f * d + 0.70f * d, y0 + 0.35f * d, true);
grad.addColour (0.5, juce::Colour (0xffff1a1a));
g.setGradientFill (grad);
g.fillEllipse (x0, y0, d, d);
```

## Les panneaux

**KRONOS KONTROL** — le rack d'origine : face noire, boutons à barre de voyant, afficheurs bleus, couronnes d'encodeurs bleues.

**OASYS OMNI** — face graphite brossée, oreilles alu. Boutons gris clair, voyants orange.
Encodeurs aluminium avec couronne de LED en points, en rappel des encodeurs à LED de l'OASYS. Afficheurs clairs façon écran TouchView.
Pavé X-Y bleu, en rappel du joystick vectoriel rétroéclairé en bleu.

**NAUTILUS NAVIGATOR** — noir satiné, boutons et afficheurs plus arrondis. Accents bleu-vert « grand fond »,
voyants blancs, afficheurs sombres façon écran TFT.

Logos : texte simple (« KRONOS » en Inter Light, « OASYS » en Michroma, « NAUTILUS » en Montserrat Light), avec en dessous,
même police et même taille, « KONTROL », « OMNI » ou « NAVIGATOR » ; ce ne sont pas les logos déposés.

## NAUTILUS : arpégiateurs à la place de KARMA
Le NAUTILUS n'a pas KARMA : la partie droite est remplacée par ses deux arpégiateurs, d'après le Guide d'utilisation
du NAUTILUS (chapitre « Arpeggiator function », p. 157-161) :
- façade : **ARPEGGIATOR** (ARP, LATCH, TAP) et **DRUM TRACK** (ON/OFF, MUTE) ;
- **ARPEGGIATOR A** et **ARPEGGIATOR B** : motif (P0-P4 UP, DOWN, ALT1, ALT2, RANDOM ; A0000-A2047, B000-B127) avec ▲ ▼,
  OCTAVE 1-4, LATCH, KEY SYNC, SORT, KEYBOARD, LOOP / 1 SHOT, RESO (Resolution) ;
- **SCENES 1-4** (4 scènes au lieu de 8) ;
- **ARP / DRUM** : 6 encodeurs = boutons RT en position ARP/DRUM : GATE, VELOCITY, LENGTH, SWING, DRUM SD, TEMPO.
Les voyants MODULE (propres à KARMA) sont retirés. Les deux arpégiateurs servent en COMBINATION et SEQUENCER ; en PROGRAM, un seul.
Les SysEx correspondants restent à établir.

## À trancher
- Le nom de programme d'exemple (« I-A000 K-Lab: Katja's House ») est celui du KRONOS ; il ne figure que dans les maquettes.

## Refonte du 3 novembre 2026 (hauteur 432)

Validée par le mainteneur sur maquettes (`ctrlr-project\panels\KronosKontrol\mockupenders`, v1 à v6), appliquée aux
trois panneaux Main et à toutes les pages EDITOR (KRONOS, OASYS, NAUTILUS) :
- **hauteur 414 → 432** : 18 px ajoutés en bas, même couleur ; les pages EDITOR ne changent pas autrement (la 4e rangée
  de cases du gabarit FX, coupée en 414, est maintenant entière) ;
- trous des oreilles : 40, 216 (milieu) et 392 (40 du bas) ;
- encodeurs de gauche : bloc du haut + 4 ; séparateur gris sur le trou du milieu (y = 216) ; bloc du bas placé à la même
  distance du bord bas que le bloc du haut du bord haut ;
- COMBI, PROG, SW1, SW2, HOLD : 49 × 18 (largeur des IFX), sur les colonnes IFX2 à IFX6 ; HOLD quitte la droite du pavé ;
- FX SWITCHES et les 16 boutons FX : - 8 ; pavé X-Y à x = 635, curseur = point blanc cerclé de la couleur des couronnes,
  flèches des rails alignées sur le curseur ;
- logo élargi de 2 px, centré entre le cadre du pavé et le séparateur vertical, centré en hauteur sur le pavé ;
- MIXER / PAN et leurs 8 encodeurs : + 8 ; encodeurs avec couronne (style EDITOR) ;
- bloc KARMA SLIDERS (NAUTILUS : ARP / DRUM) : + 12 ; encodeurs KARMA + 10 ; titre centré sur les encodeurs ; séparateur
  horizontal à mi-hauteur entre le bas des boutons SCENES et le titre ; libellés SLIDER 1-8 / GATE… en 9 gras ;
- champ des messages : 964, 396, 474 × 14 (bas à 410), texte 8,5 ; champ PCG : texte 9 gras (nom de fichier chargé
  affiché en MAJUSCULES : comportement du panneau, à coder dans Ctrlr).
