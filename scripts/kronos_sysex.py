"""kronos_sysex.py — fabrication et lecture des messages MIDI / SysEx du Korg KRONOS (OS 3.x).

Module autonome (Python 3, aucune dépendance), tiré du device Max for Live « Kronos Kontrol OS3.2.3 »
(Le grand livre du KRONOS, F. Rossi, oct. 2026). Les numéros de paramètres viennent du MIDI Implementation
officiel (KRONOS_MIDIimp.zip : KRONOS_MIDI_SysEx.txt, CombiAndSongTimbreSet.txt, Prog_HD-1.txt, Prog_EXi_Common.txt).

Ce que le module sait faire :
  - fabriquer les messages : Parameter Change (fonction 43), Mode Change (4E), Mode Request (12),
    sélection de banque / programme (CC0, CC32, Program Change, table « Bank Map KORG »), CC simples ;
  - lire un message reçu du KRONOS : 43 (le KRONOS en envoie quand on touche un paramètre), 4E, 42 Mode Data,
    24 Reply (codes d'erreur) ;
  - donner les identifiants (TYP, SOC, SUB, PID, IDX) des paramètres utilisés et TESTÉS dans Kronos Kontrol.

Envoi réel (facultatif) : `pip install mido python-rtmidi`, puis `send(port_name, msg)` (voir en bas).
Test : `python kronos_sysex.py` vérifie que les octets produits sont ceux du device (qui fonctionne sur le KRONOS).
"""

KORG, MODEL = 0x42, 0x68          # fabricant Korg, modèle KRONOS (le M3 était 0x75 : ne pas confondre)
F_PARAM, F_PARAM_BIN, F_MODE_REQ, F_MODE_DATA, F_MODE_CHANGE, F_REPLY = 0x43, 0x44, 0x12, 0x42, 0x4E, 0x24

MODES = {0: 'COMBINATION', 2: 'PROGRAM', 4: 'SEQUENCER', 6: 'SAMPLING', 7: 'GLOBAL', 8: 'DISK', 9: 'SET LIST'}
REPLY = {0: 'no error', 1: 'parameter type incorrect for current mode', 2: 'unknown parameter id or index',
         3: 'short or mangled message', 4: 'target object not found', 5: 'insufficient resources',
         6: 'value out of range', 7: 'internal error', 64: 'other error', 65: 'target object is protected',
         66: 'memory overflow'}


# ---------------------------------------------------------------- en-tête et valeurs
def header(channel=1):
    """F0 42 3g 68 — g = canal MIDI global du KRONOS moins 1 (canal 1 -> 0x30)."""
    return [0xF0, KORG, 0x30 | ((channel - 1) & 0x0F), MODEL]

def enc21(v):
    """Valeur -> (valueH, valueM, valueL) : entier 21 bits en complément à 2, 7 bits par octet."""
    v &= 0x1FFFFF
    return [(v >> 14) & 0x7F, (v >> 7) & 0x7F, v & 0x7F]

def dec21(h, m, l):
    v = (h << 14) | (m << 7) | l
    return v - (1 << 21) if v & (1 << 20) else v


# ---------------------------------------------------------------- messages à envoyer
def param_change(typ, soc, sub, pid, idx, value, channel=1):
    """Parameter Change (43), forme courte (pid 0..126). Agit sur le mode en cours (Program OU Combi).
    Ne fait aucune écriture : seule la mémoire d'édition change."""
    assert 0 <= pid <= 126, 'pid > 126 : forme longue (dépréciée) non gérée'
    return header(channel) + [F_PARAM, typ, soc, sub, pid, idx] + enc21(value) + [0xF7]

def mode_change(mode, channel=1):
    """Mode Change (4E) : 0 = Combination, 2 = Program, 4 = Sequencer, 9 = Set List… (testé : 0 et 2)."""
    return header(channel) + [F_MODE_CHANGE, mode & 0x0F, 0xF7]

