@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
cd /d C:\Korg\kronos-corpus\ctrlr-project\probe\src
cmake -B C:\Korg\kronos-corpus\ctrlr-project\probe\b -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_MAKE_PROGRAM=C:/Users/Superdad/AppData/Local/Python310/Scripts/ninja.exe
if errorlevel 1 exit /b 1
cmake --build C:\Korg\kronos-corpus\ctrlr-project\probe\b --target CtrlrPanelProbe -j 12
