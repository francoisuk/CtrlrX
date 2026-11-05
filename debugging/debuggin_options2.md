
# Debugging a CTRLR VST3 Panel Crash in SAVIHost — Corrected Guide (v2)

> **vice-cli reports:  Correction notice.** The previous version of this guide assumed a native access violation (`0xC0000005`: null pointer, bad handle, or off-thread UI call). That assumption is wrong for this crash. The three dumps show the fatal exception is **`0xC0000409`** raised via **`__fastfail(7)`** inside **`abort()` ← `std::terminate()`** — i.e. an **uncaught C++ exception**, specifically **`luabind::error`** propagating out of the Edit-button callback chain. The unwind data for the 5.6.23 binary confirms the call overloads that invoke `kkClick` and `kkTabChanged` have **no `try`/`catch`** (UHANDLER-only: just the `ScopedLock`), so any Lua error on that path terminates `savihost3.exe` silently.
>
> The one conclusion from v1 that still holds is the important one: **top of the non-system call stack in `ctrlr.vst3` → the panel caused it.** That is already established. What remains is recovering the *formatted Lua error string*, which the WER minidumps do not contain because they are partial-heap dumps.

---

## 1. What the dumps already established

| Fact | Evidence |
|---|---|
| Fatal exception code | `0xC0000409` (fail-fast), not `0xC0000005` |
| Fail-fast sub-code | `7` (`FAST_FAIL_FATAL_APP_EXIT`) |
| Path to termination | uncaught C++ exception → `std::terminate()` → `abort()` → `__fastfail(7)` |
| Exception type | `luabind::error` (a Lua error converted to a C++ throw by luabind) |
| Faulting module | `ctrlr.vst3` (first non-system frame) |
| Host-side handling | none — the `kkClick` / `kkTabChanged` call overloads in 5.6.23 are UHANDLER-only (no `try`/`catch`), so the throw reaches `std::terminate` |

**Implication:** the crash is deterministic for any Lua error raised on this path. It is not a memory-corruption bug; it is an *unhandled error path* in the binary. Your panel is triggering it, but the binary is what turns a catchable Lua error into a host kill.

---

## 2. Why the WER minidumps don't contain the Lua message

The WER dumps you already have are **minidumps with a partial heap**. `luabind::error` does not copy the Lua message into a `std::string`; `what()` resolves it lazily from the Lua state. At fail-fast time the message lives in:

- the Lua **global string table** (`global_State.strt`, interned `TString` objects), and/or
- the **Lua stack** of the faulting `lua_State` (`L->top` at the time of the throw),

neither of which is reliably present in a partial-heap minidump. To recover the exact statement you need either a **full-heap dump** or a **live first-chance break at the throw**.

---

## 3. Three ways to recover the exact Lua statement

Method A is the fastest if it works; Method B is the authoritative live capture; Method C is the authoritative offline capture and matches your existing dump parser.

### Method A — Wrap the callback in `pcall` and print (fastest, panel-level)

If the error originates in your Lua code (or in a binding that raises a Lua error via `lua_error`), a `pcall` inside the callback body sets a `setjmp` that is *nearer* than luabind's own `pcall`, so it will catch the error before luabind can convert it to `luabind::error`.

```lua
local function onEditButton()
    local ok, err = pcall(function()
        -- your existing Editor-button code, unchanged
    end)
    if not ok then
        -- print to Ctrlr's Lua console AND to a file so it survives the host kill
        print("EDIT-CB ERROR: " .. tostring(err))
        local f = io.open("C:/temp/ctrlr_edit_err.txt", "a")
        if f then f:write(os.date("%c"), "  ", tostring(err), "\n"); f:close() end
        error(err)  -- re-raise so behaviour is otherwise unchanged
    end
end
```

- The message is typically of the form `path/to/file.lua:NNN: <message>` — that gives you the exact file and line.
- **Caveat:** if the failing call is a C++ binding that throws a C++ exception *directly* (not via `lua_error`), the Lua-level `pcall` cannot catch it. If the file stays empty, move to Method B or C.

