# Ableton + Max for Live Kronos project — resume notes

Updated: 2026-10-07
Workspace: `C:\Korg\Ableton_Max`

## Goal
Create two native Ableton artifacts for a Korg KRONOS running OS 3.2.2:
1. A simple Ableton Instrument Rack (`.adg`) containing an External Instrument for MIDI/audio routing. No extra rack macros in this first pass.
2. A Max for Live MIDI Effect (`.amxd`) for selecting Kronos Programs and Combis and sending the continuous controller messages listed in `MAX_FOR_LIVE_FORMAT.md`.

## User-confirmed setup
- Kronos OS: 3.2.2.
- KRONOS Global MIDI channel: 1.
- Use all Program banks and all Combi banks.
- MIDI port/channel: factory-default port, channel 1 (confirm exact port name in Live after installation).
- Target: current Ableton Live and Max for Live releases.
- Selector covers Programs and Combis, all banks.
- Continuous controls: all those listed in `MAX_FOR_LIVE_FORMAT.md`.
- First `.adg`: routing only, with patch selection handled by Max for Live. Consider extra rack macros only after this works.

## Folder findings
- `ABLETON_ADG_FORMAT.md` and `MAX_FOR_LIVE_FORMAT.md` are the two root format/design notes.
- `_outils\pcgreader` reads KRONOS PCG files and makes DAW patch-name exports. `_outils\pcgbridge` builds on it and also exports SysEx.
- The user confirmed `pcgreader` and `pcgbridge` have been fully tested and work; treat them as trusted existing tools, don't spend time revalidating them.
- `noms_de_sons` contains the OS 3.2 patch-name exports. Use a user PCG if the device needs the user's current/custom patch names instead of factory names.
- Other content includes PCG reader/bridge web assets and Kronos engine reference PDFs; these aren't necessary to implement the first pass.

## Important implementation notes
- Current Cycling '74 docs: https://docs.cycling74.com/userguide/m4l/live_midieffects/ and https://docs.cycling74.com/userguide/m4l/live_limitations/ . The older Max 7 page previously referenced in chat is legacy; use the current docs.
- Build the patch from Live's Max MIDI Effect template. In Max for Live, MIDI passes between Live and the device; pass incoming MIDI downstream with `midiin` -> `midiout`. `ctlout`/`pgmout` are standard Max MIDI objects and are not inherently invalid, but confirm generated CC/Program Change messages route through the M4L device to the downstream External Instrument, not through standalone Max MIDI drivers.
- Bank-value mismatch to resolve against the actual Kronos Bank Map: the root Ableton guide says CC0/MSB 63 for internal/user Programs, while the tested exporter config in `_outils\pcgreader\pcgreader.py` currently uses CC0=0 with bank-specific CC32 values. Kronos supports KORG and GM(2) bank maps. User's “factory default” answer was specifically about the MIDI port; it did not confirm the KRONOS Bank Map. Check Global P0 / Bank Map on the instrument (or confirm it with user) before choosing bank values. Keep Program Change ordering and values consistent with the actual Kronos.
- `MAX_FOR_LIVE_FORMAT.md` lists these CCs: 74 cutoff, 71 resonance, 73 amp attack, 72 amp release, 70 variation/EG intensity, 1 mod wheel, 11 expression, 16 ribbon, 118/119 vector joystick X/Y, 64 damper, 7 volume, 10 pan, 91 reverb send, 93 chorus send, 14 KARMA on/off, 31 KARMA latch, and 102–109 KARMA switches. Confirm practical Kronos assignments during hardware verification.
- Native `.adg` and `.amxd` should be saved using Live/Max once installed, then loaded and checked in Live. Test the patch selector through the Live MIDI chain and confirm actual Kronos response. Test audio return only after the user's audio interface and Kronos input pair are available.

## Current status / resumption
- The user confirmed that the KRONOS Bank Map is **KORG** for the first implementation; add GM2 support later as a second bank-map option.
- Audio-return input pair is still unknown; do not guess the interface inputs.

