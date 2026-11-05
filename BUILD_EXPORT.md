# Building the Kronos Kontrol .exe / .vst3 (CtrlrX 5.6.36)

*Written 4 Nov 2026, revised the same day after the 1.0g exports. Applies to the .exe and the .vst3. Verified on 1.0g, 228/228 images both times: the .exe launched by double-click, without admin rights; the .vst3 loaded in REAPER. All builds live in `panels\KronosKontrol\exe\` and `panels\KronosKontrol\vst3\`.*

## Short version

1. Build the panel(s) with `sources/build_panel.py`.
2. Run `.\Prepare_Exe_Export.ps1` or `.\Prepare_VST3_Export.ps1`.
   **No _x24 build since 4 Nov 2026:** the 24 px bug no longer shows in CtrlrX 5.6.36. `-X24` / `KK_X24=1` stay available only to re-test it.
3. Export:
   - **.exe** from `CtrlrX.exe` (Program Files) → **`panels\KronosKontrol\exe\`** (maintainer's rule, 4 Nov 2026: every build in `panels\KronosKontrol\exe` or `\vst3`);
   - **.vst3** from the **CtrlrX VST3 inside REAPER** → **`panels\KronosKontrol\vst3\`**, then REAPER > Preferences > Plug-ins > VST > *Re-scan VST paths for new/modified plug-ins* (the folder is already in REAPER's paths).
   - **Release builds** (since 1.0h, 4 Nov 2026): use *Export restricted instance* and add `_restricted` to the file name. At « Would you like to attach a license to this panel? », answer **Yes**.
     - CtrlrX then shows a « License content » box. **Paste the text** of `panels/KronosKontrol/licence/EULA.txt` there: it does not pick a file.
     - At its first launch the build shows a « License agreement » window, and the user accepts it.
   - **Test builds:** use *Export instance* and answer **No**.

## Rule 0 (maintainer, 4 Nov 2026): never REAPER and CtrlrX at the same time

REAPER and CtrlrX compete for the same resource and hang. CtrlrX here means the standalone **or** an
exported Kronos Kontrol .exe.

**Order:**
1. Exe export and its check in CtrlrX.
2. Quit CtrlrX (close the panel first) **and** the test .exe.
3. Only then open REAPER for the VST3.

## Trap 0b: two Kronos VST3s in the scan path (the host loads the wrong one)

Every Kronos Kontrol VST3 build has the **same VST3 UID** (`…4B724B7446725273`). REAPER lists one « Kronos Kontrol (Francois Rossi) » entry and loads whichever file it picks.

This happened on 4 Nov: with 1.0g and 1.0h both in `vst3\`, REAPER loaded 1.0g.

**Rules:**
- Before testing a new VST3, quit REAPER and rename the older build to `.vst3.disabled`. REAPER keeps the DLL locked until it quits.
- After adding the plug-in, confirm which file was loaded:
  `(Get-Process reaper).Modules | ? FileName -match Kronos`.
- Users who keep two versions installed hit the same thing. Tell them to keep only one.

## Trap 0: CtrlrX starts but never shows a window

**Cause:** `%APPDATA%\CtrlrX\CtrlrX.settings` stores **every panel open at quit**, in full: 20 MB with two Kronos panels on 4 Nov. CtrlrX rebuilds them all before it shows its window. It sits at ~60 MB with no window and looks hung.

**Rules:**
- **Close the panel (File > Close) before quitting CtrlrX.**
- **Launch only one CtrlrX at a time.** Starting it again from the Start menu while it runs opens a second, empty instance.

**Fix:**
1. Stop CtrlrX.
2. Rename `CtrlrX.settings` (don't delete it). CtrlrX then starts empty, with default preferences.
3. Do **not** remove `%APPDATA%\CtrlrX\kkKronosKontrol`. That is the image folder the export packs. If it is gone, open the panel once in CtrlrX to recreate it before you run the prep script.
4. Run the script again just before the first launch / load of each build, then run it with `-Check`.

## Two folders, two different jobs

| Folder | Who writes it | What to do |
|---|---|---|
| `%APPDATA%\CtrlrX\kkKronosKontrol` | **CtrlrX itself** (editor or CtrlrX VST3) when it loads a `.panel`. The export packs **every file in this folder** into the .exe / .vst3. | **Never empty it, never delete it.** If it is empty, CtrlrX deletes it and every image import fails. Removing *orphan* files only is fine (`-RemoveOrphans`). |
| `%APPDATA%\Kronos Kontrol\` (`.delete_me_to_reload_resources`, `kkKronosKontrol\`, `Kronos Kontrol.settings`) | **The exported .exe / .vst3**, at its first launch. The folder name comes from the panel's `name` attribute, and `kkKronosKontrol` is the `panelUID`. The .exe, the .vst3, plain and x24 all share it. | **Clear the marker and the images before testing a new export** (the scripts do it). Keep the settings file. |

## Trap 1: the marker (cause of the 1.0f « Invalid Resource »)

An exported instance extracts its embedded images **only if `%APPDATA%\Kronos Kontrol\.delete_me_to_reload_resources` does not exist** (CtrlrX `importInstanceResources`). Otherwise it trusts the files already there. The marker carries no version and no hash, so a marker left by **any** older build blocks the next one.

On 4 Nov the marker dated from 3 Nov 21:05, and the folder held only two old images. The 1.0f build asked for other names, so it showed a black background, no knobs, and red « Invalid… » in the X-Y pad. The export itself was fine. The marker starts with a dot: delete it explicitly.

**Since 1.0g the panel repairs this itself** (`kkResCheck` in `lua/kkMain.lua`, file list `KK_RES` generated by `build_panel.py`):
1. At load, an exported build checks that every one of its images is in the cache.
2. If any is missing, it deletes the marker and the stale images, writes « UPDATED - please close and reopen Kronos Kontrol » in the monitor line, and shows a message box.
3. The next launch extracts everything.

It does nothing in the CtrlrX editor, nothing on a healthy cache, and nothing on a first install. It was verified on the real 1.0g .exe against the stale 3 Nov cache. So a forgotten clean-up now costs one restart instead of a broken panel. Testers need nothing else. Clearing before a test still gives the cleanest first-launch result.

Caveat: a tester who switches between two **different versions** (e.g. an old .vst3 in a DAW and a new .exe) triggers the repair, and one restart, at each switch.

## Trap 2: the Low integrity label on `C:\Korg\kronos-corpus`

> **Removed on 4 Nov 2026.** The maintainer reset the tree to Medium (`icacls … /setintegritylevel "(OI)(CI)M" /T /C`, saved as `C:\Korg\Reset_Integrity_Label.ps1`). Exes inside the repo now run normally.
> - **It can come back** if the tool that set the label (`CodexSandboxUsers`) works here again.
> - **To check:** `powershell -ExecutionPolicy Bypass -File C:\Korg\Reset_Integrity_Label.ps1 -CheckOnly`. `Prepare_Exe_Export.ps1 -Check` also still flags labelled exes.
> - **If the errors below reappear:** run the script without `-CheckOnly`.
>
> The rest of this section explains the problem, should it return.

`C:\Korg\kronos-corpus` and `ctrlr-project` carry an explicit **Low integrity label** (`icacls` shows `Mandatory Label\Low Mandatory Level:(OI)(CI)(NW)`, next to `CodexSandboxUsers`). Another tool's sandbox set it, so leave it alone. Every file created below inherits it. Windows starts an .exe at no more than its file's label, so **any .exe under `kronos-corpus` runs at Low integrity and cannot write to `%APPDATA%`**. That includes an exported Kronos Kontrol .exe and the test host `kronos-corpus\temp\vst3host\CtrlrX.exe`. Symptoms:

- « CtrlrResourceManager::ctor failed to create resources directory »;
- then one « ImportResource can't replace file contents with new data, resource: …\kkKronosKontrol\<image>.png » per image;
- no marker and no settings written;
- a launch through the shell can also hang;
- « Run as administrator » hides the problem.

What to do if the label is back:
- **Run `C:\Korg\Reset_Integrity_Label.ps1`** (it elevates itself). Builds stay where they are, in `panels\KronosKontrol\exe\` and `\vst3\`.
- As a stopgap without resetting, **copy** (do not move: a move keeps the label) the .exe to a folder outside `kronos-corpus` and launch that copy. While the label is there, avoid `temp\vst3host\CtrlrX.exe` as well, and use REAPER (Program Files).
- `-Check` flags labelled .exes and running processes started from a labelled file.
- Not affected: the .vst3 file in `panels\KronosKontrol\vst3\`, because a host keeps its own integrity level when it loads a plugin. Also not affected: testers, because a downloaded or unzipped .exe has no such label.
- To check a file: `icacls "<file>"` must show no `Low Mandatory Level` line.

## Scripts

Run from `ctrlr-project\`. If scripts are blocked: `powershell -ExecutionPolicy Bypass -File .\Prepare_Exe_Export.ps1`.

| Command | When |
|---|---|
| `.\Prepare_Exe_Export.ps1` [`-X24`] | Before exporting, **and before the first launch of each new .exe** |
| `.\Prepare_VST3_Export.ps1` [`-X24`] | Same for the .vst3 |
| add `-Check` | After the first launch / load: every image extracted? (exe: also flags labelled .exes) |
| add `-RemoveOrphans` | Also deletes unused images from the CtrlrX folder (never the folder itself) |

- **Version:** read from `sources/build_panel.py`; `-Version 1.0g` forces one.
- **The CtrlrX folder:** the scripts never touch it unless you pass `-RemoveOrphans`, and they stop if it is missing or empty.
- **Exe script:** if a `Kronos Kontrol*.exe` is running, it asks before closing it (`-Force` skips the question).
- **VST3 script:** if a host has a `KronosKontrol*.vst3` loaded, it stops and changes nothing. Close the host or remove the plugin yourself. A host running only the CtrlrX VST3 for the export is fine.
- **Both:** they delete the marker and the cached images, keep `Kronos Kontrol.settings`, then print the panel to open and the export target.

Only if the 24 px test is ever revived: export the plain and x24 builds, then **run the script again before launching each one** (with or without `-X24`), then `-Check`. Both variants use the same 228 images.

Shared code: `scripts/kk_prepare_export.ps1`.

## Procedure by hand (what the scripts do)

1. **(Optional) Orphans.** List the images in the CtrlrX folder that the panel no longer uses. They are harmless but still get packed into the export:

   ```powershell
   $panel = "C:\Korg\kronos-corpus\ctrlr-project\panels\KronosKontrol\KronosKontrol_1.0g.panel"
   $used  = Select-String -Path $panel -Pattern 'resourceFile="([^"]+)"' -AllMatches | % { $_.Matches } | % { $_.Groups[1].Value } | Sort-Object -Unique
   Get-ChildItem "$env:APPDATA\CtrlrX\kkKronosKontrol" | ? { $used -notcontains $_.Name } | Select Name, LastWriteTime
   ```

   Delete only the files listed. Keep the folder.
2. **Export** as in the short version.
3. **Before the first launch / load**, close every Kronos Kontrol instance (exe and host), then:

   ```powershell
   Remove-Item "$env:APPDATA\Kronos Kontrol\.delete_me_to_reload_resources" -Force -ErrorAction SilentlyContinue
   Remove-Item "$env:APPDATA\Kronos Kontrol\kkKronosKontrol\*" -Force -ErrorAction SilentlyContinue
   ```
4. **Launch.** The marker gets today's date, and `%APPDATA%\Kronos Kontrol\kkKronosKontrol` holds as many files as the panel has images (228 in 1.0g).

## Quick diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| Black or old background, missing knobs, red « Invalid Resource » (builds before 1.0g) | Stale marker (trap 1) | Run the prepare script, relaunch |
| « UPDATED - please close and reopen Kronos Kontrol » + message box (1.0g and later) | The self-repair found a stale cache and cleared it | Close and reopen once |
| « ctor failed to create resources directory », then « can't replace file contents » per image | The .exe (or host) runs at Low integrity (trap 2) | Run `C:\Korg\Reset_Integrity_Label.ps1`, then relaunch |
| « resource directory is not one » per image **in CtrlrX** while loading the panel | `%APPDATA%\CtrlrX\kkKronosKontrol` was emptied or deleted | Reload the panel in CtrlrX so it refills the folder, check it is full, export again |
| New .vst3 missing from REAPER's plugin list | Not scanned yet | Preferences > Plug-ins > VST > Re-scan VST paths for new/modified plug-ins |

At load the panel sends `F0 42 30 68 12 F7` (KRONOS Mode Request, read-only) to the selected MIDI out.

## Background: options considered for testers (4 Nov 2026)

- **A. Version in the panel `name`.** It gives a new `%APPDATA%` folder per version. Not chosen: hosts show the name, MIDI settings are lost at each version, and folders pile up. Changing `panelUID` alone does not help, because the marker sits one level up.
- **B. Panel-side self-repair.** **Chosen, in 1.0g.** It costs one restart per upgrade.
- **C. Fix in CtrlrX `importInstanceResources`** (compare hashes, as the editor already does). Reported to Damien Sellier: `for_ds/`.