### Method B — Live first-chance break on `luabind::error` in VS2022

This stops the debugger at the `throw` site, *before* `std::terminate`, while the Lua state is still alive.

1. Attach VS2022 to `savihost3.exe` as described in §4.1 (**Native (C/C++)** code type, run VS as Administrator).
2. **Debug → Windows → Exception Settings** (`Ctrl+Alt+E`).
3. Expand **C++ Exceptions**, click **Add Exception…** (the `+`), type **`luabind::error`**, press Enter, and tick its checkbox. This makes VS break on the *first-chance* throw rather than letting it unwind to `terminate`.
4. Reproduce: click the Editor button.
5. VS breaks inside `ctrlr.vst3` at the throw site. The **Exception Helper** window appears and shows the exception type; for `luabind::error` its `what()` returns `lua_tostring(L, -1)`, so the **message text is displayed directly** in the Exception Helper when symbols permit.
6. If the Exception Helper does not show the text (missing symbols for `ctrlr.vst3`), read it manually from the Lua state:
   - In the **Call Stack**, select the `luabind` frame that threw.
   - In **Locals** / **Watch**, locate the `lua_State*` (`L` or the `this` of the `luabind::error` object, which stores the state pointer).
   - Evaluate `lua_tostring(L, -1)` in the **Watch** window (native function evaluation must be enabled and `lua_tostring` must be exported/visible). If function evaluation is unavailable, read `L->top` and the `TValue` below it manually.
7. Fallback if `luabind::error` cannot be resolved by name: break on **`_CxxThrowException`** (public symbols from the Microsoft Symbol Server) and inspect `pExceptionObject` in the frame; the thrown object is the `luabind::error`, from which the `lua_State*` can be recovered.

### Method C — Full-heap ProcDump + your existing dump parser

Because fail-fast bypasses the normal unhandled-exception filter, ProcDump's `-e` (unhandled) may not fire. Capture at **termination** instead, which is guaranteed to happen:

```bat
procdump -accepteula -ma -t -x "C:\Path\To\savihost3.exe"
```

- `-ma` : **full** memory dump — this is the critical flag; it includes the Lua heap.
- `-t`  : write the dump when the process **terminates** (fail-fast always terminates).
- `-x`  : launch `savihost3.exe` under ProcDump so nothing is missed.

If you also want a shot at catching it earlier, add a first-chance trigger on the fail-fast code (verify on your ProcDump version):

```bat
procdump -accepteula -ma -e 1 -f 0xC0000409 -x "C:\Path\To\savihost3.exe"
```

Notes:

- Full dumps of a VST host can be large (hundreds of MB to multiple GB). Ensure free disk space.
- Fail-fast does **not unwind**, so the faulting thread's stack, registers, and the Lua state are intact in the dump.

**Searching the dump with your parser — recommended heuristics, in order:**

1. **Regex over the heap for the Lua source location:** `[A-Za-z0-9_./\\-]+\.lua:\d+:` — Lua errors raised by `error()`/`luaL_error` are prefixed with the chunk name and line. This usually lands on the exact statement.
2. **Common Lua error prefixes:** `attempt to ` (e.g. `attempt to index a nil value`, `attempt to call a nil value`, `attempt to perform arithmetic`), `stack overflow`, `bad argument #`.
3. **Walk the interned string table:** locate `global_State.strt` (a linked list of `TString`) and enumerate candidates matching (1) or (2). Lua interns every string, so the message persists even if the stack slot was overwritten.
4. **Corroborate against your panel source** at the reported `file:line`; the message text and the source line should agree.

If the parser can recover the `lua_State*` from the fail-fast thread's registers/stack (the `luabind::error` object may still be present, since no unwinding occurred), reading `L->top` and `lua_tostring(L, -1)` directly is a stronger confirmation than the heap search.

---

## 4. Reading the debugger for *this* crash (corrected)

### 4.1 Attach (unchanged from v1, still correct)

