#!/usr/bin/env python3
"""Measure native-frame color occupancy and inspect original-image sequences.

Offline reference study only. Video can be removed from .cache; no modified
interpolated frames or claims about Roblox Play images are produced.
"""
from __future__ import annotations
from pathlib import Path
import cv2,json,numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
VIDEO=ROOT.parent/'.cache/reference_original.mp4'
OUT=ROOT/'reference'
OUT.mkdir(exist_ok=True)
STAGES={
 'standing_bodies':(109.0,113.0,1.0),
 'fuel_cloud':(117.0,124.0,.7),
 'lit_nozzles_dark_volume':(132.0,138.5,.55),
 'cyan_expansion':(139.10,141.90,.22),
 'white_corona_growth':(142.0,155.0,1.0),
 'white_corona_breakup':(158.0,169.0,1.0),
}


def frame_at(capture,t):
 capture.set(cv2.CAP_PROP_POS_MSEC,t*1000)
 ok,frame=capture.read()
 if not ok:raise RuntimeError(('Failed seek',t))
 return frame

def profile(frame):
 # One fixed control-glass composition; upper panel is excluded. Natural
 # black level in a compressed screen recording isn't literal zero.
 chamber=frame[260:665,205:1075]
 core=frame[365:630,455:825]
 lower=frame[480:660,290:1000]
 hsv=cv2.cvtColor(chamber,cv2.COLOR_BGR2HSV)
 cH,cS,cV=cv2.split(hsv)
 wc=cv2.cvtColor(core,cv2.COLOR_BGR2HSV)
 lc=cv2.cvtColor(lower,cv2.COLOR_BGR2HSV)
 return dict(
  dark_fraction=float(np.mean(np.max(chamber,axis=2)<27)),
  cyan_fraction=float(np.mean((cH>=82)&(cH<=105)&(cS>=65)&(cV>=95))),
  bright_white_fraction=float(np.mean((wc[:,:,1]<67)&(wc[:,:,2]>215))),
  lower_neutral_vapor_fraction=float(np.mean((lc[:,:,1]<62)&(lc[:,:,2]>76)&(lc[:,:,2]<210))),
  chamber_med_luma=float(np.median(cv2.cvtColor(chamber,cv2.COLOR_BGR2GRAY))),
 )

def sheet(capture,name,start,finish,step):
 times=np.arange(start,finish+.0001,step)
 imgs=[]
 for t in times:
  frame=frame_at(capture,float(t))
  img=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
  img.thumbnail((426,341))
  imgs.append((float(t),img,profile(frame)))
 cols=3
 rows=(len(imgs)+cols-1)//cols
 sheet=Image.new('RGB',(cols*426,rows*365),(18,18,24))
 pen=ImageDraw.Draw(sheet)
 for n,(t,img,p) in enumerate(imgs):
  x=n%cols*426;y=n//cols*365
  sheet.paste(img,(x,y))
  pen.text((x+8,y+341),f'{t:6.2f}s  dark {p["dark_fraction"]:.2f}  cyan {p["cyan_fraction"]:.2f}',fill='white')
 file=OUT/f'.{name}_inspection.jpg'
 sheet.save(file,quality=85)
 return str(file)

def main():
 assert VIDEO.exists()
 cap=cv2.VideoCapture(str(VIDEO))
 assert cap.isOpened()
 readings={}
 sheets=[]
 for name,(start,end,step) in STAGES.items():
  data=[]
  for t in np.arange(start,end+.0001,step):
   p=profile(frame_at(cap,float(t)))
   data.append({'video_time':round(float(t),3),**p})
  readings[name]=data
  sheets.append(sheet(cap,name,start,end,step))
 cap.release()
 # Keep only machine-readable feature ranges; contact sheets are INTERNAL
 # scratch under hidden filenames and can be discarded after review.
 result={
  'source':VIDEO.name,'measured_in_original_video_time':True,
  'not_roblox_render':True,'segments':{
   name:{'frames_selected':len(rows),
         'color_range':{k:[round(min(r[k] for r in rows),3),
                            round(max(r[k] for r in rows),3)]
           for k in rows[0] if k!='video_time'}}
   for name,rows in readings.items()},
  'sheets':sheets,
 }
 (OUT/'visual_characteristics.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