def mode_request(channel=1):
    """Mode Request (12) : le KRONOS répond par Mode Data (42)."""
    return header(channel) + [F_MODE_REQ, 0xF7]

def cc(number, value, channel=1):
    return [0xB0 | ((channel - 1) & 0x0F), number & 0x7F, value & 0x7F]

def program_change(number, channel=1):
    return [0xC0 | ((channel - 1) & 0x0F), number & 0x7F]

# Bank Map KORG (Parameter Guide EN3 p. 764) : (MSB, LSB). Le KRONOS doit être en GLOBAL › Bank Map : KORG.
BANKS = {'I-A': (0, 0), 'I-B': (0, 1), 'I-C': (0, 2), 'I-D': (0, 3), 'I-E': (0, 4), 'I-F': (0, 5),
         'I-G': (121, 0),     # Combi I-G ; en Program, la 7e banque est GM (même adresse 121.00)
         'GM': (121, 0), **{f'g({n})': (121, n) for n in range(1, 10)}, 'g(d)': (120, 0),
         **{f'U-{c}': (0, 8 + i) for i, c in enumerate('ABCDEFG')},
         **{f'U-{c}{c}': (0, 15 + i) for i, c in enumerate('ABCDEFG')}}   # U-AA…U-GG : Program seulement

def select_sound(bank, number, channel=1):
    """Banque + numéro : CC0 (MSB) puis CC32 (LSB) puis Program Change — l'ordre compte."""
    msb, lsb = BANKS[bank]
    return [cc(0, msb, channel), cc(32, lsb, channel), program_change(number, channel)]


# ---------------------------------------------------------------- paramètres utilisés (TYP, SOC, SUB, PID, IDX)
# « T » = testé sur le KRONOS le 16 oct. 2026 ; « D » = d'après la documentation, non testé.
P = {
    # Effets : « Switch » = bypass, VALEUR INVERSÉE (1 = effet coupé). n : 0-11 IFX1-12, 12-13 MFX1-2, 14-15 TFX1-2
    'fx_switch_program':  lambda n: (6, n, 0, 0, 0),    # T (IFX1)
    'fx_switch_combi':    lambda n: (23, n, 0, 0, 0),   # D (même schéma, TYP Combi)
    # Combi : timbre t = 0..15
    'timbre_volume':      lambda t: (4, t, 0, 2, 0),    # T  0-127
    'timbre_pan':         lambda t: (4, t, 0, 1, 0),    # T  0 = RND, 1-127 = L…R, 64 = centre
    'timbre_mute':        lambda t: (4, t, 0, 14, 0),   # D
    'karma_ge_combi':     lambda m: (3, m, 0, 0, 0),    # D  module A-D = 0-3, valeur = n° de GE 0-3583
    # Program (HD-1 : OSC1 = 9, OSC2 = 10 ; EXi : EXi1 = 11, EXi2 = 12)
    'osc_level':          lambda typ: (typ, 3, 0, 6, 0),   # T (HD-1 OSC1) 0-127
    'osc_pan':            lambda typ: (typ, 3, 0, 3, 0),   # D
    'osc_mute':           lambda typ: (typ, 3, 0, 7, 0),   # D
    'drum_track_on':      (0, 0, 0, 10, 0),             # T (v3.2.3) 0/1
    'drum_track_volume':  (0, 0, 0, 39, 0),             # T  0-127
    'drum_track_mute':    (0, 0, 0, 40, 0),             # T  0/1
    'master_volume_prog': (7, 0, 0, 12, 0),             # D  0-127 (Combi : TYP 24)
    'karma_ge_program':   (1, 0, 0, 0, 0),              # D  valeur = n° de GE 0-3583
}

def fx_switch(n, on, mode='program', channel=1):
    """Interrupteur d'effet : on=True allume l'effet (le KRONOS attend la valeur inverse, bypass)."""
    typ = P['fx_switch_program' if mode == 'program' else 'fx_switch_combi'](n)
    return param_change(*typ, 0 if on else 1, channel)


