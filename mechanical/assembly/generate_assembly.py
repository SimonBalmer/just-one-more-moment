#!/usr/bin/env python3
"""Orthographic assembly views from the supplied STL geometry. Author: Simon Balmer.
Requires Python 3, numpy, Pillow and reportlab. Run from any working directory.
STL meshes are neither repaired nor rotated; explosion offsets affect illustrations only.
"""
from pathlib import Path
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
PARTS=json.loads((ROOT/'parts-manifest.json').read_text())['parts']
OUT=ROOT/'assembly'
COLORS={p['id']:p['color'] for p in PARTS};COLORS.update(D='#c7c7c7',P='#656565',C='#656565',B='#111111',S='#656565',T='#656565',L='#111111')
REF_LABELS={'D':'E1','P':'E2','C':'E3','B':'E4','S':'E5','T':'E6','L':'E7'}
OWNER_IDS={'D':91,'P':92,'C':93,'B':94,'S':95,'T':96,'L':97}
FACE_COLORS={}
FONT=os.environ.get('JOMM_MONO_FONT','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
BOLD=os.environ.get('JOMM_MONO_BOLD_FONT','/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf')

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


# Purchased components are illustration geometry only. No reference STL is published.
# E1 and E2 use the original CAD reference envelopes. E3 is approximate.
def box(lo,hi,basis=None):
 lo=np.array(lo);hi=np.array(hi)
 v=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]])
 if basis is not None:v=v@basis.T
 f=np.array([[0,1,3],[0,3,2],[4,6,7],[4,7,5],[0,4,5],[0,5,1],[2,3,7],[2,7,6],[0,2,6],[0,6,4],[1,5,7],[1,7,3]])
 return v[f]

def cylinder(x0,x1,y,z,r,steps=40):
 angles=np.linspace(0,2*np.pi,steps,endpoint=False);a=np.stack([np.full(steps,x0),y+r*np.cos(angles),z+r*np.sin(angles)],axis=1);b=a.copy();b[:,0]=x1
 faces=[]
 for i in range(steps):
  j=(i+1)%steps;faces.extend([[a[i],a[j],b[j]],[a[i],b[j],b[i]],[[x0,y,z],a[j],a[i]],[[x1,y,z],b[i],b[j]]])
 return np.array(faces,float)

def rounded_body(x0,x1,y0,y1,z0,z1,r=4):
 yz=[]
 for y,z,start in [(y1-r,z1-r,0),(y0+r,z1-r,90),(y0+r,z0+r,180),(y1-r,z0+r,270)]:
  for a in np.deg2rad(np.linspace(start,start+90,8,endpoint=False)):yz.append([y+r*np.cos(a),z+r*np.sin(a)])
 a=np.array([[x0,y,z] for y,z in yz]);b=a.copy();b[:,0]=x1;faces=[];cy=(y0+y1)/2;cz=(z0+z1)/2
 for i in range(len(a)):
  j=(i+1)%len(a);faces.extend([[a[i],a[j],b[j]],[a[i],b[j],b[i]],[[x0,cy,cz],a[j],a[i]],[[x1,cy,cz],b[i],b[j]]])
 return np.array(faces,float)

def component(id,segments):
 MESHES[id]=np.concatenate([v for v,c in segments]);FACE_COLORS[id]=np.concatenate([np.tile([int(c[i:i+2],16) for i in (1,3,5)],(len(v),1)) for v,c in segments])

# Display front is black; its rear envelope is grey.
FACE_COLORS['D']=np.tile([199,199,199],(len(MESHES['D']),1));FACE_COLORS['D'][2:4]=[17,17,17]
t=np.deg2rad(10);BASIS=np.array([[np.cos(t),0,np.sin(t)],[0,1,0],[-np.sin(t),0,np.cos(t)]]).T
component('P',[
 (box([-12.8,-45,-28.5],[-10.78975657,45,28.5],BASIS),'#c7c7c7'),
 (box([-34,-24,-22],[-12.8,24,22],BASIS),'#656565'),
 (box([-35.78975712,-12,-11],[-34,12,11],BASIS),'#111111'),
 (box([-22,-41,-25],[-12.8,-37,25],BASIS),'#111111'),
 (box([-29,34,-25],[-12.8,45,-6],BASIS),'#999999'),
 (box([-29,34,4],[-12.8,45,23],BASIS),'#999999')])
