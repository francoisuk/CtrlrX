# Compatibilité des fichiers PCG entre KRONOS 1, KRONOS X, KRONOS 2 et KRONOS 3

*Le grand livre du KRONOS — document technique interne (6 octobre 2026)*

Sources de ce document :
- l'analyse octet par octet des PCG d'usine Korg (OS 1, OS 2, OS 3.1, OS 3.2, KRONOS X) : voir `04_Outils/PCG/data/04_Analyses_usine` ;
- la reconstruction à l'identique (à l'octet près) des 6 PCG d'usine par nos scripts (`03_Scripts`) ;
- le code source de **PCG Tools** (`04_Outils/coding/PcgTools2013-master.zip`). Fichiers clés : `KronosPcgFileReader.cs`, `KronosPcgMemory.cs`, `PcgFileReader.cs`, `KronosProgram.cs`, `KronosSetListSlot.cs` ;
- la documentation MIDI de Korg (`04_Outils/PCG/data/01_MIDI_implementation_Korg`).

Le détail de chaque paramètre est dans `04_Outils/PCG/data/00_RECAPITULATIF_FORMAT_PCG.md`. Ce document-ci répond à une autre question : **qu'est-ce qui change d'un KRONOS, ou d'un OS, à l'autre, et comment produire le bon fichier ?**

---

## 1. L'idée essentielle

> **Ce n'est pas le modèle qui compte, c'est la version de l'OS.**

- Un PCG ne contient **aucune information sur le matériel**. Il indique seulement la **génération d'OS** qui l'a écrit.
- Un KRONOS 1 mis à jour en OS 3.1.4 écrit et lit **exactement** les mêmes PCG qu'un KRONOS 2 en OS 3.1.4.
- Le KRONOS X n'est pas un format à part. C'est un KRONOS avec plus de mémoire, qui écrit les PCG de son OS. Le fichier `PRELOAD_KRONOSX.PCG` existe pour une autre raison : la **répartition des types de banques** (EXi ou HD-1) n'est pas la même (voir § 7).

| Modèle | OS d'origine | OS le plus récent possible |
|---|---|---|
| KRONOS (1re génération, 2011) | 1.0 | **3.1.4** |
| KRONOS X | 2.x | **3.1.4** |
| KRONOS 2 (2015) | 3.0 | **3.1.4** |
| KRONOS 3 (2025) | 3.2 | 3.2.x |