# ---------------------------------------------------------------- lecture d'un message reçu
def parse(msg):
    """Liste d'octets (avec F0…F7) -> dict lisible. Renvoie {'type': 'other'} si ce n'est pas du KRONOS."""
    m = list(msg)
    if len(m) < 5 or m[0] != 0xF0 or m[1] != KORG or m[3] != MODEL or (m[2] & 0xF0) != 0x30:
        return {'type': 'other', 'bytes': m}
    ch, f = (m[2] & 0x0F) + 1, m[4]
    if f == F_PARAM and len(m) >= 14:
        typ, soc, sub, pid, idx = m[5:10]
        return {'type': 'param_change', 'channel': ch, 'id': (typ, soc, sub, pid, idx), 'value': dec21(*m[10:13])}
    if f == F_MODE_CHANGE:
        return {'type': 'mode_change', 'channel': ch, 'mode': m[5] & 0x0F, 'name': MODES.get(m[5] & 0x0F, '?')}
    if f == F_MODE_DATA:
        return {'type': 'mode_data', 'channel': ch, 'mode': m[5] & 0x0F, 'name': MODES.get(m[5] & 0x0F, '?'),
                'option': m[6], 'setup': m[7:10]}
    if f == F_REPLY:
        return {'type': 'reply', 'channel': ch, 'code': m[5], 'text': REPLY.get(m[5], '?')}
    return {'type': 'kronos', 'channel': ch, 'function': f, 'bytes': m}

def hexs(msg):
    return ' '.join(f'{b:02X}' for b in msg)


# ---------------------------------------------------------------- envoi / réception réels (facultatif)
def send(port_name, *msgs):
    import mido                                         # pip install mido python-rtmidi
    with mido.open_output(port_name) as out:
        for msg in msgs:
            out.send(mido.Message('sysex', data=msg[1:-1]) if msg[0] == 0xF0 else mido.Message.from_bytes(msg))

def listen(port_name):
    """Affiche tout ce que le KRONOS envoie (Ctrl+C pour arrêter)."""
    import mido
    with mido.open_input(port_name) as inp:
        for m in inp:
            b = m.bytes()
            print(hexs(b), parse(b) if b[0] == 0xF0 else '')


# ---------------------------------------------------------------- auto-test : octets identiques au device testé
if __name__ == '__main__':
    def same(a, txt):
        assert a == [int(x) for x in txt.split()], (hexs(a), txt)
    same(mode_change(2), '240 66 48 104 78 2 247')                                   # PROG (testé)
    same(fx_switch(0, True), '240 66 48 104 67 6 0 0 0 0 0 0 0 247')                  # IFX1 On (testé)
    same(fx_switch(1, False), '240 66 48 104 67 6 1 0 0 0 0 0 1 247')                 # IFX2 Off (testé)
    same(param_change(*P['timbre_volume'](0), 0), '240 66 48 104 67 4 0 0 2 0 0 0 0 247')
    same(param_change(*P['timbre_pan'](2), 127), '240 66 48 104 67 4 2 0 1 0 0 0 127 247')
    same(param_change(*P['drum_track_mute'], 1), '240 66 48 104 67 0 0 0 40 0 0 0 1 247')
    assert dec21(*enc21(-5)) == -5 and dec21(*enc21(3583)) == 3583
    assert parse(fx_switch(0, True))['id'] == (6, 0, 0, 0, 0)
    assert parse([0xF0, 0x42, 0x30, 0x68, 0x24, 0x02, 0xF7])['text'] == 'unknown parameter id or index'
    assert select_sound('U-A', 0) == [[0xB0, 0, 0], [0xB0, 32, 8], [0xC0, 0]]
    print('OK — exemples :')
    print('  PROG            ', hexs(mode_change(2)))
    print('  IFX1 On         ', hexs(fx_switch(0, True)))
    print('  Timbre 1 vol 100', hexs(param_change(*P['timbre_volume'](0), 100)))
    print('  I-B 000         ', ' | '.join(hexs(x) for x in select_sound('I-B', 0)))
