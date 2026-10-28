#!/usr/bin/env python3
"""Orthographic assembly views from the supplied STL geometry. Author: Simon Balmer.
Requires Python 3, numpy, Pillow and reportlab. Run from any working directory.
STL meshes are neither repaired nor rotated; explosion offsets affect illustrations only.
"""
from pathlib import Path
import json, math, base64, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
PARTS=json.loads((ROOT/'parts-manifest.json').read_text())['parts']
OUT=ROOT/'assembly'
COLORS={p['id']:p['color'] for p in PARTS};COLORS['D']='#c8cdd2'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def read_stl(p):
 b=Path(p).read_bytes()
 return np.frombuffer(b[84:],dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]))['v'].astype(float)
MESHES={p['id']:read_stl(ROOT/'stl'/p['file']) for p in PARTS}

# Simplified purchased display envelope, measured in the supplied CAD coordinates.
# The display, Pi and button reference STL files are not distributed as print files.
def display_box():
 t=np.deg2rad(10);basis=np.array([[np.cos(t),0,np.sin(t)],[0,1,0],[-np.sin(t),0,np.cos(t)]]).T
 lo=np.array([-13.78975754,-94.5,-57.61245634]);hi=np.array([-4.28975602,94.5,62.3875435])
 v=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]])@basis.T
 f=np.array([[0,1,3],[0,3,2],[4,6,7],[4,7,5],[0,4,5],[0,5,1],[2,3,7],[2,7,6],[0,2,6],[0,6,4],[1,5,7],[1,7,3]])
 return v[f]
MESHES['D']=display_box()

def hexrgb(h):return np.array([int(h[i:i+2],16) for i in (1,3,5)],float)

def render(ids, offsets=None, view=(1,-1.5,.9), size=(1600,1250), pad=.10, zoom=None):
 offsets=offsets or {};W,H=size
 f=np.array(view,dtype=float);f/=np.linalg.norm(f)
 right=np.cross([0.,0.,1.],f);right/=np.linalg.norm(right)
 up=np.cross(f,right)
 matrix=np.array([right,up,f]).T
 tris=[];colors=[];anchors={};edges=[]
 for id in ids:
  v=MESHES[id]+np.array(offsets.get(id,(0,0,0)))
  q=v@matrix
  tris.append(q);colors.append(hexrgb(COLORS[id]))
  anchors[id]=((v.min((0,1))+v.max((0,1)))/2)@matrix
  # Geometric feature edges: discard triangulation diagonals on flat faces.
  uv,iv=np.unique(np.round(v.reshape(-1,3),5),axis=0,return_inverse=True)
  faces=iv.reshape(-1,3); normals=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);nlen=np.linalg.norm(normals,axis=1);normals/=np.maximum(nlen[:,None],1e-15)
  ed={}
  for fi,face in enumerate(faces):
   for a,b in ((face[0],face[1]),(face[1],face[2]),(face[2],face[0])):
    ed.setdefault(tuple(sorted((a,b))),[]).append(fi)
  for (a,b),ns in ed.items():
   if len(ns)!=2 or np.dot(normals[ns[0]],normals[ns[1]])<.83 or (np.dot(normals[ns[0]],f)*np.dot(normals[ns[1]],f)<0):
    edges.append((uv[a]@matrix,uv[b]@matrix))
 allq=np.concatenate(tris).reshape(-1,3);lo=allq.min(0);hi=allq.max(0)
 scale=min(W*(1-pad*2)/(hi[0]-lo[0]),H*(1-pad*2)/(hi[1]-lo[1]))
 if zoom:scale*=zoom
 mid=(lo+hi)/2
 def screen(q):
  q=np.array(q,dtype=float).copy();q[...,0]=(q[...,0]-mid[0])*scale+W/2;q[...,1]=H/2-(q[...,1]-mid[1])*scale;return q
 rgb=np.full((H,W,3),255,dtype=np.uint8);depth=np.full((H,W),-np.inf);owner=np.zeros((H,W),np.uint8)
 light=np.array([.2,.5,.84]);light/=np.linalg.norm(light)
 for id,faces,color in zip(ids,tris,colors):
  n=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-15)
  shades=.66+.34*np.abs(n@light)
  for face,shade in zip(screen(faces),shades):
   minx=max(0,int(np.floor(face[:,0].min())));maxx=min(W-1,int(np.ceil(face[:,0].max())))
   miny=max(0,int(np.floor(face[:,1].min())));maxy=min(H-1,int(np.ceil(face[:,1].max())))
   if minx>maxx or miny>maxy:continue
   a,b,c=face;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-10:continue
   yy,xx=np.mgrid[miny:maxy+1,minx:maxx+1];xx=xx+.5;yy=yy+.5
   u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
   vv=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
   zz=u*a[2]+vv*b[2]+(1-u-vv)*c[2]
   dep=depth[miny:maxy+1,minx:maxx+1];mask=(u>=-1e-6)&(vv>=-1e-6)&(u+vv<=1.000001)&(zz>dep)
   owner[miny:maxy+1,minx:maxx+1][mask]=99 if id=='D' else int(id)
   dep[mask]=zz[mask];rgb[miny:maxy+1,minx:maxx+1][mask]=np.clip(color*shade+255*(1-shade)*.10,0,255).astype(np.uint8)
 for a,b in edges:
  a,b=screen([a,b]);n=max(2,int(np.linalg.norm((b-a)[:2])*2));t=np.linspace(0,1,n);q=a[None,:]+t[:,None]*(b-a)[None,:]
  x=np.rint(q[:,0]).astype(int);y=np.rint(q[:,1]).astype(int);ok=(x>=0)&(x<W)&(y>=0)&(y<H);x=x[ok];y=y[ok];z=q[ok,2]
  ok=z>=depth[y,x]-.9
  rgb[y[ok],x[ok]]=[36,47,56]
 newanchors={}
 for id,p in anchors.items():
  yy,xx=np.where(owner==(99 if id=='D' else int(id)));target=screen(p)[:2]
  if len(xx):
   k=np.argmin((xx-target[0])**2+(yy-target[1])**2);newanchors[id]=[int(xx[k]),int(yy[k])]
  else:newanchors[id]=target.tolist()
 return Image.fromarray(rgb),newanchors,screen,matrix