component('C',[
 (rounded_body(-38,-9,-36,36,80.5,105.5),'#656565'),
 (cylinder(-10,-4.8,-16.9,92.9,13.5),'#111111'),
 (cylinder(-4.8,-4.5,-16.9,92.9,9.5),'#999999'),
 (cylinder(-4.5,-4.2,-16.9,92.9,6.5),'#111111'),
 (cylinder(-9,-8.5,23,92.9,1.7),'#111111')])

# Front control centres are measured from the supplied openings/reference model.
# Toggle shapes are symbols. The guide assigns SW01 to the left hole and SW02
# to the right hole. Match these names to hardware/WIRING.md when wiring.
BUTTON_Y=68.1465;CONTROL_Z=-96.91578
component('B',[
 (cylinder(-5,19,BUTTON_Y,CONTROL_Z,13.8),'#656565'),
 (cylinder(19,22,BUTTON_Y,CONTROL_Z,17.0),'#111111'),
 (cylinder(22,24,BUTTON_Y,CONTROL_Z,15.0),'#ffffff'),
 (box([-20,BUTTON_Y-7,CONTROL_Z-5],[-4,BUTTON_Y+7,CONTROL_Z+5]),'#111111')])
for id,y in [('S',13.16),('T',33.16)]:
 component(id,[
  (box([6,y-4,CONTROL_Z-6],[18,y+4,CONTROL_Z+6]),'#bf1827'),
  (cylinder(18,21.5,y,CONTROL_Z,4.0),'#999999'),
  (cylinder(21.5,30,y,CONTROL_Z,1.3),'#656565'),
  (cylinder(29,32,y,CONTROL_Z,1.8),'#ffffff')])
# Simon confirmed: 12 NeoPixels fixed under the base ceiling; light leaves
# through the side vents. The spacing below is schematic, not a measured layout.
led_segments=[]
for y in [-101.5,101.5]:
 led_segments.append((box([-90,y-3,-75.3],[-6,y+3,-74.4]),'#111111'))
 for x in [-83,-69,-55,-41,-27,-13]:
  led_segments.extend([(box([x-2.8,y-2.8,-77.2],[x+2.8,y+2.8,-75.3]),'#ffffff'),(box([x-1.2,y-1.2,-77.4],[x+1.2,y+1.2,-77.2]),'#bf1827')])
component('L',led_segments)

# Illustration cutaway only: remove the lower base lip that hides the far LED row.
# This does not alter part 01 or any STL file. Page 06 explicitly labels the cutaway.
def clip_above(mesh,zcut):
 triangles=[]
 for triangle in mesh:
  polygon=list(triangle);out=[]
  for a,b in zip(polygon,polygon[1:]+polygon[:1]):
   ain=a[2]>=zcut;bin=b[2]>=zcut
   if ain:out.append(a)
   if ain!=bin:out.append(a+(b-a)*(zcut-a[2])/(b[2]-a[2]))
  for i in range(1,len(out)-1):triangles.append([out[0],out[i],out[i+1]])
 return np.array(triangles)