## Resumed 2026-10-07 after installation
- Confirmed installation paths: Live at `C:\ProgramData\Ableton\Live 12 Suite\Program\Ableton Live 12 Suite.exe`; standalone Max at `C:\Program Files\Cycling '74\Max 9\Max.exe`.
- Detected versions: Live 12.4.6; Max 9.1.4.6cc4519e5c9.
- Live and Max were opened using Computer Use. The Live User Library was relocated to `C:\Korg\Ableton_Max\Live User Library\User Library` so Live can save presets.
- Created and saved a routing Instrument Rack preset at `Kronos Routing.adg`. Its External Instrument routing still needs the actual MIDI output port and audio return inputs; it is not yet configured to the Kronos hardware.
- Created the Live set `Kronos Project\Kronos.als`. It currently has a MIDI track with Live's blank Max MIDI Effect template inserted. The set was saved in Live, then the latest `.als` was copied from the Desktop project folder into this workspace (19346 bytes; saved 2026-10-07 14:57).
- Live audio routing is now configured in the set: `3 Audio` receives Ext. In channel 1 and `4 Audio` receives Ext. In channel 2; both route to Main. Confirmed in Live and saved. The standalone routing rack preset still needs its own External Instrument port/channel values if it is intended to carry the return path.
- User saved the Max for Live device as `Kronos.amxd`; copied it to the workspace root (5812 bytes; saved 2026-10-07 14:58). The device has the `live.menu` object with its default enum labels (`one two three`); no KORG bank values have been applied yet.
- Saved a Live device preset checkpoint from the Max MIDI Effect header; it is `Kronos MIDI Effect.adv` (870 bytes; saved 2026-10-07 14:51). This is a Live preset wrapper/checkpoint, not the finished native Max for Live `.amxd`.
- Max was briefly accessible after the user saved `Kronos.amxd`. I maximized the window and expanded the `live.menu` Inspector's Parameter section. Computer Use failed again when focusing the Range/Enum editor, before changing its contents. The current Max window may still show the Range/Enum text editor with `one two three`; continue manually from there, replace with KORG labels, confirm, then save the `.amxd` again.
- First implementation target: KORG bank map. Add GM2 support later. The audio-return input pair is still unknown.
- The workspace `.als` was saved and synced after the user set up audio routing (19633 bytes; saved 2026-10-07 15:02). It includes the Max MIDI Effect with the `live.menu` object.
- Last durable checkpoints: `Kronos.amxd` (saved base device), `Kronos Project\Kronos.als` (current Live set and audio inputs 1/2), `Kronos MIDI Effect.adv` (Live preset wrapper), and `Kronos Routing.adg` (routing rack preset). Save both Live and Max at regular intervals and sync new versions into this workspace.

## Latest checkpoint — 2026-10-07 15:25
- The current working Max for Live device is `Kronos Program Selector.amxd` in the workspace root (saved in Max at 15:24; 9490 bytes at last file check). It contains the KORG bank selector, Program control, KORG bank mapping objects (`expr if($i1 < 6, $i1, $i1 + 2)`), `ctlout 32 1`, `f 63`, `ctlout 0 1`, and `pgmout 1`.
- The bank menu exposes `INT-A` through `INT-F` and `USER-A` through `USER-G`. The user has confirmed KORG bank map first; GM2 is later.
- Wiring visible in Max: bank selector to `t i b`, integer branch to the CC32 mapper/output, bang branch to `f 63`; Program control appears wired to `pgmout 1`. The final `f 63` output to `ctlout 0 1` is not yet confirmed/visible and should be checked or connected before calling the selector complete. Hardware MIDI response has not been tested.
- The user saved the Live set after the Max checkpoint. The latest Desktop set was copied into `Kronos Project\Kronos.als` (verify metadata below when resuming). Audio routing remains Ext. In 1/2 on tracks 3/4 as previously confirmed. The Kronos MIDI output port is still not selected in Live; hardware response remains unverified.
- Continue using Computer Use with Live and Max. Save Max with File > Save and Live with Ctrl+S at checkpoints. If Max cord ports remain hard to target, give the user clear step-by-step instructions to connect the outlet under `f 63` to the inlet above `ctlout 0 1`, then save in Max.