# Page layout uses 1600 x 1131 design units on A3 landscape.
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
pdfmetrics.registerFont(TTFont('Guide',FONT));pdfmetrics.registerFont(TTFont('GuideBold',BOLD))
PAGE=(1190.551,841.89)
C=None

def line(x1,y1,x2,y2,color='#637687',width=1.2,dash=None):
 C.setStrokeColor(HexColor(color));C.setLineWidth(width);C.setDash(dash or []);C.line(x1,1131-y1,x2,1131-y2);C.setDash([])
def rect(x,y,w,h,color,stroke=None):
 C.setFillColor(HexColor(color));C.setStrokeColor(HexColor(stroke or color));C.rect(x,1131-y-h,w,h,fill=1,stroke=bool(stroke))
def text(x,y,s,size=20,bold=False,color='#203241'):
 C.setFont('GuideBold' if bold else 'Guide',size);C.setFillColor(HexColor(color));C.drawString(x,1131-y-size*.82,s)
def wrap(x,y,s,width=340,size=18,leading=27,color='#526677',bold=False):
 font='GuideBold' if bold else 'Guide';words=s.split();buf='';yy=y
 for word in words:
  test=buf+' '+word if buf else word
  if pdfmetrics.stringWidth(test,font,size)>width and buf:
   text(x,yy,buf,size,bold,color);yy+=leading;buf=word
  else:buf=test
 if buf:text(x,yy,buf,size,bold,color);yy+=leading
 return yy

def image_at(im,x,y,w,h):
 C.drawImage(ImageReader(im),x,1131-y-h,w,h,mask='auto')

def header(section,title,subtitle,page):
 C.saveState();C.scale(PAGE[0]/1600,PAGE[1]/1131)
 rect(0,0,1600,1131,'#ffffff');rect(45,45,7,60,'#7b9b87')
 text(72,44,'JUST ONE MORE MOMENT  /  GEHÄUSE',18,True,color='#657c71')
 text(72,75,title,36,True);text(72,123,subtitle,18,color='#526677')
 line(45,161,1555,161,'#d7dfe4')
 line(45,1063,1555,1063,'#d7dfe4')
 text(45,1086,'Simon Balmer  ·  28.10.2026  ·  '+section,15,color='#627483')
 text(1402,1086,f'{page:02d} / 04',15,True,color='#627483')

