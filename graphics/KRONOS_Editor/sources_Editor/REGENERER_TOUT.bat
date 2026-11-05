@echo off
rem Regenerates every EDITOR page (KRONOS, NAUTILUS, OASYS) into .\out
rem Edit the two table folders below to match your PC.
setlocal
cd /d "%~dp0"
set KRONOS_TABLES=%~dp0MIDI implementation
set NAUTILUS_TABLES=C:\Korg\Manuals Nautilus\NAUTILUS_MIDIimp\SysExDumps

pip install -r requirements.txt || goto :err

set KRONOS_MIDIIMP=%KRONOS_TABLES%
python ked.py out\0.97i\Program || goto :err
python ked_combi.py out\0.97i\Combi || goto :err
python kfull.py out\KRONOS\Full || goto :err
python kfx.py out\KRONOS\Full\Effects || goto :err
python koasys.py out\OASYS\Full || goto :err
set KFULL_THEME=OASYS_OMNI
python kfx.py out\OASYS\Full\Effects || goto :err
set OASYS_REF=C:\Korg\kronos-corpus\ctrlr-project\reference\ref-oasys
if exist "%OASYS_REF%" python koasys_ofs.py out\OASYS\Full "%OASYS_REF%"
set KFULL_THEME=

set KRONOS_MIDIIMP=%NAUTILUS_TABLES%
python knaut.py out\NAUTILUS\Full || goto :err
set KFULL_THEME=NAUTILUS_NAVIGATOR
python kfx.py out\NAUTILUS\Full\Effects || goto :err

echo Done.
goto :eof
:err
echo *** Error - see the message above.
exit /b 1
