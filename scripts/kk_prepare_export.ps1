# Shared core for Prepare_Exe_Export.ps1 and Prepare_VST3_Export.ps1 (see BUILD_EXPORT.md).
# Do not run directly; the two wrappers in ctrlr-project\ call it with -Target Exe or -Target Vst3.
#
# What it does:
#   1. finds the panel to export (version from sources\build_panel.py, -X24 for the 24-px variant);
#   2. checks %APPDATA%\CtrlrX\kkKronosKontrol (must exist and be full; never emptied here);
#      lists orphan images (packed into every export but unused), removes them only with -RemoveOrphans;
#   3. makes sure no exported Kronos Kontrol is running (exe: offers to close it; vst3: lists hosts to close);
#   4. clears the exported-instance cache: %APPDATA%\Kronos Kontrol\.delete_me_to_reload_resources
#      and the files in %APPDATA%\Kronos Kontrol\kkKronosKontrol (keeps the folder and Kronos Kontrol.settings);
#   5. prints the export steps.
#   -Check (run after the first launch of the new build): verifies the images were extracted ; flags .exe files
#      and running hosts that carry a Low integrity label (they cannot write to %APPDATA%).
# Since 1.0g the panel also repairs a stale cache itself (kkResCheck, one restart) ; clearing still gives a clean test.

param(
    [Parameter(Mandatory = $true)][ValidateSet('Exe', 'Vst3')][string]$Target,
    [string]$Version,
    [switch]$X24,
    [switch]$RemoveOrphans,
    [switch]$Check,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$root      = Split-Path -Parent $PSScriptRoot                     # ctrlr-project
$panelDir  = Join-Path $root 'panels\KronosKontrol'
$ctrlrRes  = Join-Path $env:APPDATA 'CtrlrX\kkKronosKontrol'      # CtrlrX editor resources (packed into exports)
$instDir   = Join-Path $env:APPDATA 'Kronos Kontrol'              # = panel name attribute (CtrlrProperties folderName)
$instRes   = Join-Path $instDir 'kkKronosKontrol'                 # = panelUID
$marker    = Join-Path $instDir '.delete_me_to_reload_resources'

$exeDir    = Join-Path $panelDir 'exe'                          # maintainer's rule (4 Nov 2026) : builds in panels\KronosKontrol\exe and \vst3

function Say([string]$m, [string]$c = 'Gray') { Write-Host $m -ForegroundColor $c }

# An .exe carrying « Mandatory Label\Low Mandatory Level » runs at Low integrity and cannot write to %APPDATA%
function LowExes {
    $dirs = @($exeDir, 'C:\Korg\KronosKontrol_builds\exe', (Join-Path $root 'for_agent'))
    foreach ($d in $dirs) {
        if (Test-Path $d) {
            Get-ChildItem $d -Filter 'Kronos Kontrol*.exe' -File | Where-Object { (icacls $_.FullName | Out-String) -match 'Low Mandatory Level' }
        }
    }
}

# Running CtrlrX / Kronos Kontrol / host processes whose executable file carries a Low integrity label
# (e.g. if the label comes back on kronos-corpus : C:\Korg\Reset_Integrity_Label.ps1)
function LowProcs {
    Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -and ($_.ProcessName -match 'ctrlr|kronos|host') -and ((icacls $_.Path | Out-String) -match 'Low Mandatory Level')
    }
}

# Processes that have an exported Kronos Kontrol .vst3 loaded (single-file .vst3 or a .vst3 bundle)
function VstHosts {
    foreach ($p in Get-Process) {
        try {
            if ($p.Modules | Where-Object { $_.FileName -match '\\KronosKontrol[^\\]*\.vst3(\\|$)' }) { $p }
        } catch { }   # protected processes
    }
}