## Latest verified wiring checkpoint — 2026-10-07
- User connected the outlet of `f 63` to the inlet of `ctlout 0 1`. Confirmed visually in Max: `t i b` still triggers `f 63`, whose output now feeds CC0 (value 63). The title has no unsaved marker after saving in Max.
- Live was saved after the device update; Save Live Set is disabled and the title has no asterisk. The Desktop set was synced to `Kronos Project\Kronos.als` in the workspace.
- Basic KORG Program bank selection wiring is now in place. Hardware MIDI response remains untested because the Live MIDI track output still shows `No Output`; select the Kronos MIDI port when available. Continue later with the remaining Program/Combi bank list, continuous controls, and GM2 support after the KORG path is verified.

## KORG bank-map correction — 2026-10-07
- The official KORG Parameter Guide confirms Bank Map KORG uses CC0=0, not 63. The Max object is now `f 0`, wired through `ctlout 0 1`, saved in Max, and present in the Live checkpoint. The old device briefly had `f 63`; the corrected checkpoint supersedes it.
- The KORG bank dropdown still needs its Range/Enum list expanded to 21 Program banks and the LSB expression updated. Since Max stopped accepting input with the Range/Enum editor open, the user must make the following changes in that dialog:
  - Range/Enum labels: `INT-A INT-B INT-C INT-D INT-E INT-F INT-G USER-A USER-B USER-C USER-D USER-E USER-F USER-G USER-AA USER-BB USER-CC USER-DD USER-EE USER-FF USER-GG`
  - Replace `expr if($i1 < 6, $i1, $i1 + 2)` with `expr if($i1 < 7, $i1, $i1 + 1)`.
- KORG bank LSB mapping is indices 0–6 => 0–6, indices 7–13 => 8–14, indices 14–20 => 15–21. Combi mode uses only the first 14 bank labels; Program mode uses all 21. The KORG Parameter Guide states Bank Select applies to both Programs and Combinations, while Program-only USER-AA…GG are not Combination banks.
- The Live set was saved and synced into the workspace after the CC0 correction. The root design guide `MAX_FOR_LIVE_FORMAT.md` now reflects the KORG MSB/LSB mapping.

## Expanded KORG bank selector checkpoint — 2026-10-07
- Verified in Max after the user's edits: BankSelect Range/Enum contains 21 KORG Program banks in order: INT-A…G, USER-A…G, USER-AA/BB/CC/DD/EE/FF/GG. The LSB expression is `expr if($i1 < 7, $i1, $i1 + 1)`, mapping index 0–6 to LSB 0–6, 7–13 to 8–14, and 14–20 to 15–21.
- The fixed CC0 object is now `f 0`, feeding `ctlout 0 1`; BankSelect drives CC32; Program drives `pgmout 1`. Max title has no unsaved marker. The full bank-list popup remained open after my close click failed; next interaction can close it manually if it is still open.
- Live was saved after these changes (no title asterisk); the Desktop set was synced to `Kronos Project\Kronos.als`.
- Remaining KORG work: add reliable Program/Combi mode selection (SysEx on global channel, with a safe delay before Bank/Program messages), restrict/select the 14 valid Combi banks, re-trigger Program Change after a bank change as needed, add documented CC controls, and verify the MIDI route/responding hardware. GM2 follows later.

## In-progress mode selector — 2026-10-07
- The previously saved device remains the safe checkpoint with the verified 21-bank KORG dropdown, corrected CC0=0, and LSB formula `expr if($i1 < 7, $i1, $i1 + 1)`.
- A new `live.menu` object was added to the current Max patcher near the upper-right of the device area, but is not yet configured or saved. Its Range/Enum editor is open with default labels `one two three`; Max stopped accepting my click on that popup. The current patch has an unsaved marker. User needs to set labels to `Program Combi`, set Scripting Name, Long Name, and Short Name to `Mode`, then save in Max. After that, continue wiring: Mode index 0 Program -> SysEx mode 2, index 1 Combi -> SysEx mode 0, using `sxformat` into the existing `midiout`. Keep the CC0/CC32 bank and Program Change wiring intact. Give Max time to process mode changes before sending Bank/Program messages.
- No Live save/copy has been made for the in-progress Mode menu. Existing saved `.amxd` and `.als` remain recoverable checkpoints.

