#!/usr/bin/env python3
"""Unretouched, time-matched screenshot comparison of reference and Studio.

Reference labels are video clock time. Studio labels are seconds since the
start of its scripted MELTDOWN. 11:49 + 92/244/338 seconds gives the same
nominal event timestamp; original screenshots are shown in full, including
YouTube's interface on the reference side. No recoloring, crops or AI art.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import shutil
root=Path('/home/user')
out=root/'remake_evidence'/'matched_comparison'
out.mkdir(parents=True,exist_ok=True)
rows=[
 ('13_21_t092_chamber','uploads/image-3.png',
  'studio_bridge/broker_results/f8ac0089d629452cbc481945ca313097_1.jpg',
  'REFERANS 13:21  |  meltdown +92 sn',
  'STUDIO t=92 sn  |  yakın reaktör'),
 ('15_53_t244_room','uploads/image-2.png',
  'studio_bridge/broker_results/395194bc45ac4f9e8a5b37c214375099_1.jpg',
  'REFERANS 15:53  |  meltdown +244 sn',
  'STUDIO t=244 sn  |  çapraz kontrol odası'),
 ('17_27_t338_window','uploads/image-8.png',
  'studio_bridge/broker_results/a9fdfe44715c4192a7b13fb4cf342c90_1.jpg',
  'REFERANS 17:27  |  meltdown +338 sn',
  'STUDIO t=338 sn  |  pencere önü'),
]
try:
 bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
 small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
except OSError:
 bold=ImageFont.load_default();small=bold

PW,PH=642,365
PAD,GAP=18,15
TITLE=42
FOOT=36
COLOR=(15,21,32)

def panel(path,label):
    im=Image.open(path).convert('RGB')
    scaled=ImageOps.contain(im,(PW,PH),Image.Resampling.LANCZOS)
    p=Image.new('RGB',(PW,PH+TITLE), (20,27,40))
    p.paste(scaled,((PW-scaled.width)//2,TITLE+(PH-scaled.height)//2))
    d=ImageDraw.Draw(p)
    d.text((12,10),label,font=bold,fill=(245,247,250))
    return p

all_img=Image.new('RGB',(PAD*2+2*PW+GAP, PAD*2+3*(PH+TITLE+FOOT)+2*GAP),COLOR)
for idx,(slug,ref,studio,rl,sl) in enumerate(rows):
    shutil.copy2(root/studio,out/f'R5_{slug}.jpg')
    refp=panel(root/ref,rl)
    studp=panel(root/studio,sl)
    one=Image.new('RGB',(PAD*2+2*PW+GAP, PAD*2+PH+TITLE+FOOT),COLOR)
    one.paste(refp,(PAD,PAD))
    one.paste(studp,(PAD+PW+GAP,PAD))
    d=ImageDraw.Draw(one)
    d.text((PAD,PAD+PH+TITLE+12),
       'Aynı meltdown süresi; farklı oyun, yaklaşık kamera açısı. Tam kareler gösterildi; renk düzenleme veya kesme yapılmadı.',
       font=small,fill=(184,198,218))
    one.save(out/f'Karsilastirma_{slug}.png',optimize=True)
    all_img.paste(one.crop((0, PAD, one.width, PAD+PH+TITLE+FOOT)),
                  (0,PAD+idx*(PH+TITLE+FOOT+GAP)))
all_img.save(out/'Uc_Es_Zamanli_Kare.png',optimize=True)
print('Matched comparison:',out)
for p in sorted(out.iterdir()):print(p.name,p.stat().st_size)