# --- 1. panel -------------------------------------------------------------------------------
if (-not $Version) {
    $bp = Join-Path $panelDir 'sources\build_panel.py'
    $m = Select-String -Path $bp -Pattern "^VERSION\s*=\s*'([^']+)'" | Select-Object -First 1
    if (-not $m) { throw "VERSION not found in $bp ; pass -Version 1.0x" }
    $Version = $m.Matches[0].Groups[1].Value
}
$suffix = if ($X24) { '_x24' } else { '' }
$panel  = Join-Path $panelDir ("KronosKontrol_{0}{1}.panel" -f $Version, $suffix)
if (-not (Test-Path $panel)) { throw "Panel not found: $panel (build it first with build_panel.py)" }

$used = @(Select-String -Path $panel -Pattern 'resourceFile="([^"]+)"' -AllMatches |
          ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)

Say ""
Say ("Kronos Kontrol {0}{1} - {2} export" -f $Version, $suffix, $Target) 'Cyan'
Say ("Panel : {0}  ({1} images)" -f $panel, $used.Count)

# --- -Check : after the first launch ----------------------------------------------------------
if ($Check) {
    $ok = $true
    if ($Target -eq 'Exe') {
        foreach ($f in LowExes) {
            Say ("Low integrity label on {0} : it cannot write to %APPDATA% - run C:\Korg\Reset_Integrity_Label.ps1." -f $f.FullName) 'Yellow'
        }
    }
    foreach ($p in LowProcs) {
        Say ("Running from a Low-labelled file : {0}  {1} - its writes to %APPDATA% fail ; run C:\Korg\Reset_Integrity_Label.ps1." -f $p.ProcessName, $p.Path) 'Yellow'
    }
    if ($Target -eq 'Vst3') {
        $h = @(VstHosts)
        if ($h.Count) { $h | ForEach-Object { Say ("Loaded in : {0} (pid {1})" -f $_.ProcessName, $_.Id) } }
        else { Say "No host has a KronosKontrol*.vst3 loaded right now." 'Yellow' }
    }
    if (Test-Path $marker) { Say ("Marker : {0}" -f (Get-Item -Force $marker).LastWriteTime) }
    else {
        Say "Marker : missing. Either the new build has not been launched yet, or (1.0g+) it has just repaired a stale cache" 'Yellow'
        Say "         and asked for a restart. Close it, launch / load it again, then -Check again." 'Yellow'
        exit 1
    }
    $have = @()
    if (Test-Path $instRes) { $have = @(Get-ChildItem $instRes -File | ForEach-Object Name) }
    $missing = @($used | Where-Object { $have -notcontains $_ })
    Say ("Extracted : {0} files ; missing for this panel : {1}" -f $have.Count, $missing.Count)
    if ($missing.Count) { $missing | Select-Object -First 15 | ForEach-Object { Say "  missing $_" 'Red' }; $ok = $false }
    if ($ok) { Say "OK - the build extracted every image it needs." 'Green' }
    else     { Say "NOT OK - close the build, run this script again without -Check, relaunch." 'Red'; exit 1 }
    exit 0
}

# --- 2. CtrlrX resource folder (never emptied) -------------------------------------------------
if (-not (Test-Path $ctrlrRes) -or -not (Get-ChildItem $ctrlrRes -File | Select-Object -First 1)) {
    Say "WARNING : $ctrlrRes is missing or empty." 'Red'
    Say "  Open the panel in CtrlrX once (it re-creates and fills the folder), then run this script again." 'Red'
    Say "  Do not export now: every image import would fail." 'Red'
    exit 1
}
$files   = @(Get-ChildItem $ctrlrRes -File)
$orphans = @($files | Where-Object { $used -notcontains $_.Name })
$absent  = @($used  | Where-Object { -not (Test-Path (Join-Path $ctrlrRes $_)) })
Say ("CtrlrX resources : {0} files, {1} orphan(s), {2} not yet there" -f $files.Count, $orphans.Count, $absent.Count)
if ($absent.Count) { Say "  (normal: CtrlrX writes them when you open the panel)" }
if ($orphans.Count) {
    $orphans | ForEach-Object { Say ("  orphan {0}  ({1:yyyy-MM-dd HH:mm})" -f $_.Name, $_.LastWriteTime) 'Yellow' }
    if ($RemoveOrphans) {
        if ($orphans.Count -ge $files.Count) { throw "Refusing to remove every file of $ctrlrRes" }
        $orphans | Remove-Item -Force
        Say "  orphans removed (they would have been packed into the export)." 'Green'
    } else {
        Say "  they will be packed into the export; rerun with -RemoveOrphans to delete them (folder kept)."
    }
}