1. Launch `savihost3.exe` and load the panel.
2. Run **VS2022 as Administrator**.
3. **Debug → Attach to Process…** (`Ctrl+Alt+P`), select `savihost3.exe`.
4. **Attach to:** → **Select…** → **Native (C/C++)** → OK → **Attach**.

### 4.2 What the call stack now looks like

Because the failure is `terminate → abort → __fastfail`, the **top** frames are system frames. Do not be misled by them:

```
[TOP]  ntdll.dll!RtlFailFast2                         <-- fail-fast mechanism
       KernelBase.dll!RaiseFailFastException          <-- 0xC0000409 raised
       ucrtbase.dll!abort                             <-- abort()
       vcruntime140.dll!std::terminate                <-- uncaught C++ exception
       ctrlr.vst3!... (luabind throw path)            <-- FIRST NON-SYSTEM FRAME
       ctrlr.vst3!... (call overload, no try/catch)
       savihost3.exe!... (VST3 bridge / button handler)
```

**Rule (survives the correction):** walk down from the top to the **first non-system frame**. If it is `ctrlr.vst3`, the fault originates in CTRLR — already confirmed by your dumps. The v1 rule "top frame in `ctrlr.vst3`" was slightly imprecise for this crash shape: the *literal* top frame is `ntdll`/`ucrtbase`, and the meaningful frame is the first `ctrlr.vst3` one below the runtime.

### 4.3 Do not apply the v1 `0xC0000005` guidance

- Ignore any advice about null pointers, bad window handles, or off-thread UI calls as the *primary* diagnosis. Those produce `0xC0000005`; you have `0xC0000409`.
- The correct reading of `0xC0000409` + `__fastfail(7)` is: **"an exception reached `std::terminate`."** In this binary, the only mechanism that does that on the Edit-button path is `luabind::error` escaping the `kkClick`/`kkTabChanged` call overloads.
- The `Threads` window is still worth a glance (confirm the throw is on the UI thread), but threading is no longer the leading hypothesis.
- The `Modules` window is still useful: confirm the exact `ctrlr.vst3` build (5.6.23) and check symbol status before attempting Method B.

### 4.4 Exception Helper

For this crash the **Exception Helper** (shown automatically on a first-chance C++ break) is more useful than the exception banner. It reports the exception *type* and, for `luabind::error`, the `what()` text — i.e. the Lua error message you are after.

---

## 5. Mitigation and root-cause direction

- **Panel-level:** wrap every C++-invoked Lua callback (`kkClick`, `kkTabChanged`, and any other `luabind`-called hook) in `pcall`, and log the message to a file. This prevents the host kill for Lua-level errors and is the only defense available without rebuilding the binary.
- **Binary-level (upstream):** the 5.6.23 call overloads should catch `luabind::error` and re-raise via `luaL_error` (or log and swallow), instead of letting the exception reach `std::terminate`. That is a small, targeted fix; worth reporting to the CTRLR maintainers with the dump evidence.
- **Root cause:** once Method A/B/C yields the exact `file:line` and message, fix the offending statement in the panel. The host kill will then disappear.

---

## 6. Quick reference

| Task | Tool / action |
|---|---|
| Confirm crash shape | `0xC0000409`, fail-fast 7, `abort ← terminate`, first non-system frame in `ctrlr.vst3` |
| Fastest message capture | `pcall` around the callback + file log (Method A) |
| Authoritative live capture | VS2022 `Ctrl+Alt+E` → C++ Exceptions → add `luabind::error` → reproduce → Exception Helper / `lua_tostring(L,-1)` (Method B) |
| Authoritative offline capture | `procdump -ma -t -x …` → search heap for `\.lua:\d+:` and `attempt to …` (Method C) |
| Attach for live debug | `Ctrl+Alt+P` → `savihost3.exe` → **Native (C/C++)** |
| Identify culprit module | First non-system frame below `std::terminate` |
| Why WER dumps lack the message | Partial heap; message lives in Lua `strt` / `L->top` |
| Panel-level hardening | `pcall` + log on all luabind-invoked callbacks |
| Upstream fix | try/catch `luabind::error` in `kkClick`/`kkTabChanged` call overloads → `luaL_error` |