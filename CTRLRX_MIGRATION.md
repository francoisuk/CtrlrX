# Migration Ctrlr 5.6.23 → CtrlrX 5.6.36 (décision du 3 nov. 2026)

## Décision du mainteneur

- Kronos Kontrol avait été construit sur **Ctrlr-x64 VST3 5.6.23** (`build/Ctrlr-x64_VST3_v5.6.23/`).
  C'était une erreur : le moteur de référence est désormais **CtrlrX 5.6.36** de Damien Sellier
  (github.com/damiensellier/CtrlrX, publié le 21 oct. 2026), qui corrige un grand nombre de bogues.
- Application installée : `C:\Program Files\CtrlrX Project\CtrlrX\CtrlrX.exe` (version autonome,
  34 179 384 octets, 21 oct. 2026). C'est elle qui sert à ouvrir, éditer, tester et **exporter** le panneau
  (CtrlrX exporte lui-même en VST3 ou en exécutable).
- **Ctrlr 5.6.23 n'est plus utilisé. SAVIHost3 non plus**, sauf pour tester un VST3 exporté.
- Le panneau doit être **reconstruit et revu** pour CtrlrX 5.6.36 (revue par parties, sur instruction du mainteneur).

## Règle d'export : +24 px de hauteur

Bogue connu signalé par de nombreux utilisateurs : à l'export en VST3 ou en exécutable, il faut **ajouter
24 px à la hauteur** du panneau (1500 × 414 → 1500 × 438). Vérifié dans le source 5.6.36 :

- `CTRLR_MENUBAR_HEIGHT = 24` (`Source/Core/CtrlrMacros.h:23`), propriété `ctrlrMenuBarHeight = 24`,
  forcée aussi pour les instances exportées depuis 5.6.31 (`CtrlrManagerInstance.cpp:45`).
- `CtrlrEditor.cpp:68-89` : la taille de la fenêtre part de `ctrlrEditorBounds` ; si
  `uiPanelMenuBarVisible` est vrai, la barre de menu (24 px) est ajoutée/prise sur cette hauteur.
- À l'export, `uiPanelMenuBarVisible` est remplacé par `!uiPanelMenuBarHideOnExport`
  (`CtrlrPanelFileOperations.cpp:34-35`).
- Notre panneau : `uiPanelCanvasRectangle="0 0 1500 414"`, `uiPanelMenuBarVisible="1"`,
  `uiPanelMenuBarHideOnExport="1"`, `uiViewPortMode="Scaled"`. En mode Scaled, 24 px de moins pour le canevas
  = zoom ≈ 390/414 et décalage : c'est très probablement ce qui a abîmé l'affichage du VST 1.0b.
- À faire au moment de l'export : appliquer +24 px (et vérifier dans CtrlrX quelle propriété le porte,
  canevas ou bornes d'éditeur), puis contrôler visuellement l'instance exportée.

## Source de référence mis à jour

- `build/CtrlrX-damiensellier/CtrlrX/` : **clone git** de damiensellier/CtrlrX, sur l'étiquette **v5.6.36**
  (commit `d35edd226089263bd08317cb289d97e6566090a6`, 21 oct. 2026) = la version installée.
  Mise à jour future : `git fetch --tags` puis `git checkout <étiquette>`. (Le `master` distant a reçu des
  commits après l'étiquette, le 25 oct. ; on reste sur l'étiquette publiée.)
- L'ancien instantané 5.6.35 (`CtrlrX-master/`) a été supprimé le 3 nov. 2026 à la demande du mainteneur.
- Export 1.0b fait avec 5.6.23 : mauvais résultats, notamment les menus déroulants — avant de connaître la
  règle des 24 px, qui en explique sans doute une partie.
- Documentation nouvelle dans le clone : `Doc/manual/` (manuel utilisateur, 10 chapitres),
  `Doc/readme/05-exporting-instances.md`, `Doc/readme/06-changelog.md` (5.6.24 → 5.6.36), `Doc/LUAJIT.md`.

## Ce qui change pour Kronos Kontrol (5.6.23 → 5.6.36)

CtrlrX est issu de Ctrlr 5.6.23 (« Version 0.0.0 — forked from Ctrlr 5.6.23 ») ; tout le journal 5.6.24 → 5.6.36
s'applique donc. Points qui nous concernent directement :

### Corrige des problèmes connus du projet
1. **VST3 affiché « Ctrlr (Instigator) »** (point suspect 2 de la reprise) — résolu depuis 5.6.32 : à l'export,
   CtrlrX remplace dans le binaire le nom, le code plug-in, le fabricant et le type par ceux du panneau
   (`Native/CtrlrWindows.cpp:225-301`) : `name` (32 octets max), `panelInstanceUID` (4, chez nous `KrKt`),
   `panelAuthorName` (16 octets max — CtrlrX écrit un octet par caractère, `CtrlrWindows.cpp:407-421` :
   « François Rossi » = 14 octets avec ç en Latin-1 0xE7, pas en UTF-8 ; à décider, voir journal du 3 nov.),
   `panelInstanceManufacturerID` (4, `FrRs`), `panelVersionMajor/Minor`, `panelPlugType`
   (« Instrument|… »). Condition : `panelReplaceVst3PluginIds` activé. Notre panneau n'a pas encore
   `panelPlugType` ni `panelReplaceVst3PluginIds`, et `panelVersionMajor/Minor` valent 0.1 → à régler.
