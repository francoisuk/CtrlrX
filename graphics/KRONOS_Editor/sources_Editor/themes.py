"""Thèmes des panneaux Kontrol. Chaque thème ne change que l'habillage ; l'implantation est celle du rack KRONOS.
Panneaux retenus (liste ALL, générés par kt.py) :
  KRONOS_KONTROL      — rack d'origine ; logo KRONOS / KONTROL
  OASYS_OMNI          — graphite & TouchView (ancienne proposition B) ; logo OASYS / OMNI
  NAUTILUS_NAVIGATOR  — noir abyssal (ancienne proposition A), arpégiateurs à la place de KARMA ; logo NAUTILUS / NAVIGATOR
Propositions écartées (liste PROPOSITIONS, non générées) : O1 aluminium brossé, O3 argent & bleu vectoriel,
N2 gris AT, N3 noir & bois. N2 et N3 dérivent de N1 : ils en héritent tout ce qu'ils ne redéfinissent pas.
logo() : grand texte, taille ajustée pour une largeur maxi de 140 ; sub() : texte sous le logo (même police et taille
pour KONTROL, OMNI, NAVIGATOR)."""
import txt2path_ext as TP

def logo(text, font, weight, color, ls, maxw=140, maxsize=27, y=131):
    w = TP.width(text, font, weight, maxsize, ls)
    size = round(min(maxsize, maxsize * maxw / w), 2)
    return dict(text=text, font=font, weight=weight, color=color, ls=round(ls * size / maxsize, 2), size=size, y=y)
def sub(color, font='Inter', weight='600', ls=7.2, y=146, size=8.5, text='KONTROL'):
    return dict(text=text, font=font, weight=weight, color=color, ls=ls, size=size, y=y)

KRONOS = dict(  # contrôle : reproduit le rack d'origine
    id='KRONOS_KONTROL', name='KRONOS KONTROL (rack d’origine)',
    face=[(0, '#262628'), (0.5, '#1b1b1d'), (1, '#141415')], ear=[(0, '#18181a'), (1, '#232325')], hole='#d9e3ec',
    div=('#2e2e31', '#0b0b0c'), hline='#2e2e31', label='#d0d0d0', title='#e0e0e0', title_font=('Inter', '700', 10.5, 1),
    num='#d8d8d8', num2='#bdbdbd', small='#d0d0d0',
    btn=[(0, '#3a3a3d'), (1, '#1e1e20')], btn_stroke='#000', btn_text='#f2f2f2', btn_rx=2.5, btn_shadow=0, led_shape='bar',
    lit='#3fb6ff', lit_mode='#ffd23f',
    oled=[(0, '#36b6ff'), (1, '#0f86e0')], oled_text='#04203a', oled_frame='#050608', oled_frame_stroke='#000', oled_glow=True, oled_rx=2,
    knob='kronos', knobg=[(0, '#3c3c3f'), (1, '#09090a')], knobtop=[(0, '#4a4a4e'), (1, '#151517')], knob_ind='#f0f0f0',
    ring='arc', ring_on='#1ea7ff', ring_off='#0e2a40',
    pad=[(0, '#0c1d2e'), (1, '#06101b')], pad_grid='#1d4766', pad_cross='#1ea7ff', pad_frame='#2c2c2f', rail='#555', arrow='#e0e0e0',
    led_on=[(0, '#ff8a80'), (0.5, '#ff1a1a'), (1, '#8a0000')], led_off=[(0, '#5a2a2a'), (1, '#1a0606')], led_bezel='#0a0a0a', led_bezel_stroke='#555',
    karma='#cfe7ff', logo=logo('KRONOS', 'Inter', '300', '#f0f0f0', 3.4), sub=sub('#bdbdbd'),
    pw_frame='#0d0d0e', pw_stroke='#555', pw_rocker='#3a3a3d')