MESHES['V']=clip_above(MESHES['01'],-112)
COLORS['V']=COLORS['01'];OWNER_IDS['V']=1
PRINT_LABELS={'V':'01'}

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
  tris.append(q);colors.append(FACE_COLORS.get(id,np.tile(hexrgb(COLORS[id]),(len(q),1))))
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
  for face,shade,facecolor in zip(screen(faces),shades,color):
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
   owner[miny:maxy+1,minx:maxx+1][mask]=OWNER_IDS[id] if id in OWNER_IDS else int(id)
   dep[mask]=zz[mask];rgb[miny:maxy+1,minx:maxx+1][mask]=np.clip(facecolor*shade+255*(1-shade)*.10,0,255).astype(np.uint8)
 for a,b in edges:
  a,b=screen([a,b]);n=max(2,int(np.linalg.norm((b-a)[:2])*2));t=np.linspace(0,1,n);q=a[None,:]+t[:,None]*(b-a)[None,:]
  x=np.rint(q[:,0]).astype(int);y=np.rint(q[:,1]).astype(int);ok=(x>=0)&(x<W)&(y>=0)&(y<H);x=x[ok];y=y[ok];z=q[ok,2]
  ok=z>=depth[y,x]-.9
  rgb[y[ok],x[ok]]=[17,17,17]
 newanchors={}
 for id,p in anchors.items():
  yy,xx=np.where(owner==(OWNER_IDS[id] if id in OWNER_IDS else int(id)));target=screen(p)[:2]
  if len(xx):
   k=np.argmin((xx-target[0])**2+(yy-target[1])**2);newanchors[id]=[int(xx[k]),int(yy[k])]
  # Fully hidden components are not labelled in installed views.
  else:continue
 return Image.fromarray(rgb),newanchors,screen,matrix



