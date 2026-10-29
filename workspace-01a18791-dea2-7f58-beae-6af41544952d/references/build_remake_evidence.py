#!/usr/bin/env python3
"""Assemble *captured* reference and Studio frames (no synthetic imagery)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import shutil
ROOT=Path('/home/user')
OUT=ROOT/'remake_evidence'
OUT.mkdir(exist_ok=True)
shots={
 'R5_COLD_Studio.jpg':'aa4c682820744020888930f95af9dcdc',
 'R5_STARTUP_PRIME_Studio.jpg':'83a6ab80ab294e1cb670bf784882d87e',
 'R5_STARTUP_FUSION_Studio.jpg':'5b98af2cd397421d992423f56700c88d',
 'R5_ONLINE_Studio.jpg':'3e0a5df398bb45cba49a4ac0f57b168b',
 'R5_MELTDOWN_244_Studio.jpg':'680f565761244d6cb41f65463cd9527f',
}
for dst,job in shots.items():
    shutil.copy2(ROOT/f'studio_bridge/broker_results/{job}_1.jpg',OUT/dst)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
    note=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
except OSError:
    title=ImageFont.load_default();note=title


def card(src,heading,width=610,height=355):
    art=Image.open(src).convert('RGB')
    art=ImageOps.contain(art,(width,height),Image.Resampling.LANCZOS)
    img=Image.new('RGB',(width,height+43),(19,24,36))
    img.paste(art,((width-art.width)//2,43+(height-art.height)//2))
    d=ImageDraw.Draw(img)
    d.text((13,10),heading,fill=(244,244,249),font=title)
    return img

cards=[
 card(OUT/'R5_COLD_Studio.jpg','COLD — yıldız ve ışınlar kapalı'),
 card(OUT/'R5_STARTUP_PRIME_Studio.jpg','STARTUP — soğutma hazırlığı'),
 card(OUT/'R5_STARTUP_FUSION_Studio.jpg','STARTUP — füzyon ateşlemesi'),
 card(OUT/'R5_MELTDOWN_244_Studio.jpg','MELTDOWN — 244. saniye önizlemesi'),
]
GAP=16;PAD=20
sheet=Image.new('RGB',(PAD*2+610*2+GAP,PAD*2+398*2+GAP+28),(15,20,31))
for i,c in enumerate(cards):
    sheet.paste(c,(PAD+(i%2)*(610+GAP),PAD+(i//2)*(398+GAP)))
ImageDraw.Draw(sheet).text((PAD,PAD+398*2+GAP+4),
 'Gerçek Studio Play yakalamaları; başlangıç ve meltdown önizlemeleri test sonrası kapatıldı.',
 fill=(182,194,215),font=note)
sheet.save(OUT/'R5_Durum_Sekansi.png',optimize=True)

comparison=Image.new('RGB',(PAD*2+610*2+GAP,PAD*2+398+49),(15,20,31))
ref=card(ROOT/'uploads/image-2.png','Referans — A Core Game (video karesi)')
ours=card(OUT/'R5_MELTDOWN_244_Studio.jpg','Studio — remake R5 / t≈244 s')
comparison.paste(ref,(PAD,PAD));comparison.paste(ours,(PAD+610+GAP,PAD))
ImageDraw.Draw(comparison).text((PAD,PAD+398+16),
 'Farklı kamera açıları ve kaynak çözünürlüğü; birebir varlık eşlemesi iddia edilmez.',
 fill=(182,194,215),font=note)
comparison.save(OUT/'Referans_ve_R5_Meltdown.png',optimize=True)
print('Evidence written to',OUT)
