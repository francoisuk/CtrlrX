# Le savoir consolidé : fichiers PCG du KRONOS, usines, SysEx, MIDI et Max for Live

*Le grand livre du KRONOS · dossier `bonus/consolidate` · 13 octobre 2026*
*Pour développer un éditeur / bibliothécaire de sons du KRONOS sans refaire la rétro-ingénierie.*

Légende : ✅ vérifié sur des fichiers de Korg ou sur un KRONOS · ⚠️ hypothèse ou point ouvert.
Les numéros d'octets sont **décimaux** et **relatifs au début de l'objet** (programme, combinaison…), sauf mention contraire.

---

## 1. Les sources de vérité

| Quoi | Où | Note |
|---|---|---|
| Tables octet par octet de Korg (objets v5, combinaisons v3, effets, kits, séquences d'ondes, Global, SysEx) | `04_Outils/PCG/data/01_MIDI_implementation_Korg/` (KRONOS MIDI Implementation v1.27, 2016) | décrit le format **OS 2/3** seulement |
| Les mêmes tables en JSON/CSV, au bit près | `05_tables/` ici (copie de `PCG/data/02_Tables_parametres`) | chaque paramètre : octet, bits, largeur, valeurs |
| Les PCG d'usine | `04_Outils/PCG/FACTORY*` (6 PRELOAD, EXs, KRS-06, INIT) | **à ne pas diffuser** (données de Korg) |
| Noms et places de tous les sons d'usine, par OS | `01_web/pcgconvert-data.js` (JSON, 135 Ko) | noms et positions seulement : diffusable |
| Code qui fait foi | `01_web/pcgconvert-core.js`, `pcgreader-core.src.js`, `pcgbridge-core.js` | testé (voir § 13) |
| Code de PCG Tools (C#, LGPL v3) | `04_Outils/coding/PCG Tools/PCG-Tools-master` | utile, mais **3 erreurs** relevées (§ 12) |

---

## 2. Structure d'un fichier PCG ✅

```
00  'KORG'  68  00  02  osv  01  00 00 00 00 00 00 00      en-tête 16 octets
         68 = KRONOS · 02 = PCG · osv = 00 (OS 1) / 01 (OS 2) / 02 (OS 3.0 à 3.2)
10  'PCG1' taille(u32 BE) 00000400                          tout le reste du fichier
      'DIV1' …                       sommaire des banques (§ 2.3)
      'INI2' 'INI1'                  OS 1 seulement : index des blocs (§ 2.4)
      'SLS1' [ 'SLD1' ['SDB1'] , 'STL1' ['SBK1'] ]           Set Lists
      'PRG1' [ 'MBK1' (EXi) | 'PBK1' (HD-1) … ]              programmes
      'CMB1' [ 'CBK1' … ]                                    combinaisons
      'DKT1' [ 'DBK1' … ]                                    kits de batterie
      'WSQ1' [ 'WBK1' … ]                                    séquences d'ondes
      'GLB1'                                                 Global
      'DPI1'                         parfois (KRS-06, sauvegardes complètes) : rôle inconnu, on le recopie
```

### 2.1 Les blocs
- Bloc = `id (4 car.) | taille du corps (u32 gros-boutiste, sans les 12 octets d'en-tête) | champ (u32) | corps`.
- **Conteneurs** (PCG1, PRG1, CMB1, DKT1, WSQ1, SLS1, SLD1, STL1) : champ = `version << 16 | 0x0400`.
- **Banques** (MBK1, PBK1, CBK1, DBK1, WBK1, SBK1, SDB1) et **GLB1** : champ = `version << 16 | somme8`.
- **somme8 = somme de tous les octets du corps (catalogue compris) & 0xFF.** Le KRONOS refuse un fichier dont une somme est fausse. Les 15 PCG d'usine et du livre sont reconstruits à l'octet près en recalculant toutes les sommes ✅.
- Corps d'une banque : `n (u32) | taille d'un élément (u32) | numéro de banque (u32)` puis `n` éléments.
- ⚠️ **La taille annoncée de PCG1 peut être fausse** (ex. `Kronos_Preload_VB.pcg`, sauvegarde complète d'OS 2 : 47 Mo annoncés pour 152 Mo). Lire jusqu'à la fin du fichier, pas jusqu'à la taille annoncée. pcgtoolkit le fait depuis v1.2.
- ⚠️ **Banques « virtuelles »** : ce même fichier contient des banques numérotées 0x30 à 0x6F (programmes et combinaisons), pleines de « Init ». Les ignorer.

### 2.2 Versions et tailles des objets ✅

| Bloc | OS 1 | OS 2 | OS 3.0 → 3.2 | Taille d'un élément |
|---|---|---|---|---|
| MBK1 (programmes EXi) | v3 | v5 | v5 | 4 960 |
| PBK1 (programmes HD-1) | v4 | v5 | v5 | 4 960 (3 450 utiles en OS 1, 3 706 ensuite) |
| CBK1 (combinaisons) | v3 | v3 | v3 | 7 810 |
| DBK1 (kits) | v2 | v3 | v3 | 22 040 → 38 424 |
| WBK1 (séquences d'ondes) | v0 | v1 | v1 | 1 192 → 2 216 |
| GLB1 | v1 (24 620) | v1 (24 620) | **v2 (24 708)** | |
| DIV1 (champ) | 00000000 | 00010000 | 00010000 | 44 octets |
| DKT1 / WSQ1 (champ) | 00020400 / 00000400 | 00030400 / 00010400 | idem OS 2 | |

Kits : banque INT de **40** kits, puis 16 par banque utilisateur. Séquences d'ondes : INT **150**, puis 32 par banque.

### 2.3 DIV1, le sommaire (44 octets, u16 gros-boutistes) ✅
**OS 2 et 3** :
```
00000000
[masque bas, 0015, masque haut, 0015]    programmes (bit i = index PN, § 3)
[masque bas, 000E, masque haut, 000E]    combinaisons (bit i = index CN)  ⚠️ Korg écrit parfois 000F en 4e mot
[masque bas, 000F, masque haut, 000F]    kits (bit 0 = INT, bit n = 0x20000+n-1)
[masque bas, 000F, masque haut, 000F]    séquences d'ondes
[DPI, Set Lists, 00, Global]              4 octets : 1 si présent
[0001 (OS 2) | FFFF (OS 3), 0000]
```
**OS 1** : `00000000`, puis pour programmes / combinaisons / kits / séquences : `[masque, nb, dernière banque + 1 (ou nb si aucune), 0]` avec nb = 0E, 0F, 09, 09 ; puis `[Set Lists ? 1 : 0, 0]` ; puis `[6 si fichier complet, 3 si combinaisons, sinon 2 ; 0]`. Le 4e mot de chaque groupe et le 2e mot du groupe Set Lists sont des restes de mémoire chez Korg (on écrit 0).

### 2.4 INI2 et INI1 (OS 1 seulement) ✅
Index de tous les blocs, dans l'ordre du fichier (conteneur, puis ses banques ; SLS1 sans ses enfants).
- `u32 nombre d'entrées`, puis entrées de **64 octets (INI2)** ou **52 octets (INI1)** :
  `id(4) | n° de banque(4) | 0x14(4) | taille(4) | position(4) | n(4) | taille élément(4) | n° de banque(4) | nom(16) | 0(4)`
  + pour INI2 : `00 | version | somme8 | 00 | 0 × 8`.
- position = début du corps (conteneur, GLB1, SLS1) ou **début des éléments** (banque : en-tête + 24).
- Noms : « Programs », « Combinations », « Drum Kits », « Wave Sequences », « Set Lists », « Global Setting », « Bank I-A », « 000-039(Int) », « 040-055(U-A) », « 150-181(U-A) »…
- SLS1 : taille, n, taille d'élément et somme de **SBK1** ; version 0. GLB1 : n = 1, élément = taille, version 1, somme 0. Conteneurs : n = 0, somme 0, version de leur champ.
- La somme d'une banque est donc écrite **deux fois** (champ de la banque et INI2 +54) : les deux doivent être justes.
- Générateur testé : `iniBlocks()` de pcgconvert-core.js redonne à l'octet près les INI des PCG EXs OS 1 de Korg.

### 2.5 OS 1.5/1.6 : le format en deux parties
Blocs `PRG2`, `CMB2`, `DKT2`, `WSQ2`, `STL2`, `INI3` (ex. `FACTORY/INIT.PCG`). Paramètres ajoutés hors des objets. **Non géré** : à refuser, en demandant de charger le fichier sur un KRONOS puis de faire un Save All. PCG Tools le gère (`GetParameterOffsetInPbk2`).

---

## 3. Les banques et leurs quatre numérotations ✅

| Banque | N° dans le fichier | Index DIV1 / PN | « Bank Number » (timbre, Drum Track, Set List programme) | MIDI CC0/CC32 (Bank Map KORG) |
|---|---|---|---|---|
| I-A … I-E | 0 … 4 | 0 … 4 | 0 … 4 | 0 / 0 … 4 |
| I-F | **0x8000** | 5 | 5 | 0 / 5 |
| GM, g(1)…g(9), g(d) | absentes | — | 6, 7…15, 16 | 121/0, 121/1…9, **120/0** |
| U-A … U-G | 0x20000 … 0x20006 | 6 … 12 | 17 … 23 | 0 / 8 … 14 |
| U-AA … U-GG | 0x20007 … 0x2000D | 13 … 19 | 24 … 30 | 0 / 15 … 21 |

Combinaisons : I-A…I-G = 0…6 dans le fichier, U-A…U-G = 0x20000…0x20006 (index DIV1 7…13). **Dans une Set List**, banque de combinaison : 0-6 = I-A…I-G, **17-23** = U-A…U-G. MIDI : combinaison **I-G = 121/0** ; U-A… = 0/8….
Une banque de programmes est **EXi (MBK1) ou HD-1 (PBK1)**. Charger une banque entière change le type de la destination ; un programme seul exige une destination du même type. L'OS 1 n'a que I-A…U-G (13 banques de programmes) ; l'OS 2 et 3 en ont 20.

---

## 4. Le programme (4 960 octets) ✅

Règles de codage : champs **au bit près**, poids faible d'abord ; valeurs 16 bits **petit-boutistes** ; négatifs en complément à deux sur la largeur du champ ; valeurs brutes (la table donne l'affichage). Tables : `05_tables/Programme_EXi_commun.json`, `Programme_HD-1.json`, `Moteur_*.json`, `Effets.json`.

| Octets | Contenu |
|---|---|
| 0-23 | nom (latin-1, complété par 00) |
| 24 + 74 × (n−1) / 88 + 74 × (n−1) | IFX n (n = 1…12) : 64 octets de paramètres / type d'effet |
| 912-1183 | MFX 1-2, TFX 1-2 (même schéma) ; types 0-197 |
| 1252-1302 | contrôleurs ; Drum Track commun (1292 n° de motif, **1295 bit 4 = Drum Track On**) |
| 1304-2474 | KARMA (1814-1815 : n° de GE, 0-3583) |
| 2558 | **mode d'oscillateur** (HD-1, bits 0-2) : 0 Single, 1 Double, 2 Drums, 3 Double Drums |
| 2568-2571 | catégorie, gamme |
| 2586-2683 | Tone Adjust |
| **2688 / 2689** | **Drum Track Program : n° / « Bank Number »** (§ 3) |
| 2857 / 3909 | **moteur de l'EXi 1 / EXi 2** : 0 Off, 2 AL-1, 3 CX-3, 4 STR-1, 5 MS-20EX, 6 PolysixEX, 7 MOD-7, 8 SGX, 9 EP-1 |
| 2908-3907 / 3960-4959 | bloc du moteur de l'EXi 1 / EXi 2 (1 000 octets ; table `Moteur_<moteur>`, offset + 2908 ou + 3960) |

**HD-1** (PBK1) : mêmes parties communes jusqu'à 2773, puis les oscillateurs.
- Oscillateur 1 à **2774**, oscillateur 2 à **3240** (pas de 466). 8 zones de **22 octets** par oscillateur :
  `+0 type (0 Off, 1 multi-échantillon, 2 séquence d'ondes) | +1…+16 UUID de banque | +17 00 | +18-19 numéro (u16 LE) | +20-21 …`
- En mode **Drums**, la zone 1 de l'oscillateur désigne un **kit** : numéro = index global du kit (0-39 INT, 40 + 16 × (banque − 1) + n).
- Séquence d'ondes : numéro = **index global** (0-149 INT, 150 + 32 × (banque − 1) + n), **en OS 1 comme en OS 2/3** (PCG Tools se trompe, § 12).
- Utiles : 3 706 octets. Les 1 254 derniers octets de la case ne sont pas lus (on les recopie ; Korg y laisse des restes).

**Moteurs, détails utiles**
- EP-1 : modèle = `(bloc[0] >> 7) | ((bloc[1] & 3) << 1)` ; 0 Tine EP I Late, 1 Tine EP II, 2 Tine EP V, 3 Tine EP DMP, 4 Reed EP 200, 5 Reed EP 200A, **6 Tine EP I Early (OS 3.2.1+)**.
- SGX(-2) : bloc[0-1] = **n° de piano sur 16 bits** (8 bits en OS 1) ; **72-79 = pianos de l'OS 3.2** ; octets 13+ = réglages ajoutés par l'OS 3 (résonance des cordes…), à zéro en OS 2.
- MOD-7 (bloc + 467) et STR-1 (bloc + 541) : 4 bits de types de MS (High, Mid High, Mid Low, Low), puis **4 UUID de 16 octets décalés d'un demi-octet**, puis 4 numéros de MS sur 14 bits.
- CX-3 : octet 67 du bloc, bit 3 « Amp & Rotary Version » (Classic / Custom, apparu en OS 2).

---

## 5. Combinaison (7 810 octets) ✅
- 0-23 nom ; effets, KARMA, contrôleurs comme un programme (table `Combinaison.json`).
- **16 timbres de 188 octets à partir de 4802** : `+0 n° de programme | +1 « Bank Number » (§ 3) | +2 bits 0-4 canal (16 = Global), bits 5-7 statut (0 Off, 1 INT, 3 Ext, 4 Ext2) | +3/+4 Bank MSB/LSB (pour Ext) | +5 volume | +14 pan | +37/38 zone de clavier | +40/41 zone de vélocité …`
- Un timbre Off garde une référence (souvent I-A000) : sans effet, mais à mettre à jour quand on déplace des sons, comme le fait Korg.

## 6. Set Lists ✅
- `SLS1 [ SLD1 [SDB1] , STL1 [SBK1] ]`. SBK1 : n = 128 Set Lists de **69 416 octets** (0x10F28) : nom (24), puis 128 emplacements de **542 octets** à partir de +24.
- Emplacement : `+0 nom (24) | +24 bits 0-1 type (0 combinaison, 1 programme, 2 morceau) | +25 bits 0-4 banque (programme : « Bank Number » ; combinaison : 0-6 / 17-23) | +26 numéro | … texte de description`.
- SBK1 et SDB1 portent une somme8 comme les banques.

## 7. Kit de batterie et séquence d'ondes ✅
- **Kit v3** : nom (24), puis 128 notes × 300 octets : 8 zones de **34 octets** `[On/Off, UUID(16), 00, n° d'échantillon (u16), niveau, offset, transposition, accord, attaque, déclin, coupure, résonance, EQ ×3, drive, low boost, *]`, puis 28 octets par note (vélocités des zones, pan, bus, envois, groupe exclusif, assign…). OS 1 (v2) : zones de 18 octets (un octet de banque au lieu de l'UUID).
- **Séquence d'ondes v1** : 40 octets communs, puis 64 pas de **34 octets** `[type (bits 0-1 : 0 MS, 1 Rest, 2 Tie), UUID(16), 00, n° de MS (u16), niveau, start offset/reverse, accord (16), transposition, AMS1/2, durée, …]`. OS 1 (v0) : pas de 18 octets.

## 8. Références aux échantillons (la vraie différence OS 1 / OS 2+) ✅
- OS 1 : **un octet de banque** (0 = ROM, n = banque Korg) devant le numéro.
- OS 2+ : **UUID de 16 octets**. Banques Korg : `'KORG' + 00 × 8 + 'MS' + 00 + code` (le même code que l'octet OS 1). Banques d'échantillons utilisateur (apparues en OS 2) et EXs au-delà de 125 : UUID aléatoire (celui de la banque MS ; **UUID + 1 = banque de Drum Samples**).
- ⚠️ Le code n'est pas le numéro d'EXs (ex. sons « EXs18 » : codes 0, 33, 39) : ne pas l'afficher comme « EXs n ».
- UUID des EXs du KRONOS 3 (dans `PRELOAD.KSC` de l'OS 3.2, lignes `#>uuid:`) : EXs206 A2D 8e7ab882-4abf-4317-b095-874bc9627802, EXs207 Bolder 6bfff2f4-…4a46, EXs208 K-Sounds 799f7fea-…51c6, EXs209 KApro f73b1828-…3e70, EXs210 KARO 07640959-…7b22, EXs211 Kelfar e23b4956-…da62, EXs212 Kid Nepro 79f80df0-…3a78, EXs213 PCreek 1 90d97dc6-…db56, EXs214 PCreek 2 a19cc863-…f650, EXs216 Soundiron 86930f1d-…50ac, EXs217 SOP 609199a0-…5a34, EXs218 Irish Acts f0418e34-…42d2 (liste complète dans `pcgconvert-core.js`, `EXS_UUID`).
- KSC (format texte) : `#KORG Script Version 1.0`, `#v2`, `#uuid:…` (banque d'échantillons de l'utilisateur), `#>BankN.M.D.Nom` (EXs ≤ 125, N compté à partir de 0 : Bank0 = EXs1), `#>uuid:U.M.D.Nom`, `#>>uuid:U.TTn.V.B.Nom` (lien vers un MS/DS). Parameter Guide, « KSC 2.0 format ».

---

## 9. Ce qui change d'un OS à l'autre ✅

| Passage | Format | Contenu d'usine |
|---|---|---|
| OS 1 → OS 2 | UUID des échantillons (HD-1, MOD-7, STR-1, kits, séquences d'ondes) ; SGX 8 → 16 bits ; **rien d'autre** (AL-1, MS-20EX, PolysixEX, EP-1, CX-3, communs, combinaisons, Set Lists, Global identiques) | mêmes places ; sons « V2 » retouchés (CX-3 surtout), 30 kits retouchés |
| OS 2 → OS 3 | en-tête 02, Global v2 (+ 88 octets : 39 × `10 FF` + 10 × 00), DIV1 dernier mot FFFF | **ordre nouveau** : les 1 536 programmes et 480 combinaisons déplacés (ex. I-A000 → I-C000 ; combinaison I-A000 → I-A008 ; kits de Drum Track I-F → U-BB) ; 12 SGX, 3 CX-3, 1 PolysixEX retouchés |
| OS 3.1 → 3.2 | rien | nouvelles valeurs (EP-1 n° 6, SGX 72-79) ; banques U-CC, U-DD, U-EE ; combinaisons I-E, I-F ; quelques kits et séquences d'ondes |

Conversion : voir `01_web/pcgconvert-core.js` (`hdUp/hdDown`, `exiUp/exiDown`, `kitUp/kitDown`, `wsqUp/wsqDown`, `convert`) ou `02_python/kronos_pcg.py`. Le KRONOS convertit tout seul vers le haut ; depuis l'OS 3.0.3, il propose aussi de remapper les références d'un PCG de l'OS ≤ 2.1, **seulement avec .PCG Contents = All**.

## 10. Les usines (PRELOAD) ✅
- 6 PRELOAD : OS 1 (avril 2011), OS 2 (2013), OS 3.1 « nouveau KRONOS », **OS 3.1 KRONOSX**, OS 3.2 (déc. 2025), **OS 3.2 KRONOSX**.
- **Deux ordres en OS 3** : l'ordre « nouveau KRONOS » (KRONOS 2, 3) et l'ordre **KRONOS / KRONOS X** (`PRELOAD_KRONOSX.PCG`) = ordre de l'OS 2 pour I-A…U-F, puis U-AA, U-BB (et U-CC…U-EE en 3.2). Un KRONOS de 2011 ou X mis à jour peut être dans l'un ou l'autre (c'est le cas de l'auteur : KRONOS de 2011 en OS 3.2.3, ordre KRONOS X).
- Les kits et séquences d'ondes ne bougent pas d'un OS à l'autre (seulement des ajouts).
- Correspondances : `pcgconvert-data.js` donne, pour chaque usine (F1, F2, F31, F31X, F32, F32X) et chaque banque, l'identifiant du son à chaque place ; même identifiant = même son. Construit par `03_outils/gen_data.py` (contenu identique, puis nom unique ; vérifié : 1 536/1 536 programmes, 480/480 combinaisons ; les 7 680 timbres des combinaisons OS 2 tombent sur les programmes des combinaisons OS 3.1).
- Effectifs : OS 1/2 1 536 programmes, 512 combinaisons ; OS 3.1 1 792, 512 ; OS 3.2 2 176, 768 ; 88 kits ; 182 (OS 1/2) puis 214 séquences d'ondes.

## 11. SysEx (Object Dump) ✅ essayé sur KRONOS (13 oct. 2026, 5/5)
- En-tête `F0 42 3g 68` (g = canal MIDI global − 1).
- Type de banque : `F0 42 3g 68 7C banque type F7` (1 = EXi, 0 = HD-1).
- Objet : `F0 42 3g 68 73 obj banque idH idL version données(8→7 bits) F7` ; obj 00 programme (v5 ; EXi 4 960 o, **HD-1 3 706 o**), 01 combinaison (v3, 7 810).
- Enregistrer : `F0 42 3g 68 76 obj banque F7` (Store Bank Request ; réponse : code 0 = réussi).
- Codes de banque : programmes I-A…I-F = 00…05, U-A…U-GG = 40…4D ; combinaisons I-A…I-G = 00…06, U-A…U-G = 40…46.
- 8 → 7 bits : par groupes de 7 octets, un octet de poids forts (bit j = bit 7 de l'octet j) puis les 7 octets & 0x7F.
- Envoi : une pause d'au moins 100 ms entre messages ; Erriez MIDI SYSEX-IO (Windows 11) : 5 fichiers, 5 réussites.
- Autres fonctions (table complète en tête de `05_tables/KRONOS_MIDI_SysEx.txt`) : 72 demande d'objet, 77 demande de banque, 74/75 objet courant (le son en cours d'édition), **37/38 et 39/3A « Bank Digest »** (empreintes de banques : idéal pour qu'un bibliothécaire sache ce qui a changé dans le KRONOS sans tout relire), 32/33 identifiant du son courant, **34/35/36 types de pianos SGX installés**, 30/31 échantillon courant, 79/7A SMF.
- Édition en direct : **43 Parameter Change (entier)**, **44 Parameter Change (binaire, pour les UUID)** — ⚠️ la table `WaveSequence.txt` parle de 0x56 : se fier à la liste des fonctions —, 41 séquenceur, 6D KARMA, 6E Drum Track. Kronos Kontrol utilise 43 pour les FX et le GE.

## 12. PCG Tools : ce qui est juste, ce qui ne l'est pas
- Juste : structure, sommes (+11 et INI2 +54), format en deux parties, copier-coller entre fichiers de même génération, Program Reference Changer (combinaisons et Set Lists).
- **Faux** : (1) séquence d'ondes OS 1 = couple banque/numéro (`KronosProgram.cs` l. 273) : c'est un index global ; (2) kit appelé par un programme HD-1 lu à `zone + 2` (code hérité de l'OASYS) : c'est `zone + 18` ; (3) `KronosV2V3Rules.txt` : U-A000..001 → U-AA126..127, U-A023..024 → U-BB007..008, I-C095..097 → U-D125..127 manquants.
- Absent : OS 3.2, conversion entre générations, Drum Track dans le remappage, ordre KRONOSX.

## 13. Pièges pour un éditeur / bibliothécaire
1. **Recalculer toutes les sommes** (banques, GLB1, SBK1/SDB1 ; en OS 1 aussi INI2) à chaque écriture.
2. Ne pas croire la taille de PCG1 ; ignorer les banques inconnues ; refuser l'OS 1.5/1.6.
3. Un son déplacé = mettre à jour **timbres de combinaison, emplacements de Set List et Drum Tracks** (même Off).
4. Ne jamais partir d'un objet à zéro : des centaines de paramètres ont une valeur par défaut non nulle. Partir de `init_exi.bin` / `init_combi.bin` ou d'un son d'usine (`04_tests/fabrication/`).
5. Changer de type d'effet ne remet pas ses 64 octets à zéro : écrire le bloc par défaut (`Effets_blocs_par_defaut.json`, 135 types).
6. EP-1 n° 6 et SGX 72-79 n'existent qu'en 3.2.1+ ; les réglages SGX-2 au-delà de l'octet 13 du bloc, qu'en OS 3.
7. Les noms : 24 caractères latin-1 ; « Init Program », « Init Combi », « Init Combination », « Init Drum Kit », « Init Wave Sequence » = cases vides.
8. Les noms d'usine supposent une PRELOAD et un ordre (§ 10) : lire ceux du PCG de l'utilisateur.
9. Les banques EXi/HD-1 : contrôler le type avant de proposer une destination.
10. Pour comparer deux programmes HD-1, s'arrêter à l'octet 3 706 ; exclure 2688-2690 (Drum Track) si l'on compare entre OS 2 et 3.

## 14. Max for Live (Kronos Kontrol v3.2.3) : ce qui a été appris ✅ (12 oct. 2026, Live 12, Max 9)
- `.amxd` = conteneur `ampf` (u32 **petit**-boutiste) + chunk `ptch` au format `mx@c` : fichiers embarqués (patch JSON + images) et répertoire `dlst`. Un répertoire aux offsets périmés casse le device : le reconstruire entièrement (`06_max_for_live/amxd.py`, `build.py`).
- Le device se reconstruit par passes JSON (`edit_kk.py` Bank Map, menu GM, noms ; `fix2` expr ; `fix3` couleurs, ordre, encodeurs ; `fix4` GE ; `fix5` SysEx direct).
- **Max `expr` n'a pas de `if()`** : écrire en arithmétique booléenne.
- **Live ignore `frgb` des commentaires** : utiliser `textcolor`.
- **Ordre des messages** : renvoyer la banque en dernier (objets placés à droite, x élevé) après un changement de mode.
- **Le SysEx sort directement par `midiout` de la piste depuis Live 11.1** ; le routeur UDP (udpsend 7402 vers un patch externe) ne marche pas : abandonné.
- Sélection : CC0 (MSB) puis CC32 (LSB) puis Program Change (§ 3) ; KRONOS en Bank Map KORG ; SysEx autorisé ; canal global 1.
- **Le moteur audio de Live doit tourner**, sinon le device n'envoie rien.
- CC KARMA désactivés d'usine sur le KRONOS : Global › Reset Controller MIDI Assign › CC Default, puis Write.
- Liste des 3 584 GE (Preset 0-2047, USER-A…L) : `ge_kronos.json` (Voice Name List M2, p. 233-264) ; banque/numéro de GE = `/128` et `%128`.
- Noms d'usine OS 3.2 (4 233) : `names.json`. Correspondances CC des encodeurs : `docs_dev/MAX_FOR_LIVE_FORMAT.md`.
- Testé : I-B000, GM000, U-A000, CC74, passage en Combi. Non testés : g(1)…g(d), KARMA, GE, FX en SysEx.

## 15. Architecture proposée pour l'éditeur / bibliothécaire
1. **Modèle** : réutiliser `parse/build` (JS ou Python) + `model()` de pcgconvert-core.js (banques P/C/K/W, Set Lists, Global, DPI).
2. **Paramètres** : piloter l'affichage et l'édition par les tables JSON (octet, bits, largeur, plage, libellés) ; `02_python/kprog.py`/`kmap.py` montrent la lecture/écriture par nom de paramètre au bit près.
3. **Bibliothécaire** : copier/déplacer un son = copier l'objet (4 960 / 7 810 o) + mettre à jour les références (`mapRef` de pcgconvert) ; sauvegarder = recalculer les sommes et DIV1 (`div1New`).
4. **Envoi au KRONOS** : SysEx de pcgbridge (banque entière) ou Parameter Change (édition en direct, Max for Live ou WebMIDI).
5. **Versions** : `convert()` de pcgconvert pour produire le fichier de chaque OS, avec son rapport.