## Mode menu labels confirmed — 2026-10-07
- User entered and saved the `Mode` live.menu labels `Program Combi`; the Max inspector visually confirms Scripting Name, Long Name, and Short Name are all `Mode`.
- During Computer Use continuation, a native file dialog reappeared over Max and consumed an attempted object-entry action. Per the user's instruction, stop issuing typing/click commands while Max is not responding. Close the dialog with Escape, then create the mode SysEx formatter manually in Max if needed.
- Verified Cycling '74 `sxformat` documentation: it takes SysEx byte arguments; expressions are written as `is <expr> /`; the first and last bytes are 240/F0 and 247/F7. Planned object: `sxformat 240 66 48 104 78 is if($i1 == 0, 2, 0) / 247`. Connect Mode menu outlet to this object's inlet and the formatter outlet to the existing `midiout` inlet. This maps Program (menu index 0) to KORG mode byte 2 and Combi (index 1) to mode byte 0. Do not claim hardware verification; the Live MIDI output is still No Output.
- After wiring, save the Max device, then save Live and sync the newest `Kronos.als` from Desktop project folder to the workspace project folder. Update this note with the checkpoint time. The saved `.amxd` and `.als` before this menu wiring remain the last verified recovery checkpoint.

## Mode SysEx wiring checkpoint — 2026-10-07 16:22
- User completed the `Mode` menu labels (`Program`, `Combi`) and created the formatter object `sxformat 240 66 48 104 78 is if($i1 == 0, 2, 0) / 247`.
- Computer Use inspection confirmed the Mode menu feeds `sxformat`; I connected the formatter output to the existing `midiout` inlet, preserving the existing MIDI pass-through cable. Saved the Max device via File > Save. The title has no unsaved marker. Updated device: `Kronos Program Selector.amxd` (11902 bytes; 2026-10-07 16:22:24).
- Saved Live set with no title asterisk and synced Desktop copy into workspace: `Kronos Project\Kronos.als` (19957 bytes; 2026-10-07 16:22:48).
- Mode logic now maps Mode menu index 0 (Program) to KORG SysEx mode byte 2 and index 1 (Combi) to byte 0. This is code-level wiring only: actual Kronos response is not verified because the Live MIDI track still has `No Output`.
- Next work: add a short delay/safe sequencing so mode change completes before bank/program messages; limit or clearly disable USER-AA…GG for Combi; add the requested CC controls; configure Live MIDI output and test with Kronos hardware. GM2 remains deferred.

## Hardware connection assumption — 2026-10-07
- User clarified the Kronos is not connected right now and explicitly asked us to assume it works and responds. Proceed with the KORG control implementation on that assumption; do not block on physical verification. Retain the factual distinction that hardware behavior has not been tested.
- To avoid a mode-switch race, the current workflow can have the user choose Mode first, wait briefly for Kronos to switch, and then choose bank/program. No requirement to automatically re-send bank/program on a mode change has been confirmed. GM2 remains deferred until the KORG controls are complete.

## KORG CC control draft — 2026-10-07 16:29
- Resumed the build and added one `live.dial` object near the right edge of the Max patch as a Filter Cutoff control draft. It currently has Max defaults (`live.dial`, Float, 0–127) and is not yet connected to `ctlout 74 1`; do not present it as functional.
- Max Inspector Scripting Name field did not accept Computer Use text entry despite selection/focus checks. Per user direction, next time provide the user exact manual Inspector steps instead of repeating the failed typing action. For the selected dial: set Scripting Name `FilterCutoff`; Long Name `Filter Cutoff`; Short Name `Cutoff`; Type `Int`; Range/Enum `0 127`; then create `ctlout 74 1` and connect the dial outlet to its inlet. Save Max with File > Save.
- Saved Max device (`Kronos Program Selector.amxd`, 12827 bytes, 16:28:37) and Live set (title cleared after Ctrl+S; synced `Kronos Project\Kronos.als`, 20029 bytes, 16:29:35). This is a recovery checkpoint, although the new dial is only a draft.
- Hardware remains disconnected by user choice; continue under the user-approved assumption that MIDI commands work. No physical verification should be requested as a prerequisite. Continue after the cutoff draft with CC71,73,72,70; performance CCs 1,11,16,118,119,64; mixing/FX CCs 7,10,91,93; and KARMA CCs 14,31,102–109. GM2 later.

