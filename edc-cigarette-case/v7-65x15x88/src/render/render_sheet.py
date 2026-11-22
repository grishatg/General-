"""Compose v7_a1_sheet.png (4 views) and v7_a1_plate.png (A1 plate layout) from the Playwright screenshots.
Usage (from v7-65x15x88/):  python3 src/render/render_sheet.py <render_dir>
Needs <render_dir>/v7_{front,open,back,base}.png (made by src/render/shot7.js) and DejaVu fonts (/usr/share/fonts/truetype/dejavu)."""
import sys, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import v7_a1_export as AX

rd = sys.argv[1]
fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
fr = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
pos = AX.layout(); S = 2.6
img = Image.new('RGB', (int(256 * S) + 40, int(256 * S) + 70), (236, 234, 228)); d = ImageDraw.Draw(img)
ox, oy = 20, 50; T = lambda x, y: (ox + x * S, oy + (256 - y) * S)
d.text((20, 12), 'Bambu Lab A1 — one plate, print by object (256 × 256 mm)', fill=(30, 30, 30), font=fb)
d.rectangle([T(0, 256), T(256, 0)], outline=(90, 90, 90), width=2, fill=(214, 212, 206))
for name, (cx, cy), (w, h), col in [('COVER  grey + yellow', pos['cover'], (65, 88), (157, 161, 163)),
                                    ('TRAY  black + yellow', pos['tray'], (65, 88), (40, 40, 42)),
                                    ('SLEEVE', pos['sleeve'], (5, 5), (255, 208, 11))]:
    d.rectangle([T(cx - w / 2, cy + h / 2), T(cx + w / 2, cy - h / 2)], fill=col, outline=(20, 20, 20))
    d.text((T(cx - w / 2, cy + h / 2)[0], T(cx - w / 2, cy + h / 2)[1] - 18), name, fill=(30, 30, 30), font=fr)
d.line([T(73, 60), T(147, 60)], fill=(200, 60, 40), width=2); d.text(T(92, 66), '74 mm ≥ 73 mm clearance', fill=(200, 60, 40), font=fr)
d.text((20, int(256 * S) + 52), 'order: cover → tray → sleeve · all parts < 25 mm rod height · no prime tower (A1 purges to chute)', fill=(70, 70, 70), font=fr)
img.save(f'{rd}/v7_a1_plate.png')

ims = [Image.open(f'{rd}/v7_{v}.png').resize((400, 520)) for v in ['front', 'open', 'back', 'base']]
s = Image.new('RGB', (1600, 576), (236, 234, 228)); dd = ImageDraw.Draw(s)
ft = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
t = 'v7 · 65 × 15 × 88 mm · Bambu A1'; dd.text((14, 10), t, fill=(30, 30, 30), font=ft)
dd.text((14 + dd.textlength(t, font=ft) + 18, 16), 'one plate · by object · snap-in magnets · 4-layer yellow · test-sliced ≈ 4 h', fill=(70, 70, 70), font=fr)
for i, im in enumerate(ims): s.paste(im, (i * 400, 56))
s.save(f'{rd}/v7_a1_sheet.png')
print('wrote', f'{rd}/v7_a1_plate.png', f'{rd}/v7_a1_sheet.png')
