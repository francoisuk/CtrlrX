# Prompt — reprise du panneau CTRLR « Kronos Kontrol » (lundi 19 oct. 2026)

> **Mise à jour du 24 oct. 2026 — la « première tâche » (§ 4) est FAITE.**
> Les corrections de complet-0.96 sont préparées dans le panneau (mémoire
> de mode + renvoi 4E, GE en fn 6D, Drum Track On en fn 6E, TYP 1 en Combi,
> affichage des codes Reply 24, décodage 6D/6E). **Il reste à les tester sur
> le KRONOS** (plan en 5 points à la fin de `REPRISE.md`). `parameter_map.csv`
> (124 lignes) et `PROJECT_LAYOUT.md` sont à jour. Les chemins
> `04_Outils\bonus\VST3\` de ce prompt sont historiques : tout est dans
> `C:\Korg\kronos-corpus\ctrlr-project`.
>
> **Mise à jour du 24 oct. 2026 (soir) — phase éditeur.** complet-0.96 est en
> test auteur. Le panneau est passé en **complet-0.97** (onglets RACK/EDIT,
> étape E1 de l'éditeur : lecture du dump Programme, requête 4A / réception
> 4B, conversion 7 bits). Vérification statique faite ; **test KRONOS à
> faire** : `EDITOR_PLAN.md` § 9, résultats dans `REPRISE.md` (section
> « complet-0.97 »). Plan E1-E7 : `EDITOR_PLAN.md`. Prochaine étape après le
> test : E2 (édition + renvoi dans le tampon d'édition).

Bonjour. On reprend le panneau CTRLR Kronos Kontrol. Français, phrases courtes, petites étapes testées (crédits limités).

1. Demande l'accès à `C:\Korg\Manuals Le grand livre du KRONOS`, `C:\Korg\Manuals Kronos 3.2.x` et `C:\Korg\Manuals Kronos 3.1.4`
   (documentation : MIDI Implementation, Param Guide ; textes extraits dans `03_References_texte\`).
2. Lis `04_Outils\bonus\VST3\panels\KronosKontrol\REPRISE.md` (état et pistes), puis `..\..\PROMPT_NOUVELLE_SESSION_CTRLR.md`
   (règles : il fait foi), `ETUDE_TR-Rack.md`, `lua\kkMain.lua`, `sources\build_panel.py`.
3. Rappels techniques (vérifiés dans les sources Ctrlr, voir REPRISE) :
   - Ctrlr appelle un callback par le NOM de méthode : dans `kkMain.lua`, chaque `--@ nom` ouvre une méthode.
   - Envoi : `panel:sendMidiMessageNow(CtrlrMidiMessage("hex"))` — chaîne hexa (pas de table d'octets).
   - `setValue(v, false)` = mise à jour sans renvoi (garde anti-boucle native).
   - Sources Ctrlr : `git clone --depth 1 https://github.com/RomanKubiak/ctrlr.git` et `.../dnaldoog/CtrlrX.git`
     (le dossier `build\` du PC est trop profond pour être lu à distance).
   - Reconstruire : `python sources\build_panel.py` (ou dans l'espace de travail de Claude, puis recopier le .panel).
4. **Première tâche** : lire « Test de l'auteur — 16 oct., 18 h 30 » dans REPRISE.md, puis, dans l'ordre :
   a. modes Global / Disk / Sequencer : renvoyer 4E avant la sélection de Program / Combi (voir REPRISE) ;
   b. KARMA et Drum Track : comparer octet par octet avec le device Max for Live (`kronos_kontrol_v1.json`, sxformat),
      ajouter dans l'afficheur le code de Reply 24, rappeler à l'auteur le réglage « Reset Controller MIDI Assign › CC Default » ;
   c. ensuite : lecture de l'état du KRONOS au chargement, export VST3, modes d'emploi FR/EN/ES ;
      mise à jour de `parameter_map.csv` et `PROJECT_LAYOUT.md` (§ 4 du prompt).
5. Un seul auteur à la fois sur `lua\kkMain.lua` et `sources\build_panel.py` (le 16 oct., deux versions se sont mélangées).
6. Tout le nécessaire est aussi rassemblé dans `04_Outils\bonus\VST3\export\` (voir son README.md).
