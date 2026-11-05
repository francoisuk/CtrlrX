# Prepares a Kronos Kontrol .exe export / test (see BUILD_EXPORT.md).
# Run it before exporting AND before the first launch of every new .exe (plain or _x24).
# Save the exported .exe in panels\KronosKontrol\exe\ (the .vst3 goes to panels\KronosKontrol\vst3\).
# If a Low integrity label is ever back on kronos-corpus (-Check reports it), run C:\Korg\Reset_Integrity_Label.ps1.
#
#   .\Prepare_Exe_Export.ps1                  # plain panel, version from build_panel.py
#   .\Prepare_Exe_Export.ps1 -X24             # the 24-px variant
#   .\Prepare_Exe_Export.ps1 -RemoveOrphans   # also delete unused images from the CtrlrX folder
#   .\Prepare_Exe_Export.ps1 -Check           # after the first launch: were all images extracted? labelled .exe?
#   -Version 1.0g to force a version ; -Force closes a running Kronos Kontrol .exe without asking.
#
# If PowerShell refuses to run scripts:
#   powershell -ExecutionPolicy Bypass -File .\Prepare_Exe_Export.ps1

param([string]$Version, [switch]$X24, [switch]$RemoveOrphans, [switch]$Check, [switch]$Force)
& (Join-Path $PSScriptRoot 'scripts\kk_prepare_export.ps1') -Target Exe @PSBoundParameters
exit $LASTEXITCODE
