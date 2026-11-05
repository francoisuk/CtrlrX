La fonction « MIDI Learn » dans un VST créé avec **Ctrlr** ne marche pas comme sur un synthé logiciel classique. Ctrlr **n’a pas de bouton MIDI Learn universel intégré** : c’est surtout **ton DAW** qui fournit l’apprentissage MIDI. Tu peux quand même assigner des contrôleurs MIDI à tes paramètres Ctrlr, mais ça se joue à deux niveaux : le **panel Ctrlr** et **l’hôte**.

---

### 1. Ce que fait Ctrlr

Ctrlr sert à créer des **panels** : des interfaces de contrôle pour un synthé matériel ou des paramètres MIDI. Tu peux charger ces panels **comme un plugin VST/AU** dans un DAW. Une fois chargé en VST, chaque contrôle du panel — bouton, fader, knob — apparaît au DAW comme un **paramètre VST automatisable**. C’est ce mécanisme qui rend le MIDI Learn possible, mais de façon indirecte.

---

### 2. Le MIDI Learn vient du DAW, pas de Ctrlr

Un utilisateur sur Gearspace le résume bien :

> « you can control a plugin parameter with MIDI Learn **if your host supports**. in that case, the parameter is identified within the plugin by 'VST Index', and mapped to the MIDI CC# you choose. »

Concrètement :
- Ctrlr **n’a pas de MIDI Learn interne** dans sa version VST.
- Ton DAW voit les paramètres de Ctrlr comme des paramètres VST normaux, avec un **index VST**.
- La fonction « MIDI Learn » de ton DAW — Cubase, Ableton Live, Logic, Reaper, etc. — peut alors lier un contrôleur MIDI physique (CC#) à un paramètre Ctrlr précis.
- Ça marche bien pour **quelques paramètres en temps réel**, mais c’est peu pratique pour un panel avec des centaines de contrôles, comme un patch complet de TX7.

---

### 3. Alternative : assigner les CC directement dans le panel Ctrlr

Si tu crées toi-même le panel, tu peux **préconfigurer des numéros de CC MIDI** sur les modulators — les contrôles — directement dans l’éditeur Ctrlr. Certains panels téléchargeables intègrent déjà ces assignations :

> « All buttons associated to a Midi CC controller number so you can adjust them from a hardware controller »

Dans ce cas, ce n’est pas du « MIDI Learn » dynamique, mais une **assignation fixe** définie à l’avance. C’est souvent plus fiable pour des panels complexes, parce que chaque contrôle sait déjà quel CC écouter.

---

### 4. En résumé pratique

| Aspect | Ctrlr VST seul | DAW hôte avec MIDI Learn | Panel Ctrlr avec CC fixes |
|---|---|---|---|
| **MIDI Learn intégré ?** | ❌ Non | ✅ Oui, si ton DAW le propose | ❌ Non, mais CC pré-assignés |
| **Mécanisme** | Expose les paramètres comme VST Index | Mappe un CC à un paramètre VST via l’apprentissage | Chaque modulator écoute un CC défini à la création |
| **Idéal pour** | — | Quelques macros, réglages rapides | Contrôle complet d’un panel, mappings reproductibles |
| **Limites** | Dépend du DAW | Peu pratique pour des panels très fournis | Il faut éditer le panel pour changer les CC |

**Donc, pour utiliser le MIDI Learn avec un VST Ctrlr :** charge le panel dans ton DAW, utilise la fonction **« MIDI Learn » de ton DAW** sur le paramètre Ctrlr voulu, puis bouge le contrôleur physique. Si tu veux un contrôle plus complet sans passer par l’apprentissage du DAW, pré-assigne des CC dans le panel Ctrlr dès sa conception.