ORANGE = '#ff7a1a'
O1 = dict(KRONOS,
    id='OASYS_A_aluminium_brosse', name='OASYS A — Aluminium brossé, voyants orange, afficheurs ambre',
    face=[(0, '#cfd2d6'), (0.5, '#babec3'), (1, '#a3a7ac')], texture=('brushed', 0.20), sheen=0.22,
    ear=[(0, '#26272a'), (1, '#36373a')], hole='#e6e9ec', top_trim='#eef1f3', bottom_trim='#6f7378',
    div=('#878b90', '#e6e9ec'), hline='#8b8f94', label='#1d1f22', title='#1b1d20', title_font=('Michroma', '400', 9.2, 0.6),
    num='#24262a', num2='#33363a', small='#24262a',
    btn=[(0, '#3e4044'), (1, '#1c1d20')], btn_stroke='#0b0b0c', btn_text='#eef0f2', btn_rx=2, btn_shadow=0.35, btn_hi='#5d6065',
    lit=ORANGE, lit_mode='#ffd23f',
    oled=[(0, '#ffb347'), (1, '#ee8700')], oled_text='#2a1300', oled_frame='#141414', oled_frame_stroke='#000',
    knob='alu', knobg=[(0, '#3a3a3c'), (1, '#0b0b0c')], knobtop=[(0, '#f7f8f9'), (0.6, '#c6c9cd'), (1, '#8d9196')], knob_ind='#141414',
    ring='dots', ring_on=ORANGE, ring_off='#7c8085',
    pad=[(0, '#0f4278'), (1, '#062347')], pad_grid='#3a7cbc', pad_cross='#8fd8ff', pad_frame='#3a3c40', rail='#55585c', arrow='#2a2c30',
    led_on=[(0, '#ffd2a0'), (0.5, '#ff6a00'), (1, '#7a2a00')], led_off=[(0, '#6b5a4a'), (1, '#2a1d12')], led_bezel='#1b1b1c', led_bezel_stroke='#6d7075',
    karma='#24272b', logo=logo('OASYS', 'Michroma', '400', '#16181b', 5), sub=sub('#3a3d42'),
    pw_frame='#1a1a1b', pw_stroke='#5d6065', pw_rocker='#3a3a3d')

O2 = dict(O1,
    id='OASYS_OMNI', name='OASYS OMNI — Graphite brossé, oreilles alu, afficheurs façon TouchView (ancienne proposition B)',
    face=[(0, '#3b3d41'), (0.5, '#2f3135'), (1, '#26282b')], texture=('brushed', 0.10), sheen=0.10,
    ear=[(0, '#a6aaaf'), (1, '#cdd1d5')], hole='#25272a', top_trim='#c9cdd1', bottom_trim='#8d9196',
    div=('#55585d', '#18191b'), hline='#4b4e53', label='#e8eaec', title='#eceef0',
    num='#d6d9dc', num2='#babdc1', small='#d6d9dc',
    btn=[(0, '#9a9ea3'), (1, '#64686d')], btn_stroke='#1a1b1d', btn_text='#101114', btn_hi='#c4c8cc', btn_shadow=0.45,
    oled=[(0, '#e4ebf1'), (1, '#b6c4d1')], oled_text='#13253a', oled_glow=False, oled_gloss=0.12, oled_frame='#0d0e10',
    ring_off='#4a4c50', pad_frame='#5a5d62', rail='#7a7e83', arrow='#d6d9dc', led_bezel='#111', led_bezel_stroke='#5a5d62',
    karma='#dbe3ea', logo=logo('OASYS', 'Michroma', '400', '#eef1f3', 5), sub=sub('#a9adb2', text='OMNI'),
    pw_frame='#111', pw_stroke='#666', pw_rocker='#4a4a4d')

BLUE_V = '#2aa9ff'
O3 = dict(O1,
    id='OASYS_C_argent_bleu_vectoriel', name='OASYS C — Argent, bleu du joystick vectoriel, afficheurs TouchView',
    face=[(0, '#d9dcdf'), (0.5, '#c6c9cd'), (1, '#b0b4b8')], texture=('brushed', 0.16), sheen=0.25,
    lit=BLUE_V, ring='arc', ring_on=BLUE_V, ring_off='#9aa6b1', ring_w=3,
    oled=[(0, '#eef3f7'), (1, '#c3d0dc')], oled_text='#0f2440', oled_glow=False, oled_gloss=0.15, oled_frame='#1a1b1d',
    led_on=[(0, '#c9ecff'), (0.5, '#2aa9ff'), (1, '#063a66')], led_off=[(0, '#3b4a57'), (1, '#121a21')],
    pad_cross='#bfe9ff', logo=logo('OASYS', 'Michroma', '400', '#16181b', 5), sub=sub('#3a3d42'))