2. **Ressources figées** (point suspect 1) — 5.6.36 : « Resources not updating on load after panel update »
   corrigé, les ressources sont comparées par empreinte (`CtrlrPanelResourceManager.cpp`). La manœuvre
   `.delete_me_to_reload_resources` ne devrait plus être nécessaire (à vérifier).
3. Instances exportées : nombreuses corrections 5.6.28–5.6.31 (barre de menu absente/présente, onglets de
   panneau visibles, LookAndFeel non appliqué, plantage si `panelIsDirty = 0`, nombre de paramètres VST
   pris du plus grand `vstIndex` au lieu de 64, apparition dans Ableton Live).
4. Hôte → panneau en VST3 : automation et sortie MIDI des modulateurs réparées (5.6.32J/5.6.33 ; avant,
   seuls les 10 premiers modulateurs envoyaient du MIDI).
5. MIDI : curseurs qui ne réagissaient pas hors canal 1 (5.6.36) ; fuite d'entrée MIDI entre panneaux
   (5.6.36) ; modulateurs de même CC qui ne réagissaient pas (5.6.34) ; MSB 14 bits envoyé 0xFF au lieu
   de 0x7F (5.6.31) ; modulateur qui ne réagissait pas à l'entrée MIDI (5.6.31).
6. `uiSlider`/`uiImageSlider` n'atteignant pas `maxValue` avec `minValue` négatif (5.6.31) ; positions
   de curseurs sur `uiTabs` mal enregistrées (5.6.35) ; propriétaire de groupe perdu sur `uiTabs` (5.6.36) ;
   duplication de modulateurs au chargement (5.6.36).
7. Windows : plus de plantage au chargement d'un panneau dont un callback Lua est fautif (5.6.32).

### Changements qui peuvent casser notre Lua (à revoir)
1. **Lua 5.1 → LuaJIT 2.1** (5.6.36). LuaJIT est compatible Lua 5.1 ; nos scripts (`lua/kkMain.lua`,
   `kkEd.lua`, `kkEdGui.lua`, `kkPcg.lua`) n'utilisent ni `setfenv`, ni `bit32`, ni `module()`.
   À valider en réel (smoke + chargement). Une variante « LEGACY LUA 5.1 » existe dans le dépôt (.jucer).
2. **Chaînes Lua lues en UTF-8** (5.6.36, `stdafx_luabind.h:163-165`, `LCore.cpp:227`). Notre
   contournement **`kkU`** (`kkEdGui.lua:17-20`, ré-encode UTF-8 → Latin-1 pour toutes les étiquettes,
   menus et le moniteur) a été écrit pour 5.6.23 ; sous 5.6.36 il fabriquera des octets Latin-1 invalides
   en UTF-8 → **texte accentué abîmé**. À neutraliser. Même question pour `kkL1toUtf8`/`kkUtf8toL1`
   (`kkMain.lua`, noms de programmes).
   Attention : dans le sens C++ → Lua, `lua_pushlstring(L, value.toUTF8(), value.length())`
   (`stdafx_luabind.h:170`) passe le nombre de *caractères* et non d'*octets* → une chaîne non-ASCII lue
   depuis CtrlrX (ex. `getPropertyString`) est tronquée de la fin. Bogue amont à signaler / contourner.
3. **Curseurs en double** (5.6.32) : `getValue()`, `getModulatorValue()`… renvoient des nombres
   décimaux ; variantes entières `getValueInt()`, `getModulatorValueInt()`, etc. À vérifier là où nos
   valeurs servent d'index ou d'octets SysEx.
4. Préférence « Run modulator valueChange LUA callback in Bootstrap state » (5.6.32) : change le
   comportement des callbacks pendant le chargement du panneau.
5. Options MIDI par défaut des plug-ins : « Input from plugin host » + « Input from host to comparator »
   (5.6.34). À vérifier pour le routage vers le Kronos.
6. LookAndFeel V4 et schémas de couleurs (5.6.29–5.6.30, logique LnF modifiée en 5.6.36) : les panneaux
   anciens passent en V2/V3 ; nos couleurs de composants sont à contrôler visuellement.

### Nouveautés utiles
- `ctrlrMenuBarHeight` réglable ; `uiPanelViewPortBackgroundColour` ; redimensionnement responsive par
  callback (5.6.28) ; `setChangeNotificationOnlyOnRelease` ; callbacks `mouseUp/Enter/Exit` ; bulles d'aide ;
  `showTextEditor()` pour labels/curseurs ; checksums Korg dans le processeur SysEx (5.6.34) ;
  `PluginHostType` et `SystemStats` en Lua ; export exécutable autonome ; signature Windows par PFX.

## Impact sur la documentation du projet

- `build/BUILD_README.md` (épinglage de version) : mis à jour.
- Les mentions « SAVIHost3 + Ctrlr 5.6.23 » dans `RESUME.md`, `PROMPT.md`, `panels/KronosKontrol/*.md`
  et `tools/panel-harness/` sont historiques : elles décrivent les tests 0.95–1.0b, pas la méthode actuelle.