def bubble(x,y,label,color='#ffffff',radius=18):
 C.setFillColor(HexColor(color));C.setStrokeColor(HexColor('#314b5b'));C.setLineWidth(1.4);C.circle(x,1131-y,radius,fill=1,stroke=1)
 C.setFillColor(HexColor('#203241'));C.setFont('GuideBold',15);w=pdfmetrics.stringWidth(label,'GuideBold',15);C.drawString(x-w/2,1131-y-5,label)

def annotated(ids,offsets,view,box,guide_pairs=(),padding=.15):
 x,y,w,h=box
 im,anchors,project,mat=render(ids,offsets,view,size=(int(w*1.9),int(h*1.9)),pad=padding)
 # Add dashed assembly axes only in the white space between actual mesh surfaces.
 overlay=im.copy();draw=ImageDraw.Draw(overlay)
 for a,b in guide_pairs:
  q=project(np.array([a,b])@mat);a=q[0,:2];b=q[1,:2];dist=np.linalg.norm(b-a)
  for k in np.arange(0,dist,17):
   p1=a+(b-a)*k/max(dist,1);p2=a+(b-a)*min(k+9,dist)/max(dist,1);draw.line([tuple(p1),tuple(p2)],fill='#a5b3bc',width=2)
 arr=np.array(im);ov=np.array(overlay);white=np.all(arr>248,axis=2);arr[white]=ov[white];im=Image.fromarray(arr)
 image_at(im,x,y,w,h)
 a={id:(x+p[0]/im.width*w,y+p[1]/im.height*h) for id,p in anchors.items()}
 # Keep labels outside the exploded geometry, with a consistent minimum separation.
 sides={-1:[],1:[]}
 for id,p in a.items():sides[-1 if p[0]<x+w*.5 else 1].append((id,p))
 for side,items in sides.items():
  items.sort(key=lambda e:e[1][1]);ys=[p[1] for _,p in items]
  for i in range(1,len(ys)):ys[i]=max(ys[i],ys[i-1]+43)
  if ys and ys[-1]>y+h-30:
   ys=[v-(ys[-1]-(y+h-30)) for v in ys]
  if ys and ys[0]<y+30:ys=[v+y+30-ys[0] for v in ys]
  for (id,p),ly in zip(items,ys):
   lx=x+24 if side<0 else x+w-24
   ex=lx-side*27;line(p[0],p[1],ex,ly,'#526677',1.05);line(ex,ly,lx-side*18,ly,'#526677',1.05)
   C.setFillColor(HexColor('#314b5b'));C.circle(p[0],1131-p[1],2.8,fill=1,stroke=0)
   bubble(lx,ly,'K1' if id=='D' else id,'#eef0f2' if id=='D' else '#ffffff')
 return a

def partrow(id,y,width=330,filename=True):
 p=PARTS[int(id)-1];rect(1200,y+5,7,36,p['color']);bubble(1238,y+22,id,radius=16)
 text(1264,y+7,p['name'],17,True)
 if filename:text(1264,y+32,p['file'],12,color='#6a7c89')
 return y+(66 if filename else 45)

def note(title,body,y):
 text(1200,y,title,19,True);return wrap(1200,y+31,body,width=345,size=17,leading=25)+15

def finish():
 C.restoreState();C.showPage()

