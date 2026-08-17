"""Sdílecí obrázek 1200×630 — jeden pro celý web.

Vypadá jako titulní strana novin, protože to noviny jsou: papírové
pozadí, tenká linka, jméno a jedna věta. Žádná fotka, žádný stín,
žádný přechod. Sto pět článků nemá vlastní fotku a dosud se sdílely
jako holý odkaz bez náhledu — tohle je to, co se u nich ukáže.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
PAPER = (250, 247, 242)      # --bg z static/style.css
INK = (26, 23, 20)           # --ink
SOFT = (92, 85, 76)          # --ink-soft
LINE = (226, 219, 208)       # --line
ACCENT = (138, 90, 43)       # --accent

F = "/usr/share/fonts/truetype/dejavu/DejaVuSerif%s.ttf"
S = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"
name = ImageFont.truetype(F % "-Bold", 108)
tag = ImageFont.truetype(F % "", 40)
kick = ImageFont.truetype(S % "-Bold", 25)
foot = ImageFont.truetype(S % "", 26)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

M = 92
# horní vlasová linka a nadpisek rubriky, jako v hlavičce webu
d.line([(M, 112), (W - M, 112)], fill=LINE, width=2)
d.text((M, 134), "W O R L D   N E W S ,   E X P L A I N E D", font=kick, fill=ACCENT)

d.text((M, 212), "My Paper", font=name, fill=INK)
d.text((M, 352), "A paper that explains instead of shouting.", font=tag, fill=SOFT)

# dolní linka a adresa — jediné, co si má člověk z náhledu odnést
d.line([(M, 486), (W - M, 486)], fill=LINE, width=2)
d.text((M, 516), "mypaper.news", font=foot, fill=INK)
w = d.textlength("Moje noviny · česky i anglicky", font=foot)
d.text((W - M - w, 516), "Moje noviny · česky i anglicky", font=foot, fill=SOFT)

img.save("static/share.jpg", "JPEG", quality=88, optimize=True, progressive=True)
print("static/share.jpg", img.size)
