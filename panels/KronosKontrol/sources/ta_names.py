r"""1.0a (3 Nov 2026, layout C2) : short names of the Tone Adjust parameters, for the 9 slider screens of the RACK.
Source : Korg's Tone Adjust assignment lists (ctrlr-project/docs/MIDI implementation/SysExParams/VoiceModels/*.txt,
rows « assign type value name »). A program stores one assignment byte per control (Prog_EXi_Common.txt : Fader1-9
Assign at 2666 + 2 i, Knob1-8 Assign at 2586 + 2 i ; code = byte & 0x7F, bit 7 = SUB) ; the panel names it with this
table (generated Lua method kkTaNames, table KK_TA_NAME[engine][code]).
Names are shortened in the style of the hand-made labels of KK_SLD_TA (FLT EG ATK, PICKUP1 LVL…) ; the panel splits
them on 2 lines (kkTa2 in lua/kkMain.lua).
Usage : python ta_names.py   → prints every engine's table (check by eye) ; imported by build_panel.py.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'docs', 'MIDI implementation', 'SysExParams', 'VoiceModels'))
FILES = {1: 'HD-1.txt', 2: 'AL-1.txt', 3: 'CX-3.txt', 4: 'STR-1.txt', 5: 'MS-20EX.txt', 6: 'PolysixEX.txt',
         7: 'MOD-7.txt', 8: 'SGX-1.txt', 9: 'EP-1.txt'}          # 8 = SGX-2 (Korg's file is named SGX-1)
FOOT = ["16'", "5 1/3'", "8'", "4'", "2 2/3'", "2'", "1 3/5'", "1 1/3'", "1'"]   # CX-3 drawbars 1-9
WORDS = {'FILTER': 'FLT', 'ATTACK': 'ATK', 'DECAY': 'DEC', 'SUSTAIN': 'SUS', 'RELEASE': 'REL', 'LEVEL': 'LVL',
         'INTENSITY': 'INT', 'VELOCITY': 'VEL', 'RESONANCE': 'RESO', 'WAVEFORM': 'WAVE', 'FREQUENCY': 'FREQ',
         'OSCILLATOR': 'OSC', 'AMPLITUDE': 'AMP', 'HARMONIC': 'HARM', 'PRESSURE': 'PRES', 'RANDOMNESS': 'RAND',
         'RANDOM': 'RAND', 'NUMBER': 'NUM', 'EXPRESSION': 'EXPR', 'TRANSPOSE': 'TRANSP', 'ENABLE': 'ON',
         'THICKNESS': 'THICK', 'COMMON': 'COM', 'MODULATION': 'MOD', 'POSITION': 'POS', 'DISTANCE': 'DIST',
         'ORIENTATION': 'ORIENT', 'ATTENUATOR': 'ATTEN', 'EFFECT': 'FX', 'VIBRATO': 'VIB', 'PERCUSSION': 'PERC',
         'DRAWBAR': 'DB', 'FEEDBACK': 'FDBK', 'PULSE': 'PULSE', 'BRIGHTNESS': 'BRIGHT', 'RANDOMIZATION': 'RAND',
         'RANDOMIZE': 'RAND', 'SEQUENCE': 'SEQ', 'PORTAMENTO': 'PORTA', 'TREBLE': 'TREB', 'MIDDLE': 'MID',
         'DEPTH': 'DEPTH', 'RESONATOR': 'RESON', 'OFFSET': 'OFS', 'CUTOFF': 'CUTOFF', 'MECHANICAL': 'MECH',
         'SATURATION': 'SAT', 'PERSPECTIVE': 'PERSP', 'STEREO': 'ST', 'PEDAL': 'PED', 'SENSITIVITY': 'SENS', 'START': 'START'}
DROP = {'TIME', 'RELATIVE', 'MACRO', 'TO', 'NUM'}

def short(name, engine):
    m = re.match(r'(Upper|Lower) Drawbar (\d)$', name)
    if m and engine == 3:
        f = FOOT[int(m.group(2)) - 1]
        return f if m.group(1) == 'Upper' else 'L ' + f
    s = name.replace('(', ' ').replace(')', ' ').replace('.', ' ')
    s = s.replace('LFOAMS', 'LFO AMS')
    s = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|(?<=\d)(?=[A-Z])', ' ', s)   # FeedbackDistance, LFO1Intensity
    out = []
    for w in s.upper().split():
        w = WORDS.get(w, w)
        if w in DROP or (w == 'FORM' and out and out[-1] == 'WAVE'): continue
        if w == 'AMS' and out and out[-1] == 'INT': out[-1] = 'AMS'; continue   # « … AMS Intensity » -> … AMS
        if re.fullmatch(r'\d', w) and out and out[-1].isalpha() and len(out[-1]) <= 7:
            out[-1] += w; continue                                         # EG 3 -> EG3, Pickup 1 -> PICKUP1
        out.append(w)
    if out[-2:] == ['AMS', 'INT']: out = out[:-1]
    return ' '.join(out) or name.upper()

def table():
    """{engine: {code: short name}}"""
    res = {}
    for e, f in FILES.items():
        text = open(os.path.join(VOICE, f), encoding='utf-8', errors='replace').read()
        i = text.find('Tone Adjust')
        d = {}
        for line in text[i:].splitlines():
            m = re.match(r'\s*(\d+)\s+(Rel|Abs|-)\s+(\S+)\s+(.+?)\s*$', line)
            if m: d[int(m.group(1))] = 'OFF' if m.group(4) == 'Off' else short(m.group(4), e)
        res[e] = d
    return res

def lua(tab):
    def q(s): return '"%s"' % s.replace('\\', '\\\\').replace('"', '\\"')
    rows = ['KK_TA_NAME = {']
    for e in sorted(tab):
        rows.append('  [%d] = { %s },' % (e, ', '.join('[%d] = %s' % (c, q(n)) for c, n in sorted(tab[e].items()))))
    return '\n'.join(rows) + '\n}\n'

if __name__ == '__main__':
    for e, d in table().items():
        print(FILES[e])
        for c, n in sorted(d.items()): print('  %3d  %s' % (c, n))
