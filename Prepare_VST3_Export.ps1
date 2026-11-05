# Prepares a Kronos Kontrol .vst3 export / test (see BUILD_EXPORT.md).
# Run it before exporting AND before the first load of every new .vst3 (plain or _x24) in a host.
# Export from the CtrlrX VST3 inside REAPER, to panels\KronosKontrol\vst3\ (the .exe goes to panels\KronosKontrol\exe\).
#
#   .\Prepare_VST3_Export.ps1                  # plain panel -> vst3\KronosKontrol_<ver>.vst3
#   .\Prepare_VST3_Export.ps1 -X24             # 24-px variant -> vst3\KronosKontrol_<ver>_x24.vst3
#   .\Prepare_VST3_Export.ps1 -RemoveOrphans   # also delete unused images from the CtrlrX folder
#   .\Prepare_VST3_Export.ps1 -Check           # after the first load: were all images extracted?
#   -Version 1.0g to force a version.
#
# It stops (and changes nothing) while a host still has a Kronos Kontrol .vst3 loaded:
# close that host or remove the plugin yourself first, nothing is killed.
#
# If PowerShell refuses to run scripts:
#   powershell -ExecutionPolicy Bypass -File .\Prepare_VST3_Export.ps1

param([string]$Version, [switch]$X24, [switch]$RemoveOrphans, [switch]$Check)
& (Join-Path $PSScriptRoot 'scripts\kk_prepare_export.ps1') -Target Vst3 @PSBoundParameters
exit $LASTEXITCODE
