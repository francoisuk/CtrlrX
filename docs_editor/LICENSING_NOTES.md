# Kronos Kontrol — licensing notes (to review with a lawyer before selling)

*1 Nov 2026. Not legal advice: a checklist of the facts that matter for the EULA.*

## What the VST3 actually is
`Kronos Kontrol.vst3` is produced by Ctrlr's **File › Export › Export instance**. It is a byte copy of
the Ctrlr 5.6.23 VST3 runtime (`Ctrlr-x64.vst3`) with the panel written into it as a Windows
resource (`CtrlrWindows::exportWithDefaultPanel`). So one file holds two things:

| Part | Owner | License |
|---|---|---|
| Panel: artwork, layouts, Lua, data tables, About screen | F. Rossi, Kronoscopie | your EULA (`vst3/EULA.txt`) |
| Runtime: Ctrlr, JUCE, VST3 SDK, Lua/luabind | their authors | BSD / GPL v2 (Ctrlr), GPL (JUCE as used by Ctrlr), VST3 SDK license, MIT |

## Consequences
1. The EULA can restrict the **panel content**, but not the GPL runtime: it must say the
   third‑party components keep their own licenses (EULA §3 last sentence, §6), ship their notices
   (`vst3/THIRD_PARTY_NOTICES.txt`), and offer the GPL source (the notice includes a written offer).
2. Whether the embedded panel is a separate work or a "derivative work" of the GPL runtime is the
   key legal question for **selling** the plug-in on its own. Bundled free with the book, the risk is
   low; for separate sales, get advice. A cleaner long-term route is a native JUCE/VST3 build of
   the editor under a commercial JUCE license (sources in `native/kronos-midi/`, VST3 SDK in
   `ctrlr-project/reference/VST_SDK`).
3. KORG / KRONOS are KORG Inc. trademarks: the EULA states the product is independent and not
   endorsed (§5). Product name and marketing should keep that line.
4. Ctrlr's own "License content" prompt at export embeds a text that the user must accept **each
   time the panel loads** (`CtrlrPanelResourceManager::restoreState`, modal Yes/No). For a plug-in
   that is reloaded with every DAW project this is intrusive: present the EULA at installation
   (installer / download page / first page of the book's download) and keep the copyright in the
   About screen instead. See the 1.0b test result in the journal.

## Placeholders to fill
- EULA §11 governing law (France assumed), §12 contact; notices: contact for the source offer.
- Price / reseller wording in §2.2 if sold separately.
