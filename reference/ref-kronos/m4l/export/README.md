# Kronos Kontrol — export des outils (pour réutilisation, p. ex. un panneau CTRLR)

*Export du 16 octobre 2026. Auteur : François Rossi (« Le grand livre du KRONOS »). Destinataire : un nouveau projet
(humain ou Claude) qui veut piloter un **Korg KRONOS (OS 3.x)** en MIDI / SysEx, par exemple avec **CTRLR**.*

Ce dossier rassemble tout ce qui a servi à fabriquer le device Max for Live **Kronos Kontrol OS3.2.3**
(FR / EN / ES), **testé et fonctionnel** dans Ableton Live 12 avec un KRONOS le 16 oct. 2026. Il contient :
1. une **bibliothèque SysEx autonome** (Python et Lua) — le point de départ pour un autre projet ;
2. les **scripts qui construisent le device** Max for Live (référence, technique réutilisable) ;
3. les **scripts qui dessinent le panneau** rack (maquette SVG/PNG) — réutilisables pour un fond de panneau CTRLR ;
4. la **documentation** du projet.

## 1. Par où commencer

| Je veux… | Fichier |
|---|---|
| Fabriquer / décoder les messages du KRONOS (référence la plus sûre) | `kronos_sysex.py` (lancer `python kronos_sysex.py` : auto-test) |
| Les mêmes fonctions dans CTRLR | `ctrlr/kronos_sysex.lua` |
| La liste des messages, leur format et leur état de test | `SYSEX_KRONOS.md` |
| Comprendre comment le device Max for Live est construit | `max_for_live/README.md`, `docs/REPRISE_device.md` |
| Réutiliser le dessin du panneau | `panneau_rack/README.md`, `docs/LISEZMOI_panneau.md` |
| Le mode d'emploi utilisateur du device | `docs/LISEZMOI_device.txt` (et les guides Word dans `..\Manuels\`) |

## 2. L'essentiel à savoir sur le KRONOS (vérifié)

- **En-tête SysEx** : `F0 42 3g 68` (Korg, canal global g = canal − 1, modèle KRONOS 0x68). Le M3 utilise 0x75 : un message
  M3 ne marche pas sur le KRONOS en changeant seulement l'octet de modèle — les identifiants de paramètres diffèrent.
- **Parameter Change (fonction 43)** : `F0 42 30 68 43 TYP SOC SUB PID IDX vH vM vL F7`. Les identifiants TYP/SOC/SUB/PID/IDX sont dans
  les tables du MIDI Implementation (`C:\Korg\Manuals Kronos 3.2.x\KRONOS_MIDIimp.zip` : `CombiAndSongTimbreSet.txt`,
  `Prog_HD-1.txt`, `Prog_EXi_Common.txt`, `Global.txt`…). Valeur sur 21 bits en complément à 2, 7 bits par octet.
- Le paramètre agit **dans le mode en cours** : un paramètre de Combi n'est accepté qu'en mode Combi (sinon Reply 24, code 1).
- **Interrupteurs d'effets** : la table les marque « → bypass, Invert Value » : **envoyer 1 − état** (1 = effet coupé). Vérifié.
- **Mode Change (4E)** : 0 = Combination, 2 = Program. **Mode Request (12)** → le KRONOS répond **Mode Data (42)**.
- **Banque / programme** : CC0 (MSB), CC32 (LSB), puis Program Change, avec la **Bank Map KORG** (`kronos_sysex.BANKS`).
- Réglages du KRONOS : GLOBAL › Bank Map KORG ; Enable Exclusive ; canal global 1 ; pour KARMA en CC :
  Reset Controller MIDI Assign › CC Default (les CC KARMA sont « Off » d'usine).
- Le KRONOS **envoie** lui aussi des 43 quand on touche un paramètre (et 4E quand on change de mode) : `parse()` les décode,
  ce qui permet à un panneau de suivre l'instrument.
- Aucune de ces commandes n'écrit dans la mémoire du KRONOS (pas de Write / Store) : seule la mémoire d'édition change.

## 3. Arborescence

```
export/
├─ README.md               ce fichier
├─ SYSEX_KRONOS.md         tous les messages utilisés, format, identifiants, état (testé / documenté)
├─ kronos_sysex.py         bibliothèque Python autonome (+ envoi/écoute avec mido, facultatif)
├─ ctrlr/kronos_sysex.lua  équivalent Lua pour CTRLR
├─ max_for_live/           construction du device (.amxd) — voir son README
├─ panneau_rack/           dessin du panneau (SVG/PNG, texte en tracés) — voir son README
└─ docs/                   notes de développement, lisez-moi du device et du panneau
```

## 4. Pour un panneau CTRLR (pistes)

- Un modulateur CTRLR peut envoyer un SysEx « brut » : dans le champ *MIDI › SysEx formula*, la forme
  `F0 42 30 68 43 04 00 00 02 00 00 00 xx F7` (xx = valeur 0–127) convient pour les valeurs 0–127 (vH = vM = 0).
  Pour les valeurs > 127 ou négatives (n° de GE, détune…), passer par la fonction Lua `kronosParam()`.
- Pour les interrupteurs d'effets, utiliser `kronosFxSwitch()` (valeur inversée).
- Pour suivre le KRONOS, brancher `kronosOnMidi()` sur « Called when a panel receives a midi message ».
- Le fond du panneau peut être produit par `panneau_rack/fond_device.py` (image 1500 × 414 sans les parties actives),
  puis chargé comme image de fond du panneau CTRLR ; les coordonnées des commandes sont dans `docs/LISEZMOI_panneau.md`.
