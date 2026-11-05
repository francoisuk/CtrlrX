"""Éditeur complet NAUTILUS NAVIGATOR : mêmes pages que le KRONOS, d'après les tables du NAUTILUS
(NAUTILUS_MIDIimp\\SysExDumps). Différences : X-Y Control au lieu du vecteur, RT Controller, scènes 1-4 et Step Seq.
A-D (arpégiateurs / séquenceurs pas à pas) au lieu de KARMA, entrées audio USB, Quick Access, motifs d'arpège ; ni KARMA
ni Drum Track. Usage : KRONOS_MIDIIMP=<SysExDumps du NAUTILUS> KFULL_THEME=NAUTILUS_NAVIGATOR python knaut.py <dossier> [OBJETS]"""
import os, re, sys
import kfull, kmodel, kdata, kt, themes
from kmodel import Area
from kfull import G, link, render_object

def regroup(ps):
    kfull.regroup_common(ps)
    for p in ps:
        m = re.match(r'^Audio USB (\d)$', p.group)
        if m: p.group = 'Audio Inputs'; p.name = f'[USB{m.group(1)}] {p.name}'
    return ps
def program_areas():
    return [Area('GENERAL', G(r'^Common$', r'^Track EQ$')),
            Area('OSC', G(r'^OSC\d (Pitch|Trigger|Drive|Output)$'), ('group', r'OSC(?P<i>\d)', 'OSC'), 'hd1'),
            Area('FILTER', G(r'^OSC\d Filter( A| B| EG| Keyboard Track)?$'), ('group', r'OSC(?P<i>\d)', 'OSC'), 'hd1'),
            Area('AMP', G(r'^OSC\d Amplifier( EG| Keyboard Track)?$'), ('group', r'OSC(?P<i>\d)', 'OSC'), 'hd1'),
            Area('LFO·MIX', G(r'^OSC\d (LFO\d|Mod\.Mixer\d)$'), ('group', r'OSC(?P<i>\d)', 'OSC'), 'hd1'),
            Area('COMMON MOD', G(r'^Pitch EG$', r'^Common LFO$', r'^Common Keyboard Track\d$')),
            Area('EXi', G(r'^EXi\d (Common|Output|Input|Mod\.Mixer\d)$'), ('group', r'EXi(?P<i>\d)', 'EXi'), 'exi'),
            Area('STEP SEQ', G(r'^Common Step Sequence$'), None, 'exi'),
            link('ENGINE', 'ENGINES', 'exi'),
            Area('EFFECTS', G(r'^(Insert Effects|Master Effect\d?|Total Effect\d?|Effect LFO\d)$')),
            link('FX EDIT', 'EFFECTS'),
            Area('X-Y', G(r'^X-Y Control$')),
            Area('CONTROL', G(r'^RT Controller$', r'^Assignable Controller$', r'^Tone Adjust$')),
            Area('SCENES', G(r'^Scene( Common|\s?\d)$')),
            Area('ARP / STEP SEQ', G(r'^Step Seq\. [A-D]$'), ('group', r'Seq\. (?P<i>[A-D])', 'SEQ')),
            Area('AUDIO IN', G(r'^(Audio Input|Audio Inputs)$'))]
def combi_areas():
    return [Area('GENERAL', G(r'^Common$')),
            Area('TIMBRE', G(r'^Timbre\d+$'), ('group', r'Timbre(?P<i>\d+)', 'TIMBRE')),
            Area('EFFECTS', G(r'^(Insert Effects|Master Effect\d?|Total Effect\d?|Effect LFO\d)$')),
            link('FX EDIT', 'EFFECTS'),
            Area('X-Y', G(r'^X-Y Control$')),
            Area('CONTROL', G(r'^RT Controller$', r'^Assignable Controller$')),
            Area('SCENES', G(r'^Scene( Common|\s?\d)$')),
            Area('ARP / STEP SEQ', G(r'^Step Seq\. [A-D]$'), ('group', r'Seq\. (?P<i>[A-D])', 'SEQ')),
            Area('AUDIO IN', G(r'^(Audio Input|Audio Inputs)$'))]
