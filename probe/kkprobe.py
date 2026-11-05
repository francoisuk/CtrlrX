#!/usr/bin/env python3
"""Run CtrlrPanelProbe on a Kronos Kontrol panel and print a short summary.

    python kkprobe.py [script.json] [--panel PATH] [--out NAME]

Writes the raw report to out/<NAME>.json (bytes exactly as the probe printed them).
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, 'b', 'Tests', 'CtrlrPanelProbe.exe')
PANEL = os.path.join(HERE, '..', 'panels', 'KronosKontrol', 'KronosKontrol_1.0h.panel')


def main():
    args = sys.argv[1:]
    panel, out, script = PANEL, None, None
    while args:
        a = args.pop(0)
        if a == '--panel':
            panel = args.pop(0)
        elif a == '--out':
            out = args.pop(0)
        else:
            script = a
    out = out or (os.path.splitext(os.path.basename(script))[0] if script else 'noscript')
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    cmd = [PROBE, '--global-console', panel] + ([script] if script else [])
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, cwd=HERE, timeout=900)
    dt = time.time() - t0
    raw = os.path.join(HERE, 'out', out + '.json')
    with open(raw, 'wb') as f:
        f.write(p.stdout)
    print(f'exit={p.returncode} time={dt:.0f}s report={raw}')
    r = json.loads(p.stdout.decode('utf-8'))
    summarize(r)


def summarize(r):
    pn = r.get('panel', {})
    print('panel:', {k: v for k, v in pn.items() if not isinstance(v, (list, dict))})
    print('dialogs:', pn.get('dialogs'))
    errs, warns = r.get('errors', []), r.get('warnings', [])
    print(f'errors: {len(errs)}')
    for e in errs[:15]:
        print('   ', json.dumps(e, ensure_ascii=False)[:300])
    print(f'warnings: {len(warns)}')
    for w in warns[:15]:
        print('   ', json.dumps(w, ensure_ascii=False)[:300])
    mods = r.get('finalState', {}).get('modulators', [])
    print(f'modulators: {len(mods)}')
    for i, s in enumerate(r.get('steps', [])):
        rv = s.get('returnValue')
        extra = {k: s[k] for k in ('screenshot', 'paint', 'mouse') if k in s}
        midi = s.get('deviceMidiOut') or []
        print(f'step {i} {s.get("action")}: rv={json.dumps(rv, ensure_ascii=False)[:400]} '
              f'midiOut={len(midi)} {json.dumps(extra)[:200]} '
              f'errors={len(s.get("errors", []))} console={len(s.get("console", []))}')
        for e in s.get('errors', [])[:5]:
            print('      err', json.dumps(e, ensure_ascii=False)[:300])
        for m in midi[:4]:
            print('      out', json.dumps(m)[:200])
    con = r.get('console', [])
    print(f'console lines: {len(con)}')
    for c in con[:25]:
        print('   ', str(c)[:200])


if __name__ == '__main__':
    main()
