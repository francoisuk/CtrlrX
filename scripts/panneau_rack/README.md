# panneau_rack — dessin du panneau Kronos Kontrol (façade rack 19" 3U)

*Chemins mis à jour le 24 oct. 2026 (recolte des projets précédents).*

Python 3 + `pip install cairosvg fonttools pillow` ; polices Inter (.otf) et DejaVu Sans Mono (variable `FONT_DIR` dans `txt2path.py`).

| Fichier | Rôle |
|---|---|
| `kontrol.py` | Dessine le panneau (1500 × 414 unités) et écrit `../maquettes/kronos-kontrol-rack.svg/.png/.jpg` (créer le dossier `maquettes` à côté de `panneau_rack/`, ou adapter le chemin en bas du script). |
| `rack.py` | Briques graphiques : encodeur à anneau bleu, texte, bouton, curseur. |
| `k3vec.py` | Dessin vectoriel du KRONOS 3 (seule `screen_setlist` est utilisée par `rack.py`). |
| `txt2path.py` | Convertit les `<text>` du SVG en tracés (le SVG s'affiche partout sans les polices). |
| `fond_device.py` | Même panneau sans les parties actives (encodeurs, voyants, textes d'afficheurs, LED, croix X-Y) : `python fond_device.py fond.png` → image de fond pour Max (ou CTRLR) sur laquelle on pose les vraies commandes. Le `rack_fond.png` livré est dans `panels/KronosKontrol/`. |

L'art finalisé est conservé dans `GUI_pic/panneau_rack/` (`kronos-kontrol-rack.png` / `.svg`) et `GUI_pic/` (`kronos-kontrol-rack-final.svg` / `.png`) — ne pas le régénérer sans raison.

Coordonnées de chaque commande (1 unité = 1 pixel dans la fenêtre du device) : `panels/KronosKontrol/LISEZMOI_panneau.md` (notes de design, en français) et, dans l'original du projet vst3, la section 5 de `max_for_live/fix6.py` (fonction `at(objet, x, y, largeur, hauteur)`) — ce fichier n'est pas repris dans ce projet ; l'original reste dans `C:\Korg\Manuals Le grand livre du KRONOS\04_Outils\produits-inclus\`.

Le rack est maintenant implémenté comme panneau CTRLR : `panels/KronosKontrol/KronosKontrol.panel` (généré par `panels/KronosKontrol/sources/build_panel.py`).
