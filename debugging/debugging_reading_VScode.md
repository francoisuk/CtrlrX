
This proves the call **entered** SAVIHost's button handler, crossed the VST3 boundary into `ctrlr.vst3`, and faulted inside CTRLR. That is the smoking gun you need.

### Enabling Function Names (Symbols)

If you only see hex addresses (e.g., `0x00007FFA12B34567`) and no function names, symbols are missing. This is normal for a release build of `ctrlr.vst3`. You can still identify the module (the column on the right shows `ctrlr.vst3`), which is enough to prove the culprit. To improve symbol resolution:

- Add the **Microsoft Public Symbol Server** (`https://msdl.microsoft.com/download/symbols`) under **Tools > Options > Debugging > Symbols** to get names for Windows DLLs.
- If you can build a **debug version of CTRLR** with `.pdb` files, load those for full function and line names.

---

## 3. The Modules Window — Confirm What Is Loaded

Open **Debug > Windows > Modules** (or press `Ctrl+Alt+U`). This lists every DLL and executable loaded into the process at the time of the crash.

**What to look for:**

- Find `ctrlr.vst3` in the list. Its **Path** column shows where it was loaded from—confirm it is the build you expect.
- Check the **Symbol Status** column. If it says "Symbols loaded," you have function names in the Call Stack. If it says "Cannot find or open the PDB file," you will only see addresses.
- Note the **Version** and **Timestamp** columns to make sure you are debugging the same build you actually ran.

---

## 4. The Exception Settings / Exception Details

If you opened a dump, the **Minidump File Summary** window shows an **Exception** section with the exception code and address. If you attached live, Visual Studio displays the exception in the **Exception Settings** window and the yellow banner.

**Key fields to note:**

- **Exception Code:** `0xC0000005` = Access Violation (null pointer, invalid handle, use-after-free).
- **Exception Address:** The memory address of the faulting instruction. In the Call Stack, this maps to the top frame.
- **First-chance vs. second-chance:** If you see many "first-chance" exceptions in the Output window that do not crash the app, ignore them. Only the **second-chance (unhandled)** exception is the fatal one. The final stop is the one that matters.

---

## 5. The Threads Window — Check You Are on the UI Thread

Open **Debug > Windows > Threads** (or press `Ctrl+Alt+H`). The thread that faulted is marked with a yellow arrow.

**Why this matters for CTRLR:**

- The crash must occur on the **main UI thread** for a window-creation call to be valid. If the Call Stack top frame is on a **different thread** (e.g., a MIDI or timer thread), that itself is a likely root cause—your Lua code may be creating a window off the UI thread, which is illegal in Windows and will crash.
- Look at the **Name** or **ID** of the faulting thread. If it is not the thread running the message loop (usually the one that owns the `MainFrame` in the stack), flag it as a suspected threading bug in your panel.

---

## 6. The Locals and Watch Windows — Inspect the Bad Value

Open **Debug > Windows > Locals** (or press `Ctrl+Alt+V, L`) and **Watch** (`Ctrl+Alt+W, W`).

When stopped at the top frame, the Locals window shows the local variables of that function. If symbols are available for `ctrlr.vst3`, you can inspect the object pointers involved.

**What to look for:**

- A pointer that is `0x0000000000000000` (null) or `0x00000000FFFFFFFF` / `0xCCCCCCCC` (uninitialized memory, common in debug builds).
- A handle, window pointer, or component pointer that is clearly invalid.
- In the **Watch** window, you can type the name of a variable from the stack frame (e.g., `this`, or a parameter name if symbols exist) to inspect its members.

If you have no symbols for `ctrlr.vst3`, this window will be of limited use—rely on the Call Stack and Modules windows instead.

---

## 7. The Output Window — Last Words Before the Crash

Open **Debug > Windows > Output** (or press `Ctrl+Alt+O`). Look at the **Debug** pane. Before the crash, you may see:

- Last `print()` or `TRACE()` messages from the plugin.
- Last-chance exception messages.
- Module load/unload messages that hint at what was happening.

Scroll to the bottom just before the "The program has exited with code..." or "Unhandled exception" line. The lines immediately above it are the last thing the plugin did before dying—often a surprisingly useful clue.

---

## 8. Decision Tree: Who Is the Culprit?

Use this quick checklist after the debugger stops:

1. **Is the top Call Stack frame in `ctrlr.vst3`?**
   - **Yes →** The fault is inside CTRLR. Your Lua panel code triggered it. Proceed to inspect the call chain for the specific API (e.g., window creation, component lookup).
   - **No →** Go to step 2.
2. **Is the top frame in `savihost3.exe`?**
   - **Yes →** The fault is in the host. This is unlikely for your scenario; report it to the SAVIHost developer.
   - **No →** Go to step 3.
3. **Is the top frame in a Windows/system DLL (`ntdll`, `user32`, `kernel32`) or the C++ runtime?**
   - Look **down** the stack to the first non-system frame. That module is the one that passed bad data. If it is `ctrlr.vst3`, treat it as a CTRLR crash.
4. **Is the faulting thread the main UI thread?**
   - **No →** Suspect a threading bug in the panel (window creation off the UI thread).
   - **Yes →** Proceed with normal analysis.

---

## 9. What to Record for Further Analysis

When you have the debugger stopped, note down (or screenshot) the following—this is the evidence you will use to fix the panel:

- The **full Call Stack** (top 10 frames), including module names.
- The **exception code and address**.
- The **thread ID** and whether it is the UI thread.
- The last lines of the **Output** window before the crash.
- Any **null or suspicious pointer values** visible in Locals/Watch.
- The **module path and version** of `ctrlr.vst3` from the Modules window.

With this record, you can trace the Lua API call that reaches the faulting native function and identify the invalid argument or lifecycle issue (e.g., a closed window handle, a freed component, or an off-thread UI call) that your Editor button code is triggering.

---

## 10. Quick Reference Table

| Debugger Window | Shortcut | What to Look For |
|---|---|---|
| Call Stack | `Ctrl+Alt+C` | Top frame's module (`ctrlr.vst3` vs `savihost3.exe`) |
| Modules | `Ctrl+Alt+U` | `ctrlr.vst3` loaded, symbol status, version |
| Threads | `Ctrl+Alt+H` | Faulting thread is the UI/main thread |
| Locals | `Ctrl+Alt+V, L` | Null or invalid pointers in the faulting frame |
| Watch | `Ctrl+Alt+W, W` | Manually inspect specific variables |
| Output | `Ctrl+Alt+O` | Last log lines before the crash |
| Exception Settings | `Ctrl+Alt+E` | Exception code `0xC0000005` (access violation) |

---

## Summary

Reading the debugger for a CTRLR-in-SAVIHost crash comes down to three steps:

1. **Look at the top of the Call Stack.** If it says `ctrlr.vst3`, the fault is in CTRLR—your panel triggered it.
2. **Confirm the faulting thread is the UI thread.** If not, suspect a threading bug in your Lua code.
3. **Inspect the frames below** to see the path from your Editor button handler, across the VST3 boundary, into the faulty CTRLR function.

The exception banner saying `savihost3.exe` is **not** evidence against CTRLR—it only identifies the process. The Call Stack is the authoritative source of blame, and in your case it will almost certainly point into `ctrlr.vst3`, confirming that the crash originates in the plugin's handling of your panel's Editor button code.