def build():
 global C
 C=canvas.Canvas(str(OUT/'assembly-guide.pdf'),pagesize=PAGE)
 C.setAuthor('Simon Balmer');C.setTitle('Just One More Moment - Gehäuse und Explosionszeichnungen');C.setSubject('13 Druckteile: Zuordnung und geometrische Montageübersicht')
 n=np.array([math.cos(math.radians(10)),0,math.sin(math.radians(10))])
 def off(d,z=0):return (n*d+np.array([0,0,z])).tolist()
 # 1: Overall exploded arrangement.
 ids=[p['id'] for p in PARTS]+['D']
 offsets={'01':[0,0,0],'02':[-205,0,-25],'03':[65,0,0],'04':[65,0,0],
 '05':[-48,0,22],'06':[-48,0,-22],'07':off(0,60),'08':off(85,60),'09':off(140,60),
 '10':off(-85,60),'D':off(40,60),'11':[0,0,125],'12':[0,0,178],'13':[55,0,125]}
 header('Gesamtübersicht','Welche Teile gehören zusammen?','Explosionsansicht der 13 Druckteile. Nummern entsprechen den Dateinamen im STL-Ordner.',1)
 annotated(ids,offsets,(1,-1.05,.60),(45,185,1090,815),[
 ([-20,0,-72],[-20,0,205]),([0,0,-130],[0,0,-195]),
 ([-100,0,60],[150,0,104]),([-8,-17,219],[52,-17,219])],padding=.07)
 text(1200,186,'13 TEILE  ·  JE 1× DRUCKEN',19,True)
 yy=227
 for group,title in [('base','BASIS'),('display','DISPLAY'),('camera','KAMERA')]:
  text(1200,yy,title,15,True,color='#738491');yy+=28
  for p in PARTS:
   if p['group']==group:
    bubble(1215,yy+11,p['id'],radius=13);rect(1240,yy+1,5,21,p['color']);text(1256,yy,p['name'],16);yy+=31
  yy+=14
 bubble(1215,yy+10,'K1',radius=13);text(1256,yy,'Touch-Display: Kaufteil',16);yy+=42
 yy=note('Zeichnung lesen','Die Teile sind zur besseren Sicht auseinandergezogen. Gestrichelte Linien ordnen die Einbaulagen zu. Details auf den Folgeseiten.',yy)
 note('Darstellung','Farben dienen der Zuordnung. K1 zeigt das Display schematisch. Weitere Kaufteile und Befestigungsmittel sind ausgeblendet. Kein Massstab.',yy)
 text(65,1021,'Basis → Display → Kamera   /   Abstände der Explosionsansicht sind frei gewählt.',16,color='#657987')
 finish()
 # 2: Display layered assembly.
 ids=['07','08','09','10','D'];offsets={'07':off(0),'10':off(-110),'D':off(60),'08':off(125),'09':off(190)}
 header('Display','Display: von hinten nach vorne','Rückschale 10 → Haupthalter 07 → Touch-Display K1 → Innenrahmen 08 → Aussenrahmen 09.',2)
 guides=[]
 for yy in [-68,68]:
  start=np.array([-5,yy,0]);guides.append(((start+n*(-110)).tolist(),(start+n*190).tolist()))
 annotated(ids,offsets,(1,-1.1,.60),(45,205,1090,685),guides)
 text(1200,190,'DRUCKTEILE',19,True);yy=230
 for id in ['07','08','09','10']:yy=partrow(id,yy)
 bubble(1238,yy+20,'K1',radius=16);text(1264,yy+5,'Raspberry Pi Touch Display 2',16,True);text(1264,yy+32,'Kaufteil, grau und schematisch',14,color='#6a7c89');yy+=81
 yy=note('1  Displayaufnahme','Display mit der sichtbaren Fläche nach vorne in die Aufnahme des Haupthalters 07 setzen. Innenrahmen 08 und Aussenrahmen 09 liegen auf der Vorderseite.',yy)
 note('2  Rückseite schliessen','Pi, Leitungen und Anschlüsse vor dem Schliessen der Rückschale 10 einpassen. Die Montagepunkte sind im STL vorgegeben.',yy)
 rect(65,911,1040,108,'#f2f5f7');wrap(87,930,'K1 zeigt nur den Einbauraum des gekauften Displays. Pi, Kühler und Leitungen sind hier ausgeblendet. Die Zeichnung legt die räumliche Reihenfolge fest; Befestigungsart und Schraubenlängen sind aus STL allein nicht bestimmbar.',width=990,size=18,leading=27)
 finish()
 # 3: Base, rear grommet visible from reverse angle in separate inset.
 ids=['01','02','03','04'];offsets={'01':[0,0,0],'02':[-205,0,0],'03':[70,0,0],'04':[70,0,0]}
 header('Basis','Basis: Blenden, Boden und Kabelauslass','Bodenabdeckung mit rückseitiger Abschlusswand. Separates Detail der Kabeldurchführung.',3)
 annotated(ids,offsets,(1,-1.2,.85),(45,205,1090,530),[
 ([20,-40,-96],[87,-40,-96]),([20,90,-96],[87,90,-96]),([-80,0,-120],[-285,0,-120])])
 text(78,757,'RÜCKSEITIGES DETAIL  /  05 + 06',16,True,color='#667d89')
 annotated(['05','06'],{'05':[0,0,14],'06':[0,0,-14]},(-1,-1.4,.5),(80,786,450,242),[
 ([-109,-69.89,-111],[-109,-69.89,-79])])
 wrap(570,800,'Die beiden Hälften 05 und 06 bilden die Kabeldurchführung an der Rückseite der Basis. Das Kabel vor dem Zusammenfügen einlegen und durch die Öffnung der Bodenabdeckung 02 führen.',width=495,size=18,leading=28)
 text(1200,190,'DRUCKTEILE',19,True);yy=230
 for id in ['01','02','03','04','05','06']:yy=partrow(id,yy)
 yy=note('1  Front vorbereiten','Zierleisten 03 und 04 an der Front zuordnen. Taster und beide Schalter in die passenden Öffnungen einsetzen.',yy)
 yy=note('2  Kabelauslass einsetzen','05 oben und 06 unten an der rückseitigen Durchführung anordnen. Original-Suffix L liegt im CAD oben.',yy)
 note('3  Boden schliessen','Innenraum und Leitungswege prüfen. Bodenabdeckung 02 mit ihrer Abschlusswand an der Rückseite des Basisgehäuses 01 ausrichten.',yy)
 finish()
 # 4: Camera.
 ids=['11','12','13'];offsets={'11':[0,0,0],'12':[0,0,48],'13':[44,0,0]}
 header('Kamera','Kamera: zwei Schalen und ein Frontring','Unterschale 11 und Oberschale 12 umschliessen die Kamera. Ring 13 sitzt vor der Objektivöffnung.',4)
 annotated(ids,offsets,(1,-1.15,.85),(45,205,1090,690),[
 ([-25,0,73],[-25,0,164]),([-3,-16.9,92.9],[43,-16.9,92.9])])
 text(1200,190,'DRUCKTEILE',19,True);yy=230
 for id in ['11','12','13']:yy=partrow(id,yy)
 yy=note('1  Webcam einpassen','Die Logitech-C270-Kamera gehört zwischen die beiden Schalen. Objektiv und Mikrofonöffnung müssen zu den Öffnungen an der Vorderseite zeigen.',yy)
 yy=note('2  Schalen zusammenfügen','Unterschale 11 am Displaygehäuse ausrichten und Kamera einsetzen. Oberschale 12 von oben aufsetzen; USB-Leitung freihalten.',yy)
 yy=note('3  Ring zuordnen','Frontring 13 von vorne an der grossen Objektivöffnung ausrichten. Die Stellung entspricht den gemeinsamen CAD-Koordinaten.',yy)
 note('Befestigung','Die STL-Dateien definieren Form und Lage. Kamerazerlegung, Schrauben, Klebung und Druckprofil sind nicht durch die Dateien festgelegt.',yy)
 rect(65,918,1040,101,'#eef4ef');wrap(87,936,'Druckumfang: 13 einzelne STL-Dateien, jeweils 1×. Gesamtbaugruppe, Pi-, Taster- und Display-Platzhalter gehören nicht auf die Druckplatte. Für alle Teile dieselbe Skalierung verwenden: 100 %, Einheit mm.',width=992,size=18,leading=27)
 finish();C.save()
 # Publish the illustrated pages as ordinary PNGs for GitHub and chat preview.
 import fitz
 doc=fitz.open(OUT/'assembly-guide.pdf')
 names=['exploded-overview','display-assembly','base-assembly','camera-assembly']
 for page,name in zip(doc,names):
  pix=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False);pix.save(OUT/(name+'.png'))
 print('Created four-page assembly guide and four illustrated PNGs.')

if __name__=='__main__':build()