def run_program(out):
    hd = kmodel.load(kdata.parse('Prog_HD-1.txt')); ex = kmodel.load(kdata.parse('Prog_EXi_Common.txt'))
    ps = regroup(hd + [p for p in ex if re.match(r'^(EXi\d|Common Step Sequence)', p.group)])
    render_object(out, 'Program', program_areas(), ps, 'P_', '0 : Program', 'Program', 'obj 00 (Program)')
def run_combi(out):
    ps = regroup(kmodel.load(kdata.parse('CombiAndSongTimbreSet.txt')))
    render_object(out, 'Combi', combi_areas(), ps, 'C_', '1 : Combi', 'Combi', 'obj 01 (Combi)')
def run_global(out):
    ps = kmodel.load(kdata.parse('Global.txt'))
    for p in ps:
        m = re.match(r'^QuickAccess User (\d+)-([A-F])$', p.group)
        if m: p.group = f'QuickAccess User {m.group(1)}'; p.name = f'[{m.group(2)}] {p.name}'
        m = re.match(r'^(Program|Combi) Category (\d+)$', p.group)
        if m: p.group = f'Category {m.group(2)}'; p.name = f'[{m.group(1).upper()}] {p.name}'
    areas = [Area('BASIC', G(r'^(Basic|Special Function|Audio|Manual Info)$')),
             Area('CONTROLLER', G(r'^Controller$')),
             Area('MIDI', G(r'^MIDI$')),
             Area('AUDIO IN', G(r'^(Audio Input \d|USB\s+Input [LR])$')),
             Area('OCTAVE SCALES', G(r'^User Octave Scale \d+$'), ('group', r'Scale (?P<i>\d+)', 'SCALE')),
             Area('ALL NOTE SCALE', G(r'^User All Note Scale$')),
             Area('CATEGORIES', G(r'^Category \d+$'), ('group', r'Category (?P<i>\d+)', 'CATEGORY')),
             Area('QUICK ACCESS', G(r'^QuickAccess$')),
             Area('QUICK USER', G(r'^QuickAccess User \d+$'), ('group', r'User (?P<i>\d+)', 'USER')),
             Area('ASSIGNMENTS', G(r'^Assignments$'))]
    render_object(out, 'Global', areas, ps, 'G_', '3 : Global', 'Global', 'obj 03 (Global)')
def run_arp(out):
    ps = kmodel.load(kdata.parse('ArpPattern.txt'))
    for p in ps:
        m = re.match(r'^Tone (\d+)$', p.group)
        if m: p.group = 'Tones'; p.name = f'[{m.group(1)}] {p.name}'
    areas = [Area('PATTERN', G(r'^(Common|Tones)$')), Area('STEP', G(r'^Step \d+$'), ('group', r'Step (?P<i>\d+)', 'STEP'))]
    render_object(out, 'ArpPattern', areas, ps, 'A_', '— : Arp Pattern', 'Arp Pattern', 'Arp Pattern (ArpPattern.txt)')

if __name__ == '__main__':
    out = sys.argv[1]; objs = [a.upper() for a in sys.argv[2:]] or ['PROGRAM', 'ENGINES', 'COMBI', 'SONG', 'GLOBAL', 'DRUMKIT', 'WAVESEQ', 'SETLIST', 'ARP']
    kt.T = next(t for t in themes.ALL if t['id'] == os.environ.get('KFULL_THEME', 'NAUTILUS_NAVIGATOR'))
    for o in objs:
        print('==', o, flush=True)
        dict(PROGRAM=run_program, ENGINES=kfull.run_engines, COMBI=run_combi, SONG=kfull.run_song, GLOBAL=run_global,
             DRUMKIT=kfull.run_drumkit, WAVESEQ=kfull.run_waveseq, SETLIST=kfull.run_setlist, ARP=run_arp)[o](out)