Par conséquent, en 2026, le parc réel se partage en **deux cibles** :
- **OS 3.1.4** pour les KRONOS 1, X et 2 à jour ;
- **OS 3.2.x** pour le KRONOS 3 (et tout KRONOS qui recevrait un jour l'OS 3.2.1 ou plus récent).

C'est pourquoi le livre fournit `LIVRE_KRONOS_OS314.PCG` et `LIVRE_KRONOS_K3.PCG`. Les KRONOS restés en OS 1 ou 2 sont un cas d'école, mais il faut savoir les reconnaître (§ 4 et § 5).

---

## 2. Où se lit la version : l'en-tête de 16 octets

```
4B 4F 52 47  68  00  02  <osv>  01  00 00 00 00 00 00 00
 K  O  R  G  ID KRONOS  type PCG  |
                                  └ octet 7 = génération d'OS
```

| Octet 7 (`osv`) | Génération | PCG Tools (`EOsVersion`) |
|---|---|---|
| `00` | OS 1.0 / 1.1 | `Kronos10_11` |
| `00` + blocs INI2/INI3 ou XXX2 | OS 1.5 / 1.6 | `Kronos15_16` |
| `01` | OS 2.x | `Kronos2x` |
| `02` | OS 3.0 à 3.2.x | `Kronos3x` |

- PCG Tools lit `content[7]` dans `KronosPcgFileReader`. Il ne peut pas distinguer OS 1.0 et OS 1.5/1.6 par l'en-tête : il bascule en `Kronos15_16` **dès qu'il rencontre** un bloc `INI2`/`INI3` ou un bloc « 2 » (`PRG2`, `CMB2`, `STL2`, `DKT2`, `WSQ2`) (`PcgFileReader.cs`, lignes 87 à 132).
- **OS 3.0, 3.1 et 3.2 portent tous `02`.** L'en-tête ne permet pas de les distinguer. Seules les **valeurs** à l'intérieur diffèrent (§ 6).

---

## 3. Le squelette commun à toutes les versions

Le principe est le même pour tous les OS :

- **En-tête** de 16 octets.
- **Blocs** (chunks) : `ID (4 octets) | taille du corps (u32, big-endian) | champ (u32) | corps`.
  - Pour un **conteneur**, le champ vaut `version << 16 | 0x0400`.
  - Pour une **banque** et pour `GLB1`, le champ vaut `version << 16 | somme8`. La somme8 est la somme de **tous** les octets du corps, catalogue de 12 octets compris, modulo 256. PCG Tools la recalcule dans `FixChecksumValues` (offset +11).
- **`DIV1`** (44 octets) : pour chaque type d'objet, `[masque bas, nb, masque haut, nb]`, terminé par `ffff 0000`. Le nb vaut `0x15` pour les programmes, `0x0E` pour les combinaisons et `0x0F` pour les kits et les séquences d'ondes. Les Set Lists absentes sont codées `0000 0000`.
- **Numérotation des banques** : I-A à I-E = 0 à 4, I-F = `0x8000`, U-A à U-GG = `0x20000` à `0x2000D`.

Ce squelette **n'a pas changé** de l'OS 1 à l'OS 3.2. Ce qui change, ce sont :
1. les **numéros de version** des banques ;
2. la **taille ou le contenu** de certains objets ;
3. en OS 1.5/1.6 seulement, une **structure en deux morceaux** (§ 4.2).

---

## 4. OS 1.x : deux formats différents

### 4.1 OS 1.0 / 1.1 : le format d'origine

- `osv = 00`, uniquement des blocs « 1 » (`PRG1`, `CMB1`, `DKT1`, `WSQ1`, `GLB1`).
- Les objets sont **plus petits** qu'en OS 2 (tableau du § 5).
- **Référence à une séquence d'ondes** dans un oscillateur : 2 octets séparés, l'un pour la banque et l'autre pour le numéro. Les banques utilisateur sont codées à partir de `0x40` (`0x40` à `0x46` = U-A à U-G). Voir `KronosProgram.cs`, ligne 273.

### 4.2 OS 1.5 / 1.6 : le format « en deux morceaux »

Korg a ajouté des paramètres sans pouvoir agrandir les objets `PRG1`/`CMB1`. Les **compléments** ont donc été mis dans des **blocs parallèles** :

- `INI2` / `INI3` (puis `INI1`) : des blocs d'index et d'information.
- `PRG2`, `CMB2`, `DKT2`, `WSQ2`, `STL2` : des banques jumelles, qui contiennent la suite des paramètres de chaque objet.
- Un programme est donc réparti entre `PBK1/PRG1` (le gros des paramètres) **et** `PBK2/PRG2` (les ajouts). PCG Tools le gère explicitement : quand il copie un programme en `Kronos15_16`, il recopie aussi le contenu de `PRG2` via `GetParameterOffsetInPbk2` (`KronosPcgMemory.cs`, lignes 203 et 262).
- **Sommes de contrôle** : en plus de la somme de chaque banque, la somme est **aussi écrite dans `INI2`**, à l'offset +54. Si l'une des deux est fausse, le fichier est refusé.
- Les **Set Lists** (apparues en OS 1.5) ont des offsets propres à ce format (`KronosSetListSlot.cs`, lignes 213 et 333 à 380).
- **`INIT.PCG`** (dans `FACTORY`) est dans ce format. C'est un piège classique : le fichier a l'air d'être de l'OS 1, mais il ne se lit pas comme un PRELOAD OS 1.0.

> **À retenir.** Le format OS 1.5/1.6 est une **impasse historique**. L'OS 2 a fusionné les deux morceaux dans des objets agrandis. Il ne faut **jamais** fabriquer un fichier dans ce format aujourd'hui.

---

## 5. OS 2 : le grand changement

L'OS 2 est la **seule rupture importante** du format. Tout ce qui a été écrit après se lit de la même façon.

### 5.1 Versions des objets

| Banque / objet | OS 1 | OS 2 | OS 3 |
|---|---|---|---|
| `MBK1` (conteneur) | v3 | v5 | v5 |
| `PBK1` (programmes) | v4 | v5 | v5 |
| `CBK1` (combinaisons) | v3 | v3 | v3 |
| `DBK1` (kits de batterie) | v2, 22 040 o | **v3, 38 424 o** | v3 |
| `WBK1` (séquences d'ondes) | v0, 1 192 o | **v1, 2 216 o** | v1 |
| `GLB1` (Global) | v1 | v1 | **v2** |

### 5.2 Ce qui change à l'intérieur d'un programme

- **Moteurs identiques** entre OS 1 et OS 2 : **AL-1, MS-20EX, PolysixEX, EP-1**. Leurs paramètres restent aux mêmes offsets.
- **Moteurs modifiés** : **MOD-7, STR-1, SGX et CX-3**, ainsi que **tout le HD-1** (ajouts de paramètres et nouvelles plages).
- **Séquences d'ondes** : la référence passe de 2 octets séparés (banque, numéro) à **un index unique sur 2 octets** (`KronosProgram.cs`, lignes 288 à 296). Les banques de séquences d'ondes et de kits grandissent, d'où les nouvelles tailles de `DBK1` et `WBK1`.
- Les ajouts de l'OS 1.5/1.6 (anciens `PRG2`…) sont **intégrés** dans les objets « 1 ». Les blocs « 2 » disparaissent.

### 5.3 Conversion au chargement

- **Vers le haut, tout se convertit.** Un KRONOS en OS 2 ou 3 charge un PCG d'OS 1 et le **convertit** en mémoire. Les paramètres absents prennent leur valeur par défaut. Les références aux séquences d'ondes et aux kits sont recalculées.
- **Les OS anciens (jusqu'à 2.1) proposent une option de remappage** des références lors du chargement d'un PCG partiel. Sur les OS récents, la correction des références est automatique quand on charge ensemble les banques et les combinaisons qui s'y réfèrent.
- **Vers le bas, rien ne se convertit.** Un KRONOS en OS 1 ne lit pas un PCG d'OS 2 ou 3 : il ne connaît ni les nouvelles versions de banques ni les nouvelles tailles.

---

## 6. OS 3.0 → 3.1 → 3.2 : un même format, de nouvelles valeurs

### 6.1 OS 2 → OS 3

- `osv` passe de `01` à `02`.
- `GLB1` passe en **v2**.
- Dans un programme, **seuls les octets 2688-2689 changent de sens** : c'est le **Drum Track Program**. Les kits d'usine utilisés par le Drum Track passent de la banque **I-F** à la banque **U-BB**. Un programme OS 2 dont le Drum Track pointe vers I-F doit être corrigé pour pointer vers l'emplacement OS 3.
- Tout le reste des programmes et des combinaisons est **identique à l'octet près**.

### 6.2 OS 3.1 → OS 3.2 : aucun changement de format

Ni l'en-tête, ni les versions, ni les tailles ne changent. Seules **de nouvelles valeurs** deviennent légales :

| Élément | Valeurs OS 3.1.4 | Valeurs OS 3.2.x |
|---|---|---|
| **EP-1 Model 6** | Reed EP 200A | **Tine EP I Early** (OS 3.2.1 et plus) |
| **SGX-2 Piano Type** | jusqu'à 71 | **72 à 79** (nouveaux pianos) |
| **Effets** (type) | jusqu'au n° 197 | jusqu'au n° 197 (aucun nouveau type) |
| **Banques de programmes de la PRELOAD** | jusqu'à U-BB | **U-CC, U-DD, U-EE** en plus (17 banques au total) |
| **Banques de combinaisons de la PRELOAD** | 4 | **6** |

Conséquences :
- **Un PCG OS 3.1.4 se charge tel quel sur un KRONOS 3.**
- **Un PCG OS 3.2 se charge sur un OS 3.1.4** (même en-tête, même structure). Mais :
  - un EP-1 réglé sur **Tine EP I Early** sonnera avec le **Reed EP 200A**, la valeur 6 n'ayant pas le même sens ;
  - un SGX-2 réglé sur un **Piano Type de 72 à 79** fait référence à des échantillons absents : son incorrect ou muet ;
  - une combinaison qui appelle un programme des banques **U-CC, U-DD ou U-EE** de la PRELOAD 3.2 tombera sur un programme vide ou différent.
- **La compatibilité dépend donc du contenu, pas du fichier.** C'est exactement la seule différence entre les deux PCG du livre : `LIVRE_KRONOS_K3.PCG` contient en plus « EP-1 Soul Ballad Early » (U-G 066).

---

## 7. Banques EXi, banques HD-1 et le KRONOS X

- Chaque banque utilisateur de programmes est **typée** : **EXi** (programmes EXi de 4 960 octets) ou **HD-1** (programmes HD-1, 3 706 octets utiles dans une case de 4 960).
- Le type est enregistré dans le fichier, banque par banque. On ne peut charger un programme EXi dans une banque HD-1, ni l'inverse.
- `PRELOAD_KRONOSX.PCG` a **le même contenu** que la PRELOAD standard, avec **une autre répartition** des types de banques, adaptée à la configuration du KRONOS X. Si l'on veut que les combinaisons d'usine fonctionnent, il faut charger la PRELOAD qui correspond à **son** instrument.
- Pour le livre : U-G est une banque **EXi**, U-GG une banque **HD-1**. L'utilisateur doit charger chacune dans une banque **du même type**.

---

## 8. Tableau de compatibilité (charger le fichier X sur la machine Y)

| PCG écrit par ↓ / chargé sur → | OS 1.0/1.1 | OS 1.5/1.6 | OS 2.x | OS 3.1.4 (K1, X, K2) | OS 3.2.x (K3) |
|---|---|---|---|---|---|
| **OS 1.0/1.1** | ✅ | ✅ conversion | ✅ conversion | ✅ conversion | ✅ conversion |
| **OS 1.5/1.6** | ❌ | ✅ | ✅ conversion | ✅ conversion | ✅ conversion |
| **OS 2.x** | ❌ | ❌ | ✅ | ✅ (Drum Track à vérifier) | ✅ (Drum Track à vérifier) |
| **OS 3.0/3.1** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **OS 3.2** | ❌ | ❌ | ❌ | ⚠️ se charge, valeurs 3.2 mal interprétées | ✅ |

✅ = fonctionne · ⚠️ = fonctionne avec réserves · ❌ = refusé ou illisible.

---

## 9. Passer d'un format à l'autre

### 9.1 Vers le haut (le plus fréquent) : laisser faire le KRONOS

1. Copier l'ancien PCG sur une clé USB.
2. Le charger sur le KRONOS récent (mode Disk → Load). Le KRONOS **convertit** en mémoire.
3. **Vérifier** les programmes MOD-7, STR-1, SGX, CX-3 et HD-1 (moteurs modifiés en OS 2), ainsi que le Drum Track des programmes venus d'OS 2.
4. Faire un **Save All** : le fichier réécrit est au format de l'OS courant.

### 9.2 Vers le bas : le reconstruire

Aucun KRONOS ne sait « rétrograder » un PCG. Il faut **reconstruire** le fichier :
- **OS 3.2 → OS 3.1.4** (le seul cas utile aujourd'hui) :
  1. remplacer EP-1 Model 6 = Tine EP I Early par un modèle existant en 3.1.4 ;
  2. ramener les Piano Type SGX-2 de 72 à 79 sur un piano de 0 à 71 ;
  3. vérifier qu'aucune combinaison n'appelle U-CC, U-DD ou U-EE ;
  4. l'en-tête, les versions et les sommes ne changent pas.
- **OS 3 → OS 2** : remettre le Drum Track vers I-F (octets 2688-2689), puis passer `GLB1` en v1 et `osv` en `01`. À réserver à un besoin réel.
- **OS 2 → OS 1** : déconseillé. Il faudrait réécrire les objets MOD-7, STR-1, SGX, CX-3 et HD-1, réduire les banques de kits et de séquences d'ondes, recoder les références, puis repasser aux versions du § 5.1.

### 9.3 Ce que fait PCG Tools

- Il **lit** les quatre familles (`Kronos10_11`, `Kronos15_16`, `Kronos2x`, `Kronos3x`), affiche les noms, les catégories et les références, et permet de **copier-coller** des programmes ou des combinaisons **entre fichiers de même génération**.
- Il **recalcule** les sommes de contrôle à l'enregistrement : offset +11 de chaque banque et, en OS 1.5/1.6, offset +54 de `INI2`.
- Il gère le format en deux morceaux de l'OS 1.5/1.6 (copie conjointe de `PRG1` et `PRG2`) et la double façon de référencer les séquences d'ondes.
- Il **ne convertit pas** d'une génération à l'autre : il n'y a ni migration des moteurs modifiés en OS 2 ni correction du Drum Track. Pour monter de version, c'est le KRONOS qui convertit (§ 9.1).

---

## 10. Fabriquer un PCG pour une cible donnée (avec nos scripts)

Le dossier `04_Outils/PCG/data/03_Scripts/fabrication/` contient la chaîne complète (`livre_lib.py`, `recettes_*.py`, `build_livre.py`).

### 10.1 Méthode générale

1. **Partir d'un PCG d'usine de la génération visée**, qui sert de gabarit : `FACTORY_V3.2/.../PRELOAD.PCG` pour le KRONOS 3, `FACTORY_V3.1/PRELOAD.PCG` pour l'OS 3.1.4. On hérite ainsi de l'en-tête, des versions de banques, de `GLB1` et de la structure exacte.
2. **Partir d'un objet vierge de la même génération** pour chaque son : `init_exi.bin` (4 960 o), `init_combi.bin` (7 810 o), INIT HD-1.
3. **Écrire les paramètres** aux offsets du récapitulatif, en respectant les énumérations **de la cible** (§ 6.2).
4. **Assembler** les banques voulues, avec le bon `DIV1` (masques, nombre d'éléments, Set Lists à `0000 0000` si absentes).
5. **Recalculer** la somme8 de chaque banque et de `GLB1`.
6. **Relire** le fichier avec `pcgreader` / `kpcg` et le contrôler : pas de valeur hors limites, noms de 24 caractères au plus, statut des timbres INT = 1, banques de timbres codées 0-5 INT, 6-16 GM et 17-30 utilisateur.

### 10.2 Cible par cible

| Cible | Gabarit | `osv` | Points d'attention |
|---|---|---|---|
| **KRONOS 3 / OS 3.2.x** | PRELOAD 3.2 | `02` | Toutes les valeurs 3.2 sont permises (EP Early, SGX-2 72-79, U-CC à U-EE). |
| **KRONOS 1, X, 2 en OS 3.1.4** | PRELOAD 3.1 | `02` | Pas de Tine EP I Early ; SGX-2 ≤ 71 ; combinaisons limitées aux banques ≤ U-BB. |
| **OS 2.x** | PRELOAD V2 | `01` | `GLB1` v1 ; Drum Track vers I-F. |
| **OS 1.0/1.1** | PRELOAD OS 1 | `00` | Objets OS 1 (MOD-7, STR-1, SGX, CX-3, HD-1 différents) ; références WSQ par octets séparés ; `DBK1` v2, `WBK1` v0. Non outillé. |
| **OS 1.5/1.6** | INIT.PCG | `00` + INI2/INI3 | Format en deux morceaux, double somme de contrôle. **À éviter.** |

### 10.3 Ce qui a été vérifié

- Les 6 PCG d'usine (OS 1, OS 2, OS 3.1, OS 3.2, KRONOS X, EXs) sont **reconstruits à l'octet près** par nos scripts.
- Les deux PCG du livre (2 269 620 octets chacun) ont **la même structure** que les PCG EXs de Korg et KRS-06.
- 5 634 réglages relus, 0 valeur hors limites.
- **Reste à faire** : l'essai au clavier sur un vrai KRONOS (OS 3.1.4 et OS 3.2).

---

## 11. Aide-mémoire

- **Une seule question à se poser : quel OS ?** Le modèle de KRONOS ne compte pas.
- `osv` = 0, 1 ou 2. La présence de INI2/INI3 ou de blocs « 2 » signale l'OS 1.5/1.6.
- **OS 2 = la rupture.** OS 3 = Drum Track et GLB v2. OS 3.2 = de nouvelles valeurs seulement.
- **Vers le haut** : le KRONOS convertit. **Vers le bas** : il faut reconstruire.
- **En 2026** : deux fichiers suffisent, un pour l'OS 3.1.4 (KRONOS 1, X, 2) et un pour l'OS 3.2 (KRONOS 3).