## Cutoff CC74 verified in patch — 2026-10-07 16:36
- After the user configured and saved the control, Max inspection confirms the dial's Scripting Name, Long Name, and Short Name are all `FilterCutoff`, its type is Int, and its range is 0–127. The dial is visibly wired to `ctlout 74 1`.
- Live showed an unsaved asterisk after the Max-device update; saved with Ctrl+S and confirmed the asterisk cleared. Synced the latest Desktop set to `Kronos Project\Kronos.als` (20017 bytes, 16:36:34). Max file currently 13362 bytes (16:34:26).
- This verifies patch structure only. Hardware is disconnected as requested and is assumed to respond. Next build the remaining KORG CC controls, preserving the mode/bank/program mappings. The CC reference table is in `MAX_FOR_LIVE_FORMAT.md`.

## Resume audit corrections — 2026-10-07 16:42
- Audited the saved `.amxd` patch JSON and found two CC cables targeted the middle inlet (controller-number inlet) instead of left/value inlet: `f 0` -> `ctlout 0 1` and `FilterCutoff` -> `ctlout 74 1`. Corrected both destination indices to inlet 0 in `Kronos Program Selector.amxd`. A backup of the previous file is `Kronos Program Selector pre inlet-fix.amxd`.
- Max Console showed that `sxformat` rejects `if()` with `expr • function if not found`. Replaced it with arithmetic `sxformat 240 66 48 104 78 is 2 - 2 * $i1 / 247`, mapping Program index 0 to byte 2 and Combi index 1 to byte 0. Saved-file JSON parses, and this expression uses only arithmetic; it still needs a fresh Max load check because Computer Use could not capture the reopened patch window after the console opened it.
- Updated the Live User Library device at `Live User Library\User Library\Presets\MIDI Effects\Max MIDI Effect\Kronos.amxd` with the corrected device. Preserved the old file as `Kronos pre-resume-fix.amxd` in that folder. The Live set `.als` itself is still the 16:36 checkpoint, before these inlet and SysEx corrections; reload the updated User Library device in Live and save the set when Max/Live UI is available.
- Max Console currently contains stale errors from the prior version, including the invalid `if()` expression. Clear/reopen before interpreting them as errors in the corrected file. User-requested hardware assumption remains in force; no physical Kronos connection is required.

## Max expression saved — 2026-10-07 16:50
- User reports replacing the `sxformat` text with the arithmetic expression and saving. Disk inspection of the latest Max-saved file confirms `sxformat 240 66 48 104 78 is 2 - 2 * $i1 / 247`; both `f 0` -> `ctlout 0 1` and `FilterCutoff` -> `ctlout 74 1` terminate at inlet 0. The Max-saved AMXD parses successfully using its normalized chunk header (file 13365 bytes; 16:50:07).
- Copied that latest Max-saved device to the Live User Library as `Kronos.amxd`, replacing the 16:42 copy; preserved that previous copy as `Kronos pre-1650-save.amxd`.
- Live set remains at its earlier 16:36 save (20017 bytes). Reload the updated User Library device into the Live set and save the set to embed the corrected patch. Do not use the old console errors as evidence about the corrected expression; fresh Max verification is still needed when the patcher window is targetable.