TEAL = '#2fd3c5'
N1 = dict(KRONOS,
    id='NAUTILUS_NAVIGATOR', name='NAUTILUS NAVIGATOR — Noir satiné, accents bleu-vert « grand fond » (ancienne proposition A)', right='arp',
    face=[(0, '#202326'), (0.5, '#16181b'), (1, '#0e1012')], texture=('grain', 0.05), sheen=0.07,
    ear=[(0, '#0c0d0f'), (1, '#17191c')], hole='#c9d3dc', top_trim='#3a3f45',
    div=('#2a2e33', '#060708'), hline='#262a2f', label='#e9eef2', title='#e3e9ee', title_font=('Montserrat', '600', 9.5, 1.4),
    num='#cfd6dc', num2='#aab3bb', small='#c8d0d7',
    btn=[(0, '#2c2f33'), (1, '#16181b')], btn_stroke='#000', btn_text='#f1f4f6', btn_rx=4.5, btn_shadow=0.5, btn_hi='#3d4248',
    lit='#e6f7ff', lit_mode='#ff9d2e',
    oled=[(0, '#0f2a33'), (1, '#081a21')], oled_text='#86ece3', oled_glow=False, oled_gloss=0.05, oled_frame='#050607', oled_frame_stroke='#22272c', oled_rx=3.5,
    knob='soft', knobg=[(0, '#2f3236'), (1, '#060708')], knobtop=[(0, '#212428'), (1, '#0e1012')], knob_ind='#f4f6f8',
    ring='arc', ring_on=TEAL, ring_off='#132a2e', ring_w=2.4,
    pad=[(0, '#0b1d23'), (1, '#050d10')], pad_grid='#17454d', pad_cross=TEAL, pad_frame='#2a2e33', pad_rx=6, rail='#3d4248', arrow='#cfd6dc',
    led_on=[(0, '#ffffff'), (0.5, '#9ff0ff'), (1, '#1a6a78')], led_off=[(0, '#203034'), (1, '#0a1214')], led_bezel='#050607', led_bezel_stroke='#3a3f45',
    karma='#9fe9e2', logo=logo('NAUTILUS', 'Montserrat', '300', '#eef2f5', 4.5), sub=sub('#8d979f', text='NAVIGATOR'),
    pw_frame='#08090a', pw_stroke='#3d4248', pw_rocker='#2a2d31')

N2 = dict(N1,
    id='NAUTILUS_B_gris_AT', name='NAUTILUS B — Gris mat (NAUTILUS AT édition limitée), voyants blancs',
    face=[(0, '#7d8186'), (0.5, '#6e7277'), (1, '#5f6368')], texture=('grain', 0.06), sheen=0.10,
    ear=[(0, '#18191b'), (1, '#262729')], hole='#d5dbe0', top_trim='#9a9ea3',
    div=('#55595e', '#8f9398'), hline='#55595e', label='#f4f6f8', title='#ffffff', num='#f0f2f4', num2='#e4e7ea', small='#f0f2f4',
    btn=[(0, '#27292c'), (1, '#111214')], btn_hi='#3a3d41',
    lit='#ffffff', lit_mode='#ff8a2a',
    oled=[(0, '#1c1f23'), (1, '#0e1013')], oled_text='#f2f4f6', oled_frame_stroke='#3a3e43',
    ring_on='#ffffff', ring_off='#4b4f54',
    pad=[(0, '#1b1e22'), (1, '#0c0e10')], pad_grid='#3b4046', pad_cross='#ffffff', pad_frame='#45494e', rail='#3d4146', arrow='#f0f2f4',
    led_on=[(0, '#ffffff'), (0.5, '#e8eef4'), (1, '#6a737c')], led_off=[(0, '#3a3e42'), (1, '#141618')], led_bezel='#0d0e10', led_bezel_stroke='#45494e',
    karma='#ffffff', logo=logo('NAUTILUS', 'Montserrat', '300', '#ffffff', 4.5), sub=sub('#d9dde1'),
    pw_stroke='#45494e')

AMBER = '#ffb35c'
N3 = dict(N1,
    id='NAUTILUS_C_noir_bois', name='NAUTILUS C — Noir, joues en bois noir (modèle 88), accents ambre',
    face=[(0, '#1f1d1c'), (0.5, '#161514'), (1, '#0f0e0d')], texture=('grain', 0.05),
    ear_wood=(58, 44, 36), ear=[(0, '#000'), (1, '#000')], hole='#d9d2c8', top_trim='#3b3733',
    div=('#2e2b28', '#070606'), hline='#2a2724', label='#efe9e2', title='#ece5dc', num='#d8d1c8', num2='#b5ada3', small='#d2cac0',
    lit=AMBER, lit_mode='#ff6b4a',
    oled=[(0, '#22170c'), (1, '#140d06')], oled_text='#ffc580', oled_frame_stroke='#2c2622',
    ring_on=AMBER, ring_off='#2e2216',
    pad=[(0, '#1d140b'), (1, '#0e0905')], pad_grid='#4a3420', pad_cross=AMBER, pad_frame='#2e2b28', arrow='#d8d1c8',
    led_on=[(0, '#fff1d9'), (0.5, '#ffb35c'), (1, '#7a4310')], led_off=[(0, '#3a2c1f'), (1, '#140e08')], led_bezel_stroke='#3b3733',
    karma='#f2d2a8', logo=logo('NAUTILUS', 'Montserrat', '300', '#f3ede6', 4.5), sub=sub('#a39a8f'))

ALL = [KRONOS, O2, N1]          # panneaux retenus (26 oct. 2026)
PROPOSITIONS = [O1, O3, N2, N3]  # propositions écartées, gardées pour mémoire