# --- 3. no running exported instance ------------------------------------------------------------
if ($Target -eq 'Exe') {
    if (-not (Test-Path $exeDir)) { New-Item -ItemType Directory -Force $exeDir | Out-Null }
    $running = @(Get-Process -Name 'Kronos Kontrol*' -ErrorAction SilentlyContinue)
    if ($running.Count) {
        $running | ForEach-Object { Say ("Running : {0} (pid {1}) {2}" -f $_.ProcessName, $_.Id, $_.Path) 'Yellow' }
        $go = $Force -or ((Read-Host "Close it now? [y/N]") -match '^[yYoO]')
        if (-not $go) { Say "Close it yourself, then run this script again." 'Red'; exit 1 }
        $running | Stop-Process -Force
        Start-Sleep -Milliseconds 800
    }
} else {
    $hosts = @(VstHosts)
    if ($hosts.Count) {
        $hosts | ForEach-Object { Say ("Host with Kronos Kontrol loaded : {0} (pid {1})" -f $_.ProcessName, $_.Id) 'Yellow' }
        Say "Save your work and close it (or remove the plugin), then run this script again." 'Red'
        Say "(A host only running the CtrlrX VST3 to export is fine.)"
        exit 1
    }
}

# --- 4. clear the exported-instance cache --------------------------------------------------------
if (Test-Path $marker) {
    $t = (Get-Item -Force $marker).LastWriteTime
    Remove-Item -Force $marker
    Say ("Marker removed (dated {0:yyyy-MM-dd HH:mm})." -f $t) 'Green'
} else { Say "Marker : none." }
if (Test-Path $instRes) {
    $old = @(Get-ChildItem $instRes -File -Force)
    $old | Remove-Item -Force
    Say ("{0} cached image(s) removed from {1} (folder kept)." -f $old.Count, $instRes) 'Green'
}
if (Test-Path (Join-Path $instDir 'Kronos Kontrol.settings')) { Say "Kronos Kontrol.settings kept." }

# --- 5. next steps ---------------------------------------------------------------------------------
$vstOut = Join-Path $panelDir ("vst3\KronosKontrol_{0}{1}.vst3" -f $Version, $suffix)
$self   = if ($Target -eq 'Exe') { 'Prepare_Exe_Export.ps1' } else { 'Prepare_VST3_Export.ps1' }
$flag   = if ($X24) { ' -X24' } else { '' }
Say ""
Say "Ready. Next:" 'Cyan'
if ($Target -eq 'Exe') {
    Say "  1. CtrlrX.exe (Program Files) : File > Open Panel  $panel"
    Say "  2. Release: File > Export > Export restricted instance ; license : Yes, paste licence\EULA.txt ; save to"
    Say "     $exeDir\Kronos Kontrol ${Version}${suffix}_restricted.exe"
    Say "     (test build: Export instance ; license : No ; save as  Kronos Kontrol $Version$suffix.exe)"
} else {
    Say "  1. REAPER : add the CtrlrX VST3 to a track ; in it, File > Open Panel  $panel"
    $vstRel = $vstOut -replace '\.vst3$', '_restricted.vst3'
    Say "  2. Release: File > Export > Export restricted instance ; license : Yes, paste licence\EULA.txt ; save to  $vstRel"
    Say "     (test build: Export instance ; license : No ; save to  $vstOut)"
    Say "  2b. REAPER > Preferences > Plug-ins > VST > Re-scan > 'Re-scan VST paths for new/modified plug-ins'"
}
Say "  3. Launch / load the new build once, then check:  .\$self$flag -Check"
Say "  Before launching another build (e.g. the other variant), run this script again for it." 'Yellow'
exit 0
