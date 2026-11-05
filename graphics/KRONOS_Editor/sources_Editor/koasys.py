"""Éditeur complet OASYS OMNI. Aucune MIDI Implementation de l'OASYS n'est disponible ici : la structure est celle du
KRONOS, moins ce que pcglib (KronosToOasysConverter.cs, carte OASYS vérifiée octet par octet) déclare absent de l'OASYS :
Drum Track (programme et combi), zones de multi-échantillons 5-8, fondus de dynamique 4-7, paramètres Gate des
Mod.Mixer ; plus SGX-2 et EP-1 (moteurs absents de l'OASYS) et la Set List (fonction du KRONOS).
Les OFS des _layout.json sont ceux du KRONOS : correspondance OASYS dans pcglib (docs/OASYS_PARAMETER_MAP.md).
Usage : KFULL_THEME=OASYS_OMNI python koasys.py <dossier> [OBJETS]"""
import os, re, sys
import kfull, kmodel, kdata, kt, themes
from kmodel import Area
kfull.PAGE_NOTE = ('OASYS : structure du KRONOS moins les fonctions absentes de l’OASYS ; OFS = offsets KRONOS. '
                   'Correspondance OASYS : pcglib (KronosToOasysConverter.cs, docs/OASYS_PARAMETER_MAP.md) — '
                   'zone A 0..1291 identique ; KARMA + Common décalés de -12 ; blocs OSC : pas de 466 → 288 ; '
                   'combi : timbres 188 → 186 octets. Global, Song et effets : à vérifier sur un OASYS.')
GATE = re.compile(r'(Threshold|Fixed Value|Control At Note On Only)$')
def oasys_filter(rows):
    out = []
    for r in rows:
        g, n = r['group'], r['name']
        if re.match(r'^Drum Track', g): continue
        if re.match(r'^OSC\d Trigger$', g) and (re.match(r'^Zone[5-8] ', n) or re.match(r'^Zone[4-7] - [5-8] ', n)): continue
        if re.match(r'^(OSC\d |EXi\d )?Mod\.Mixer\d$', g.split(' ', 1)[-1] if g.startswith('OSC') else g) and GATE.search(n): continue
        if re.match(r'^OSC\d Mod\.Mixer\d$', g) and GATE.search(n): continue
        out.append(r)
    return out
_parse = kdata.parse
def parse(fname, single=False, lines=None):
    if fname == 'SetList.txt': return []
    return oasys_filter(_parse(fname, single, lines))
kdata.parse = parse
_eng = kdata.parse_engines
kdata.parse_engines = lambda: {k: v for k, v in _eng().items() if k not in ('SGX-2', 'EP-1')}
kfull.program_areas = (lambda pa: lambda: [a for a in pa() if a.label != 'DRUM TRACK'])(kfull.program_areas)
kfull.combi_areas = (lambda ca: lambda label='Combi': [a for a in ca(label) if a.label != 'DRUM TRACK'])(kfull.combi_areas)

if __name__ == '__main__':
    out = sys.argv[1]; objs = [a.upper() for a in sys.argv[2:]] or ['PROGRAM', 'ENGINES', 'COMBI', 'SONG', 'GLOBAL', 'DRUMKIT', 'WAVESEQ']
    kt.T = next(t for t in themes.ALL if t['id'] == os.environ.get('KFULL_THEME', 'OASYS_OMNI'))
    for o in objs:
        print('==', o, flush=True)
        dict(PROGRAM=kfull.run_program, ENGINES=kfull.run_engines, COMBI=kfull.run_combi, SONG=kfull.run_song,
             GLOBAL=kfull.run_global, DRUMKIT=kfull.run_drumkit, WAVESEQ=kfull.run_waveseq)[o](out)