## Handoff checkpoint — 2026-10-07, before M3Kontrol analysis
- User requested a handoff to a new conversation and asked that the next task analyze `M3Kontrol.amxd` first to determine whether the Kronos project can be adapted to save time. Do not analyze or modify M3Kontrol until the new conversation begins.
- Confirmed both M3Kontrol files exist and match in size (600,323 bytes): `C:\Korg\Ableton_Max\M3Kontrol.amxd` and `C:\Users\Superdad\Documents\Ableton\User Library\M3Kontrol.amxd`. They were not opened or inspected in this handoff.
- The Desktop Live set `C:\Users\Superdad\Desktop\Kronos Project\Kronos.als` was saved 16:59:15 (19,981 bytes), newer than the workspace set. Synced it to `Kronos Project\Kronos.als` and preserved the previous workspace copy as `Kronos Project\Kronos pre-handoff 2026-10-07.als` (20,017 bytes, saved 16:36:34).
- Current Max device remains `Kronos Program Selector.amxd` (13,365 bytes, saved 16:50:07) and the User Library copy is `Live User Library\User Library\Presets\MIDI Effects\Max MIDI Effect\Kronos.amxd`. Existing patch state and known debugging notes are above; KORG first, GM2 later. Hardware is disconnected by user choice; assume responses and do not require physical verification.
- New-chat prompt saved as `NEW_PROMPT.md`. It directs the next chat to read the notes, analyze both M3Kontrol copies first, report findings and an adaptation recommendation before any implementation, preserve the original, then proceed with KORG work and regular checkpoints.

## M3-to-KRONOS reference comparison — 2026-10-07
- User added `M3_Sysex.zip`, `M3_ParamG_E.pdf`, and `KRONOS_Param_Guide_EN3.pdf` to the workspace and authorized editing the original M3 device, noting that they have copies. The archive contains `M3_SYSEX.TXT` and `M3_MIDIFX.TXT`; the Kronos folder already contains `KRONOS_MIDI_SysEx.txt` and its full parameter tables.
- Correct M3 model ID from the official M3 implementation is `75` hex (`0x75`, decimal 117), not `72` hex. The Kronos model ID is `68` hex (`0x68`, decimal 104). Both use function `4E` for Mode Change; mode bytes are Combination `0` and Program `2`, so mode control translates by changing the model ID while keeping those values. User's M3 header/example `0x72` is inconsistent with the official guide and source device.
- M3 MIDI tables explicitly assign KARMA ON/OFF CC14, sliders CC22–29, Scene CC30, Latch CC31, and KARMA switches CC102–109. M3 standard channel CCs also include bank select CC0/32, volume 7, pan 10, expression 11, XY 118/119, damper 64, and the sound controls CC70–79. These are the standard CC-based controls to retain/map in the Kronos device.
- M3Kontrol root patch has 602 boxes and 791 cords. It contains MIDI passthrough, standard CC widgets, an M3 mode formatter (`sxformat ... 117 78`), plus M3-only parameter messages (`... 117 65 ...`) and a UDP-to-M3Router architecture. The SysEx parameter-change command/address payloads are not safely ported by replacing model ID alone. Kronos has its own SysEx parameter functions/address tables; any direct M3 parameter-edit mappings need translation or should remain disabled.
- Next: use the M3 layout as the visual reference, preserve standard CC and KARMA mappings, translate the mode/bank/Program/Combi controls to Kronos, and identify or disable M3-specific SysEx/UDP features that lack a verified Kronos equivalent. Keep all changes recoverable; user has copies but preserve the original content unless a concrete adapted copy is ready.

## KronosKontrol first adaptation checkpoint — 2026-10-07
- User added `M3_Sysex.zip`, `M3_ParamG_E.pdf`, and `KRONOS_Param_Guide_EN3.pdf`, and authorized edits to the original M3 device. The original `M3Kontrol.amxd` remains unchanged; created a separate adaptation to preserve it.
- Created `Kronos Kontrol.amxd` by preserving the M3 panel, changing the mode SysEx model ID from M3 `75` to Kronos `68`, setting the KORG Bank Select MSB to `0`, and renaming the 14 shared bank labels to `INT-A...G` and `USER-A...G`. Replaced the M3 bank LSB logic with `expr $i1 + ($i1 >= 7)`, yielding CC32 values 0–6 and 8–14. Installed identical copy at `Live User Library\User Library\Presets\MIDI Effects\Max MIDI Effect\KronosKontrol.amxd`.
- The official Kronos Parameter Guide confirms the default KARMA control CCs match the M3: On/Off 14, sliders 22–29, Scene 30, Latch 31, switches 102–109. Corrected `MAX_FOR_LIVE_FORMAT.md` from CC15 to CC31 and updated earlier references in these notes.
- The M3 header in the user's example (`0x72`) does not match the official M3 implementation or M3Kontrol source; both use model ID `0x75`. Kronos uses `0x68`. Mode command `4E` and Program/Combi data values `2`/`0` remain the same.
- Structural inspection confirms the new AMXD retains the M3 panel and embedded resource tail, and its Max JSON parses. It has 603 boxes (one new bank mapper); the mode, CC0, CC32, and 14 bank labels contain the intended values. The User Library copy has the same SHA-256 as the root device. Max/Live loading and hardware response have not been checked.
- Remaining adaptation work: map Kronos Program-only USER-AA...GG banks; translate or explicitly disable the M3-only GE selector, Drum Track, FX and parameter-change SysEx. Those M3 parameter payloads use function `41` and M3-specific addresses; Kronos uses different parameter functions/address tables, so changing the model byte alone is unsafe. The Kronos MIDI CC controls and KARMA function are shared and retained.

