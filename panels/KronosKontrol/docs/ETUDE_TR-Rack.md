# Étude du panneau TR-Rack (idiomes CTRLR)

Lecture de `..\TR-Rack-Editor-main\Tr Rack Editor.bpanelz` : zlib → ValueTree binaire JUCE → XML (2 840 modulateurs, 92 méthodes Lua).

- Callbacks du panneau : `luaPanelLoaded="initPanel"`, `luaPanelMidiReceived="receiveStatus"` (reçoit un CtrlrMidiMessage).
- Envoi : `panel:sendMidiMessageNow(CtrlrMidiMessage("f0 42 30 3B 41 … F7"))` (chaîne hexa).
- Lecture : `midiMessage:getData():getRange(5,1):toHexString(1)`, `midiMessage:getSize()`.
- Mise à jour sans renvoi : `panel:getModulatorByName("x"):getComponent():setValue(v, false)`.
- Texte : `panel:getComponent("modeBox"):setPropertyString("uiLabelText", s)`.
- Minuteries : `timer:setCallback(n, f)`, `timer:startTimer(n, ms)`.
- Image de fond : `uiPanelEditor uiPanelImageResource="nom"`, `uiPanelImageLayout="64"` (étirer) ; images stockées dans
  `resourceExportList/resource resourceData="taille.base64-JUCE"` (encodeur : `sources\jb64.py`, vérifié octet par octet).
- Commandes : `uiSlider` (RotaryVerticalDrag), `uiButton`, `uiLabel`, `uiCombo`, `uiXYSurface` ; MIDI d'un modulateur :
  `midiMessageType` 0 = CC, 5 = SysEx, 9 = aucun ; `midiMessageCtrlrNumber`, `midiMessageChannel`.
