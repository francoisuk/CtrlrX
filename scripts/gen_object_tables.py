# gen_object_tables.py — tables éditeur E6 (Drum Kit / Wave Seq / Global)
# depuis kronos-pcglib/docs/midi_korg/{DrumKit,WaveSequence,Global}.txt (parseur kmap).
# Normalisations par rapport aux tables reference/ref-kronos/tables (même forme de ligne) :
#  - pieces 'lo~hi' inversés (hi < lo, ex. '0~7' relu (7,0) par kmap._bits) -> (min, max)
#  - section vide + nom non vide -> hérite de la dernière section non vide (forward-fill)
#  - espaces multiples dans les sections réduits à un seul ('USB    Input L' -> 'USB Input L')
#  - ids normalisés à 6 éléments (note à l'index 5 ; DrumKit = colonne 'note', autres = '')
# Sortie : ctrlr-project/scripts/tables/{DrumKit,WaveSequence,Global}.json
# Usage : python gen_object_tables.py   (depuis ctrlr-project/scripts)
import sys, os, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r'C:\Korg\kronos-corpus\kronos-pcglib\scripts')
import kmap

OUT = os.path.join(HERE, 'tables')
# (fichier, index de la colonne 'note' dans le reste — DrumKit = 0, autres = None)
FILES = [('DrumKit.txt', 0), ('WaveSequence.txt', None), ('Global.txt', None)]

os.makedirs(OUT, exist_ok=True)
for fn, note_at in FILES:
    rows = kmap.parse_rows(open(os.path.join(kmap.DOC, fn), encoding='latin-1'), [3, 4])
    out, last_sec, nswap, nff = [], '', 0, 0
    for r in rows:
        pcs = [[o, lo, hi] for o, lo, hi in r['pieces']]
        pcs2 = [[o, min(lo, hi), max(lo, hi)] for o, lo, hi in pcs]
        if pcs2 != pcs:
            nswap += 1
        r['pieces'] = pcs2
        if not r['sec'] and r['name'] and r['name'] != '*':
            r['sec'] = last_sec                    # forward-fill
            nff += 1
        elif r['sec']:
            last_sec = r['sec']
        r['sec'] = re.sub(r'\s+', ' ', r['sec']).strip()
        rest = list(r.get('ids') or [])
        note = rest[note_at] if note_at is not None and len(rest) > note_at else ''
        r['ids'] = ['', '', '', '', '', note]
        out.append({'sec': r['sec'], 'name': r['name'], 'pieces': r['pieces'],
                    'data': r['data'], 'value': r['value'], 'ids': r['ids']})
    dst = os.path.join(OUT, fn[:-4] + '.json')
    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('%s -> tables/%s : %d lignes (pieces inversés %d, forward-fill %d)'
          % (fn, fn[:-4] + '.json', len(out), nswap, nff))