## Kronos Kontrol real-time encoders — 2026-10-07
- Remapped the eight encoder dials in `Kronos Kontrol.amxd` from the M3-oriented CC1–8 output to Kronos defaults: knob1 CC74 (filter cutoff), knob2 CC71 (filter resonance), knob3 CC79 (filter EG intensity), knob4 CC72 (EG release), and knobs5–8 CC17/19/20/21 (Knob Mod.1–4). Korg documents these as the Kronos realtime knob CCs; Knobs 5–8 still depend on each Program/Combi's knob assignment.
- The X/Y vector panel already sends Kronos CC118/119; SW1/SW2 remain CC80/81 at 0/127; KARMA controls retain shared M3/Kronos CC assignments. No `sxsend`/`sysex` or hardware tests were run, per user instruction; assume the work functions and let the user check later.
- Updated installed User Library copy to match root device. Remaining review: GE selection, Drum Track, Wave Sequence, and FX switches are still routed through M3-specific SysEx/UDP parameter paths and need translation to the corresponding Kronos parameters before claiming the full M3 panel is adapted. Program-only USER-AA…GG also needs a clean UI/mode-safe addition; keep the 14 shared Combi/Program banks valid meanwhile.

## Kronos Kontrol continued adaptation checkpoint — 2026-10-07
- Expanded the bank `live.tab` to all 21 Kronos Program banks: INT-A…G, USER-A…G, USER-AA…GG. CC32 maps indices 0–6 to 0–6, 7–13 to 8–14, and 14–20 to 15–21. Mode state comes from the existing Program/Combi buttons. In Combi mode, selecting a Program-only bank returns the selector to USER-G (index 13) and sends the valid Combi-bank value.
- Remapped the eight RT encoder controls to Kronos defaults: CC74, CC71, CC79, CC72, CC17, CC19, CC20, CC21. Kronos knobs 5–8 depend on each Program/Combi's stored assignments.
- Translated the eight FX switches (IFX1–5, MFX1–2, TFX1) from the M3 SysEx formatter to Kronos function 43 parameter changes, using Program TYP=6 and Combi TYP=23, correct slot numbers, and mode gates. The old M3 effect formatter and its cords were removed.
- Mapped the Drum Track On/Off control to Kronos Program parameter TYP=0/SOC=0/SUB=0/PID=10/IDX=0 and gated it off in Combi mode, where the supplied Combi map has no corresponding Drum Track parameter. Corrected the inherited KARMA On/Off CC from 15 to the Korg default 14. SW1/SW2 CC80/81 use 0/127; KARMA switches/scene/latch retain their shared CC assignments; Vector X/Y use CC118/119.
- `Kronos Kontrol.amxd` and the Live User Library copy were synced. Structural inspection found 634 boxes, 835 cords, no missing cord endpoints, and both copies have SHA-256 `7574a3247eec93eee2c65914e202a75cee9646d941eec565a02b5ae77d150a4b` at this checkpoint.
- Per user instruction, no MIDI/SysEx send/receive or hardware tests were run; assume the adaptation works for later user verification. The old M3 GE-selection and Wave Sequence parameter paths still require Kronos translation; other M3-specific parameter paths need auditing before calling the entire panel complete.
- Final structural audit after adding the Program-only bank guard and Drum Track path: 636 boxes, 840 cords, 0 missing endpoints. Root and installed copies match at SHA-256 `79c2d5d88679111d4a884a33c60d351555d978258afe388d8d017d82f39dda58`. This supersedes the earlier 634/835 count and hash in the prior checkpoint.

