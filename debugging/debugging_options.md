# Debugging a CTRLR VST3 Panel Crash in SAVIHost with Visual Studio 2022

This guide provides two complete methods to diagnose the native crash that occurs when you click your Editor button. You can either **attach the debugger to the live process** to watch the crash happen in real-time, or **capture a crash dump** and analyze it afterwards.

---

## Method 1: Live Debugging (Attach to Process)

This is usually the fastest route. You will attach the Visual Studio debugger to the already-running `savihost3.exe` process, reproduce the crash, and let VS break at the exact faulty instruction.

### Step 1: Prepare the Environment

1. Launch `savihost3.exe` normally and load your CTRLR panel.
2. **Run Visual Studio 2022 as Administrator** (right-click the VS shortcut → **Run as administrator**). This is often required to attach to certain processes correctly.

### Step 2: Attach the Debugger

1. In Visual Studio 2022, open the **Attach to Process** dialog: go to **Debug > Attach to Process...** or press **`Ctrl+Alt+P`**.
2. Set the **Connection type** to **Local** (this is the default for most local scenarios).
3. In the **Available processes** list, find `savihost3.exe`. You can type "savihost" in the **Filter processes** box to locate it quickly.
4. **Crucial step:** Before clicking Attach, look at the **Attach to:** field. By default it may say "Automatic." Click the **Select...** button next to it. In the "Select Code Type" dialog, choose **Native (C/C++)** and click OK. This tells VS to debug the C++ code inside the plugin, not just managed code.
5. Click **Attach**.

### Step 3: Reproduce the Crash

1. Go back to the `savihost3` window.
2. Click your **Editor button** to trigger the crash.
3. When the access violation occurs, Visual Studio will **break execution**. The debugger will stop and highlight the exact line of C++ code (likely inside `ctrlr.vst3` or a related DLL) that caused the fault.
4. You can now examine the **Call Stack** window (usually at the bottom right) to see the chain of function calls that led to the crash, and inspect variable values in the **Locals** or **Watch** windows.

> **Tip:** If you want to catch the crash even earlier, you can enable **Just-In-Time debugging** in Visual Studio (Tools > Options > Debugging > Just-In-Time). This can cause the debugger to launch automatically when an unhandled exception occurs outside of Visual Studio.

---

## Method 2: Post-Mortem Debugging (Crash Dump Analysis)

If live debugging is impractical, you can use **ProcDump** to capture a memory dump (`.dmp`) at the moment of the crash, then open that dump in Visual Studio for analysis.

### Step 1: Capture a Crash Dump with ProcDump

**ProcDump** is a free Sysinternals utility that can monitor a process and write a dump file when an unhandled exception occurs.

1. Download ProcDump from the official Sysinternals page: [https://learn.microsoft.com/sysinternals/downloads/procdump](https://learn.microsoft.com/sysinternals/downloads/procdump). Unzip it to a convenient folder.
2. Open a Command Prompt (as Administrator recommended).
3. Navigate to the ProcDump folder.
4. Launch `savihost3.exe` **through ProcDump** so that ProcDump is monitoring it from the start. Use this command (adjust the path to your `savihost3.exe`):

    ```bash
    procdump -accepteula -ma -e -x "C:\Path\To\savihost3.exe"