# Pixel alphabet from my wiring illustration: same project title style.
PIX = {
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['11111','00100','00100','00100','00100','00100','11111'],
'J':['00111','00010','00010','00010','10010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','11001','10101','10011','10011','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
' ':['00000']*7,
}

# A3 landscape pages. Black, white, red and grey match my wiring overview.
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
pdfmetrics.registerFont(TTFont('Guide',FONT));pdfmetrics.registerFont(TTFont('GuideBold',BOLD))
PAGE=(1190.551,841.89)
BLACK='#111111';WHITE='#ffffff';RED='#bf1827';GREY='#656565';LIGHT='#eeeeee';MID='#c7c7c7'
C=None

def line(x1,y1,x2,y2,color=BLACK,width=1.2,dash=None):
 C.setStrokeColor(HexColor(color));C.setLineWidth(width);C.setDash(dash or []);C.line(x1,1131-y1,x2,1131-y2);C.setDash([])
def rect(x,y,w,h,color,stroke=None,sw=1.2):
 C.setFillColor(HexColor(color));C.setStrokeColor(HexColor(stroke or color));C.setLineWidth(sw);C.rect(x,1131-y-h,w,h,fill=1,stroke=bool(stroke))
def text(x,y,s,size=20,bold=False,color=BLACK):
 C.setFont('GuideBold' if bold else 'Guide',size);C.setFillColor(HexColor(color));C.drawString(x,1131-y-size*.82,s)
def wrap(x,y,s,width=355,size=17,leading=25,color=GREY,bold=False):
 font='GuideBold' if bold else 'Guide';buf='';yy=y
 for word in s.split():
  test=buf+' '+word if buf else word
  if pdfmetrics.stringWidth(test,font,size)>width and buf:text(x,yy,buf,size,bold,color);yy+=leading;buf=word
  else:buf=test
 if buf:text(x,yy,buf,size,bold,color);yy+=leading
 return yy

def image_at(im,x,y,w,h):C.drawImage(ImageReader(im),x,1131-y-h,w,h,mask='auto')

def pixel_title(x,y,value,scale=5):
 for char in value:
  for row,entry in enumerate(PIX.get(char,PIX[' '])):
   for col,on in enumerate(entry):
    if on=='1':rect(x+col*scale,y+row*scale,scale,scale,BLACK)
  x+=6*scale
 rect(x+5,y,15,7*scale,RED)

def header(section,title,subtitle,page):
 C.saveState();C.scale(PAGE[0]/1600,PAGE[1]/1131)
 rect(0,0,1600,1131,WHITE);rect(18,18,1564,1095,WHITE,BLACK,1)
 text(45,36,'PHKI / HSLU / SIMON BALMER',14,color=RED)
 pixel_title(45,64,'JUST ONE MORE MOMENT',5)
 text(1120,65,'ENCLOSURE / ASSEMBLY',20);text(1120,99,'REV 02 / 28 OCT 2026',14,color=RED)
 text(45,131,title,25,bold=True);text(45,168,subtitle,15)
 line(45,198,1555,198,GREY,.8)
 line(45,1055,1555,1055,BLACK,.8)
 text(45,1074,'SIMON BALMER / '+section+' / REV 02',13,color=GREY)
 text(1400,1074,f'{page:02d} / 06',14,color=RED)

def bubble(x,y,label,radius=17):
 if label.startswith('E'):
  rect(x-21,y-15,42,30,RED);text(x-12,y-9,label,17,True,WHITE)
 else:
  C.setFillColor(HexColor(WHITE));C.setStrokeColor(HexColor(BLACK));C.setLineWidth(1.4);C.circle(x,1131-y,radius,fill=1,stroke=1)
  C.setFillColor(HexColor(BLACK));C.setFont('GuideBold',15);w=pdfmetrics.stringWidth(label,'GuideBold',15);C.drawString(x-w/2,1131-y-5,label)

def annotated(ids,offsets,view,box,guide_pairs=(),padding=.13,label_ids=None,anchor_sides=None):
 x,y,w,h=box
 im,anchors,project,mat=render(ids,offsets,view,size=(int(w*1.85),int(h*1.85)),pad=padding)
 overlay=im.copy();draw=ImageDraw.Draw(overlay)
 for a,b in guide_pairs:
  q=project(np.array([a,b])@mat);a=q[0,:2];b=q[1,:2];dist=np.linalg.norm(b-a)
  for k in np.arange(0,dist,17):
   p1=a+(b-a)*k/max(dist,1);p2=a+(b-a)*min(k+9,dist)/max(dist,1);draw.line([tuple(p1),tuple(p2)],fill=MID,width=2)
 arr=np.array(im);ov=np.array(overlay);white=np.all(arr>248,axis=2);arr[white]=ov[white];im=Image.fromarray(arr);image_at(im,x,y,w,h)
 anchors={id:(x+p[0]/im.width*w,y+p[1]/im.height*h) for id,p in anchors.items() if label_ids is None or id in label_ids}
 sides={-1:[],1:[]}
 for id,p in anchors.items():
  side=(anchor_sides or {}).get(id,-1 if p[0]<x+w*.5 else 1);sides[side].append((id,p))
 for side,items in sides.items():
  items.sort(key=(lambda e:e[0]) if {id for id,p in items}=={'S','T'} else (lambda e:e[1][1]));ys=[p[1] for _,p in items]
  for i in range(1,len(ys)):ys[i]=max(ys[i],ys[i-1]+43)
  if ys and ys[-1]>y+h-28:ys=[v-(ys[-1]-(y+h-28)) for v in ys]
  if ys and ys[0]<y+28:ys=[v+y+28-ys[0] for v in ys]
  for (id,p),ly in zip(items,ys):
   lx=x+24 if side<0 else x+w-24;ex=lx-side*29;color=RED if id in REF_LABELS else BLACK
   # White halo keeps callouts legible where they cross a dark purchased component.
   line(p[0],p[1],ex,ly,WHITE,3.1);line(ex,ly,lx-side*18,ly,WHITE,3.1)
   line(p[0],p[1],ex,ly,color,1.0);line(ex,ly,lx-side*18,ly,color,1.0)
   C.setFillColor(HexColor(color));C.circle(p[0],1131-p[1],2.5,fill=1,stroke=0);bubble(lx,ly,REF_LABELS.get(id,PRINT_LABELS.get(id,id)))
 return anchors

def partrow(id,y):
 p=PARTS[int(id)-1];bubble(1195,y+16,id,radius=15);text(1220,y+1,p['name'],16,True)
 text(1220,y+25,p['file'],11,color=GREY);return y+56

def refrow(id,name,description,y):
 bubble(1196,y+15,id);text(1230,y,name,16,True);yy=wrap(1230,y+26,description,width=310,size=14,leading=21);return yy+15

def note(title,body,y,size=16):
 text(1173,y,title,18,True,color=RED);return wrap(1173,y+30,body,width=365,size=size,leading=24)+16

def band(x,y,w,title,body):
 rect(x,y,w,89,LIGHT);rect(x,y,5,89,RED);text(x+20,y+13,title,16,True);wrap(x+20,y+40,body,width=w-35,size=15,leading=22)

def finish():C.restoreState();C.showPage()

def build():
 global C
 C=canvas.Canvas(str(OUT/'assembly-guide.pdf'),pagesize=PAGE)
 C.setAuthor('Simon Balmer');C.setTitle('Just One More Moment - Enclosure Assembly');C.setSubject('13 printed parts and the display, Raspberry Pi and Logitech camera positions')
 n=np.array([math.cos(math.radians(10)),0,math.sin(math.radians(10))])
 def off(d,z=0):return (n*d+np.array([0,0,z])).tolist()
 # 1 / All printed parts and the three purchased component references.
 ids=[p['id'] for p in PARTS]+['D','P','C','B','S','T','L']
 offsets={'01':[0,0,0],'02':[-205,0,-25],'03':[65,0,0],'04':[65,0,0],
 '05':[-48,0,22],'06':[-48,0,-22],'07':off(0,60),'08':off(105,60),'09':off(165,60),
 '10':off(-120,60),'D':off(50,60),'P':off(-55,60),'11':[0,0,120],'12':[0,0,218],'13':[60,0,120],'C':[0,0,167],'B':[65,0,0],'S':[90,0,0],'T':[120,0,0],'L':[0,0,-78]}
 header('OVERVIEW','01 / EXPLODED ENCLOSURE','13 printed parts, one of each. E1-E7 are purchased components. Numbers match the STL filenames.',1)
 annotated(ids,offsets,(1,-1.05,.60),(45,219,1080,780),[
 ([-20,0,-72],[-20,0,320]),([-100,0,60],[170,0,109]),([-8,-17,213],[52,-17,213])],padding=.075,anchor_sides={'07':-1,'P':-1})
 text(1173,218,'PRINT EACH PART ONCE',19,True,color=RED);yy=255
 for group,title in [('base','BASE'),('display','DISPLAY'),('camera','CAMERA')]:
  text(1173,yy,title,15,True);yy+=22
  for p in PARTS:
   if p['group']==group:bubble(1189,yy+10,p['id'],radius=11);text(1215,yy,p['name'],15);yy+=24
  yy+=8
 text(1173,yy,'PURCHASED / DO NOT PRINT',15,True,color=RED);yy+=32
 for label,name in [('E1','Touch Display 2'),('E2','Raspberry Pi 5 + cooler'),('E3','Logitech C270 camera'),('E4','Arcade button + LED'),('E5','SW01 / AI mode'),('E6','SW02 / EN-DE'),('E7','12 NeoPixels / WS2812B')]:
  bubble(1194,yy+10,label);text(1227,yy,name,15);yy+=34
 yy+=8;wrap(1173,yy,'Grey shapes and red details identify parts, not filament colours. Dashed lines link the positions. Not to scale.',width=365,size=15,leading=22)
 text(65,1020,'BASE > DISPLAY > CAMERA / Positions come from the shared CAD assembly coordinates.',14,color=GREY)
 finish()
 # 2 / Opened display stack, including the Pi behind the display.
 ids=['07','08','09','10','D','P'];offsets={'07':off(0),'10':off(-165),'P':off(-85),'D':off(65),'08':off(130),'09':off(195)}
 header('DISPLAY','02 / DISPLAY AND RASPBERRY PI','From rear to front: cover 10, Pi E2, bracket 07, display E1, inner bezel 08 and outer frame 09.',2)
 guides=[]
 for yy in [-68,68]:
  start=np.array([-5,yy,0]);guides.append(((start+n*(-165)).tolist(),(start+n*195).tolist()))
 annotated(ids,offsets,(1,-1.1,.6),(45,235,1080,665),guides,anchor_sides={'07':-1,'P':-1})
 text(1173,219,'PRINTED PARTS',18,True,color=RED);yy=252
 for id in ['07','08','09','10']:yy=partrow(id,yy)
 yy=refrow('E1','Touch Display 2','Screen faces the front.',yy+4)
 yy=refrow('E2','Raspberry Pi 5','Behind the display, inside cover 10.',yy)
 yy=note('1 / PLACE THE DISPLAY','Fit E1 into bracket 07. Put bezel 08 and outer frame 09 on the front side.',yy)
 yy=note('2 / PLACE THE PI','Position E2 behind the display. Check the cooler, USB plugs and ribbon cable space before fitting cover 10.',yy)
 note('3 / CLOSE THE BACK','Fit cover 10 after routing the wires. Use the mounting features in the model.',yy)
 band(65,935,1040,'E1 + E2 / SCHEMATIC COMPONENTS','Their envelopes follow the supplied CAD references. Pi chips and ports are simple symbols. See page 05 for their installed position.')
 finish()
 # 3 / Base details.
 ids=['01','02','03','04','B','S','T'];offsets={'01':[0,0,0],'02':[-205,0,0],'03':[70,0,0],'04':[70,0,0],'B':[65,0,0],'S':[90,0,0],'T':[120,0,0]}
 header('BASE','03 / BASE, FRONT TRIMS AND CABLE GUIDE','The bottom cover also forms the rear closing wall. The cable guide is split into upper and lower halves.',3)
 annotated(ids,offsets,(1,-1.2,.85),(45,225,1080,515),[
 ([20,-40,-96],[87,-40,-96]),([20,90,-96],[87,90,-96]),([-80,0,-120],[-285,0,-120])])
 text(78,760,'REAR CABLE GUIDE / 05 + 06',17,True,color=RED)
 annotated(['05','06'],{'05':[0,0,14],'06':[0,0,-14]},(-1,-1.4,.5),(80,792,440,225),[
 ([-109,-69.89,-111],[-109,-69.89,-79])])
 wrap(565,813,'Put the cable between the two guide halves. Align the guide with the hole in the rear wall of bottom cover 02. Upper half: 05. Lower half: 06.',width=500,size=17,leading=27)
 text(1173,219,'PRINTED PARTS',18,True,color=RED);yy=252
 for id in ['01','02','03','04','05','06']:yy=partrow(id,yy)-8
 for ref,name in [('E4','Illuminated button'),('E5','SW01 / AI mode'),('E6','SW02 / EN-DE')]:
  bubble(1195,yy+13,ref);text(1228,yy+3,name,15);yy+=36
 text(1173,yy+2,'LED placement: page 06.',14,color=GREY);yy+=31
 yy=note('1 / PREPARE THE FRONT','Fit trims 03/04. Put E4 in the large hole and E5/E6 in the two small holes.',yy+8)
 yy=note('2 / ADD THE CABLE GUIDE','Put 05 above 06 at the rear cable outlet. Route the cable before closing.',yy)
 note('3 / CLOSE THE BASE','Check the cables, then fit cover 02 with its closing wall at the back.',yy)
 finish()
 # 4 / Camera body added between the shells.
 ids=['11','12','13','C'];offsets={'11':[0,0,0],'12':[0,0,90],'13':[58,0,0],'C':[0,0,43]}
 header('CAMERA','04 / LOGITECH C270 AND CAMERA SHELLS','Shells 11 and 12 surround the camera. Ring 13 sits in front of the large lens opening.',4)
 annotated(ids,offsets,(1,-1.15,.85),(45,230,1080,675),[
 ([-25,0,73],[-25,0,200]),([-3,-16.9,92.9],[58,-16.9,92.9])])
 text(1173,219,'PRINTED PARTS',18,True,color=RED);yy=252
 for id in ['11','12','13']:yy=partrow(id,yy)
 yy=refrow('E3','Logitech C270','Purchased USB webcam.',yy+12)
 yy=note('1 / ALIGN THE CAMERA','Put E3 in lower shell 11. Align its lens with the large round opening. Keep the USB cable clear.',yy)
 yy=note('2 / CLOSE THE SHELL','Align lower shell 11 with the top of the display housing. Fit upper shell 12 from above.',yy)
 yy=note('3 / FIT THE FRONT RING','Place ring 13 around the front lens opening. Its location follows the supplied CAD coordinates.',yy)
 note('CAMERA SHAPE','E3 is a rough shape, aligned to the lens opening. It does not define a measured camera model or a disassembly method.',yy)
 band(65,935,1040,'E3 / POSITION REFERENCE','The grey body and black lens show where the webcam sits. The red ring is printed part 13. The camera itself is not a part to print.')
 finish()
 # 5 / Actual assembled coordinates. Covers are removed, not exploded.
 header('INSTALLED PARTS','05 / WHERE THE ELECTRONICS SIT','These views use the original assembled positions. Covers are hidden so the purchased parts are visible.',5)
 text(65,226,'A / DISPLAY REAR',19,True,color=RED);text(837,226,'B / CAMERA INTERIOR',19,True,color=RED)
 text(65,258,'Rear cover 10 removed.',16);text(837,258,'Upper shell 12 removed.',16)
 line(800,225,800,900,MID,1)
 annotated(['07','08','09','D','P'],{},(-1,-1.15,.72),(55,295,720,525),padding=.10,label_ids=['07','D','P'],anchor_sides={'P':-1,'D':1,'07':1})
 annotated(['11','13','C'],{},(1,-1.2,1.5),(825,295,720,525),padding=.13,label_ids=['11','13','C'],anchor_sides={'C':-1})
 wrap(65,836,'E2 sits behind E1. The Pi and cooler are shown within the supplied Pi reference envelope. Keep space for the display ribbon and USB cables.',width=690,size=17,leading=26)
 wrap(837,836,'E3 sits inside lower shell 11, below upper shell 12. Its lens faces ring 13. The body is approximate; the lens opening sets its position.',width=690,size=17,leading=26)
 band(65,941,1470,'PRINT SCOPE / 13 FILES / MM / 100% SCALE','Print parts 01-13 once each. Purchased parts E1-E7 do not belong on the print bed. Front controls and the 12 NeoPixels are shown on page 06.')
 finish()
 # 6 / Purchased front controls and the confirmed LED position.
 header('CONTROLS AND LEDS','06 / BUTTON, SWITCHES AND 12 NEOPIXELS','The button has its own LED. The separate 12 NeoPixels sit under the base ceiling and shine through the side vents.',6)
 text(65,226,'A / FRONT CONTROLS',19,True,color=RED);text(837,226,'B / BASE INTERIOR, FROM BELOW',19,True,color=RED)
 text(65,258,'Installed in the front holes.',16);text(837,258,'Cutaway: cover 02 and lower lip hidden.',16)
 line(800,225,800,900,MID,1)
 annotated(['01','03','04','B','S','T'],{},(1,-.12,.18),(55,295,720,490),padding=.13,label_ids=['B','S','T'],anchor_sides={'B':1,'S':-1,'T':-1})
 annotated(['V','L'],{},(.35,-.15,-1.8),(825,295,720,490),padding=.12,label_ids=['V','L'],anchor_sides={'L':-1})
 yy=809
 for ref,body in [('E4','Illuminated arcade button, including its LED.'),('E5','SW01: Local AI / Cloud AI + Cam.'),('E6','SW02: EN / DE.')]:
  bubble(86,yy+10,ref);wrap(120,yy,body,width=650,size=16,leading=23);yy+=40
 wrap(837,809,'E7: 12 WS2812B NeoPixels fixed inside the base, under its ceiling. Their light shines through the side ventilation slots. Spacing in this view is schematic.',width=690,size=17,leading=26)
 band(65,946,1470,'PURCHASED PARTS / DO NOT PRINT','E4 includes the button LED. E7 is the separate 12-LED strip. Wire E4-E7 using hardware/WIRING.md; the assembly views show positions, not electrical connections.')
 finish();C.save()
 import fitz
 doc=fitz.open(OUT/'assembly-guide.pdf')
 names=['exploded-overview','display-assembly','base-assembly','camera-assembly','electronics-placement','controls-and-leds']
 for page,name in zip(doc,names):page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False).save(OUT/(name+'.png'))
 print('Created six English assembly pages in the project wiring style.')

if __name__=='__main__':build()