## Kronos Kontrol GE selector adaptation — 2026-10-07
- Translated the five legacy M3 GE-selection formatter paths to Kronos integer Parameter Change (function 43): Program GE `TYP=1, SOC=0, SUB=0, PID=0, IDX=0`; Combi KARMA modules A–D use `TYP=3, SOC=0–3, SUB=0, PID=0, IDX=0`. The existing two 7-bit value inputs are retained as the low-order value bytes, with valueH fixed to zero.
- Disconnected two hidden M3-specific formatter outputs (`obj-334`, `obj-424`) from UDP forwarding. Inspection shows these are patch internals rather than front-panel controls: `obj-334` is driven by a hidden tab/counter path, and `obj-424` is driven only by an untriggered internal bang message. Their original purpose is not established.
- The existing GE menu still contains 3,200 M3 GE entries (index 0–3199), while Kronos documents a range through `0x0DFF` (0–3583). The additional Kronos GE names/indices were not available in the embedded M3 menu, so those 384 entries are not exposed yet. The existing 3,200 name-to-index correspondences were presumed compatible based on the shared KARMA GE catalog; no hardware test was done.
- Root `Kronos Kontrol.amxd` and installed `Live User Library/User Library/Presets/MIDI Effects/Max MIDI Effect/KronosKontrol.amxd` are identical, SHA-256 `02658343afb093f342e873c83e6382a4e9b205be4b3a1a50710fe635dd84d7e1`. Structural inspection: 636 boxes, 838 cords, zero missing cord endpoints. No SysEx send/receive or hardware tests were run, per user instruction.


## Encoder coverage correction — 2026-10-07
- The panel contains 24 dials in three banks (Control1, Control2, Control3), not just eight. Only Control1 is remapped to Kronos CCs 74, 71, 79, 72, 17, 19, 20, 21. Control2 and Control3 still emit legacy CC1–8 and have not been adapted. Therefore the encoder section is not complete.
- Control1's first four CCs correspond to cutoff, resonance, filter EG intensity, and EG release. Knobs 5–8 send CC17/19/20/21; their destination is determined by each Kronos Program/Combi's knob assignments. LFO speed is not a fixed generic assignment; it will respond only when a sound assigns an LFO parameter to one of those knobs.

## Kronos Kontrol color preview — 2026-10-07
- Applied a color-only preview: patcher presentation background black; pink/magenta control accents changed to pale yellow; panel comment labels and dial/live.text labels changed to pale yellow for contrast. No box/cord wiring or layout values were edited.
- Saved `Kronos Kontrol pre-black-yellow.amxd` as the pre-color backup and created `Kronos Kontrol Color Preview.amxd` as a separate preview copy. Root `Kronos Kontrol.amxd` and installed `Live User Library/User Library/Presets/MIDI Effects/Max MIDI Effect/KronosKontrol.amxd` match at SHA-256 `38669be4b8be730194602970a3a80f9c544412d25e47140a5725aeeb9a2acd58`.
- Structural inspection retains 636 boxes and 838 cords. Max currently has an older cached presentation open; its displayed screenshot did not refresh to the disk version, so the rendered black/yellow appearance is not visually confirmed in Max yet.
- Follow-up clarification: the exact `Kronos Kontrol Color Preview.amxd` JSON has a black patcher `bgcolor`, 0 inspected pink accent entries, and 261 pale-yellow color entries. The extracted project source at `KronosKontrol.amxd/patchers/KronosKontrol.amxd.maxpat` is a stale 602-box version with the old M3 palette. Max's `Project (KronosKontrol.amxd)` window may be the stale view the user reopened. PowerShell could not foreground the preview AMXD (Access Denied), so still open the exact preview AMXD directly in Max and visually confirm. Do not claim rendering was confirmed.
- Created `RESUME_PROMPT.md` with current state, constraints, exact paths, and next steps for another AI or a later session.
