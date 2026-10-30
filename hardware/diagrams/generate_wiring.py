#!/usr/bin/env python3
"""Generate my labelled wiring illustration as SVG, PDF and PNG.

Dependencies: reportlab, fonttools; pdftoppm is used for PNG rendering.
Run from any directory: python3 hardware/diagrams/generate_wiring.py
Set JOMM_MONO_FONT to a compatible monospaced TrueType font if needed.
"""
from pathlib import Path
import os
import subprocess
from html import escape

from fontTools.ttLib import TTFont as Font
from fontTools.pens.svgPathPen import SVGPathPen
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A3, landscape

OUT = Path(__file__).resolve().parent
FONT_PATH = os.environ.get('JOMM_MONO_FONT', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
W, H = 2600, 1900
RED, BLACK, WHITE = '#bf1827', '#111111', '#ffffff'
GREY, LIGHT, MID = '#656565', '#eeeeee', '#c7c7c7'

# Physical header pins. Pin 1 is the inner/lower row with USB ports on the right.
PIN_NAMES = ['3V3','5V','GPIO2','5V','GPIO3','GND','GPIO4','GPIO14',
             'GND','GPIO15','GPIO17','GPIO18','GPIO27','GND','GPIO22','GPIO23',
             '3V3','GPIO24','GPIO10','GND','GPIO9','GPIO25','GPIO11','GPIO8',
             'GND','GPIO7','GPIO0','GPIO1','GPIO5','GND','GPIO6','GPIO12',
             'GPIO13','GND','GPIO19','GPIO16','GPIO26','GPIO20','GND','GPIO21']
USED = {2,4,6,9,11,13,14,15,16,19,20,25,34}

pdfmetrics.registerFont(TTFont('JOMMMono', FONT_PATH))
font = Font(FONT_PATH)
glyphs = font.getGlyphSet()
cmap = font.getBestCmap()
units = font['head'].unitsPerEm
metrics = font['hmtx'].metrics
cache = {}


class Art:
    def __init__(self, width, height, pdf_path=None, description=''):
        self.w, self.h = width, height
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
                    '<title>Just One More Moment</title>', f'<desc>{escape(description)}</desc>']
        self.pdf = canvas.Canvas(str(pdf_path), pagesize=landscape(A3)) if pdf_path else None
        if self.pdf:
            pw, ph = landscape(A3)
            scale = min(pw/width, ph/height)
            self.pdf.setTitle('Just One More Moment - Wiring overview')
            self.pdf.setAuthor('Simon Balmer')
            self.pdf.translate((pw-width*scale)/2, (ph-height*scale)/2)
            self.pdf.scale(scale, scale)

    def rect(self,x,y,w,h,fill=WHITE,stroke=BLACK,sw=2,r=0):
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')
        if self.pdf:
            c=self.pdf
            if fill: c.setFillColor(fill)
            if stroke: c.setStrokeColor(stroke)
            c.setLineWidth(sw)
            c.roundRect(x,self.h-y-h,w,h,r,stroke=bool(stroke),fill=bool(fill))

    def line(self,pts,color=BLACK,width=3,dash=None):
        coord=' '.join(f'{x},{y}' for x,y in pts)
        dashattr=f' stroke-dasharray="{dash}"' if dash else ''
        self.svg.append(f'<polyline points="{coord}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{dashattr}/>')
        if self.pdf:
            c=self.pdf;c.setStrokeColor(color);c.setLineWidth(width)
            c.setLineCap(1);c.setLineJoin(1)
            c.setDash([float(n) for n in dash.split()] if dash else [])
            p=c.beginPath();p.moveTo(pts[0][0],self.h-pts[0][1])
            for x,y in pts[1:]:p.lineTo(x,self.h-y)
            c.drawPath(p)
            c.setDash([])

    def circle(self,x,y,r,fill=WHITE,stroke=BLACK,sw=2):
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')
        if self.pdf:
            c=self.pdf
            if fill:c.setFillColor(fill)
            if stroke:c.setStrokeColor(stroke)
            c.setLineWidth(sw);c.circle(x,self.h-y,r,stroke=bool(stroke),fill=bool(fill))

    def text(self,x,y,value,size=22,color=BLACK):
        # Outlined SVG text keeps the chosen mono typeface on GitHub and in print.
        self.svg.append(f'<g aria-label="{escape(value,quote=True)}" fill="{color}">')
        pos=x
        for char in value:
            name=cmap.get(ord(char),cmap[ord('?')])
            if name not in cache:
                pen=SVGPathPen(glyphs);glyphs[name].draw(pen);cache[name]=pen.getCommands()
            if cache[name]:
                self.svg.append(f'<path d="{cache[name]}" transform="translate({pos:.3f} {y}) scale({size/units:.6f} {-size/units:.6f})"/>')
            pos+=metrics[name][0]*size/units
        self.svg.append('</g>')
        if self.pdf:
            self.pdf.setFont('JOMMMono',size);self.pdf.setFillColor(color)
            self.pdf.drawString(x,self.h-y,value)

    def wire(self,pts,kind='signal'):
        # White halos make crossings unconnected and visible against the PCB.
        self.line(pts,WHITE,14)
        if kind=='signal':
            self.line(pts,BLACK,9);self.line(pts,WHITE,4,dash='10 9')
        elif kind=='power':self.line(pts,RED,8)
        else:self.line(pts,BLACK,8)

    def save(self,path):
        Path(path).write_text('\n'.join(self.svg+['</svg>']))
        if self.pdf:self.pdf.showPage();self.pdf.save()


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


def pixel(a,x,y,value,scale=7,color=BLACK):
    for char in value:
        pattern=PIX.get(char,PIX[' '])
        for row,entry in enumerate(pattern):
            for col,on in enumerate(entry):
                if on=='1':a.rect(x+col*scale,y+row*scale,scale,scale,fill=color,stroke=None)
        x+=6*scale
    return x


# Connection view: endpoints are grouped by component rather than drawn at their
# physical positions. The separate pin locator is the physical top view of J8.
# Each tuple is (physical pin, component terminal, y, side, wire kind).
CONNECTIONS = [
    (2, '+5 V', 350, 'left', 'power'),
    (6, 'GND', 405, 'left', 'ground'),
    (9, 'COM', 665, 'left', 'ground'),
    (11, 'NO', 720, 'left', 'signal'),
    (13, 'LED+', 800, 'left', 'signal'),
    (14, 'LED-', 855, 'left', 'ground'),
    (15, 'SIGNAL', 1040, 'left', 'signal'),
    (20, 'GND', 1090, 'left', 'ground'),
    (16, 'SIGNAL', 1250, 'left', 'signal'),
    (25, 'GND', 1300, 'left', 'ground'),
    (4, '+V', 360, 'right', 'power'),
    (19, 'DIN', 500, 'right', 'signal'),
    (34, 'GND', 620, 'right', 'ground'),
]


def right_text(a, x, y, value, size=24, color=BLACK):
    width = sum(metrics[cmap.get(ord(c), cmap[ord('?')])][0] for c in value)*size/units
    a.text(x-width, y, value, size, color)


def end_dot(a, x, y, color=BLACK):
    a.circle(x, y, 7, WHITE, color, 3)


def cable(a, x1, x2, y, kind='usb'):
    a.line([(x1,y),(x2,y)], BLACK, 18 if kind=='usb' else 24)
    a.line([(x1,y),(x2,y)], MID, 10 if kind=='usb' else 17)
    if kind=='ribbon':
        a.line([(x1,y-4),(x2,y-4)], WHITE, 2)
        a.line([(x1,y+4),(x2,y+4)], WHITE, 2)


def toggle(a, y, title, mode):
    a.text(90,y-24,title,27,RED)
    a.rect(90,y,610,145,LIGHT,BLACK,3,12)
    a.circle(165,y+68,36,BLACK,None)
    a.circle(165,y+68,26,MID,None)
    a.line([(165,y+68),(145,y+25)],BLACK,16)
    a.circle(145,y+25,11,WHITE,BLACK,2)
    a.text(230,y+52,mode[0],23)
    a.text(230,y+91,mode[1],23)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert {c[0] for c in CONNECTIONS} == USED
    assert len(CONNECTIONS) == len(USED)
    desc=('My wiring for Just One More Moment, by Simon Balmer. '
          'Connection view grouped by component; separate physical 40-pin J8 locator. '
          'Display P2/P6 plus DSI; button COM P9, NO P11 GPIO17, LED+ P13 GPIO27, LED- P14. '
          'SW01 P15 GPIO22/P20 GND; SW02 P16 GPIO23/P25 GND. '
          '11 NeoPixels: P4 through MIC 1N4001 to +V, cathode ring toward strip; '
          'P19 GPIO10 directly to DIN; P34 to GND. Webcam USB; official PSU USB-C.')
    a=Art(W,H,OUT/'wiring-overview.pdf',desc)
    a.rect(0,0,W,H,WHITE,None)
    a.rect(45,35,2510,1825,WHITE,BLACK,2)
    a.text(85,83,'PHKI / HSLU / SIMON BALMER',22,RED)
    end=pixel(a,85,108,'JUST ONE MORE MOMENT',7)
    a.rect(end+12,108,22,49,RED,None)
    a.text(1870,108,'WIRING OVERVIEW',29)
    a.text(1870,150,'REV 06 / 30 OCT 2026',22,RED)
    a.text(90,200,'Connections grouped by component. Physical J8 pin positions: locator below.',23)

    # Main functional view. The central block explicitly does not depict the
    # physical arrangement of pins or USB/DSI ports.
    a.rect(1010,230,580,1140,BLACK,BLACK,3,18)
    a.text(1040,273,'RASPBERRY PI 5',30,WHITE)
    a.text(1040,309,'8 GB / CONNECTION VIEW',21,MID)
    a.text(1040,1340,'Pxx = physical header pin',21,WHITE)
    a.text(1320,725,'J8 / GPIO',24,WHITE)
    a.rect(1350,755,180,140,GREY,MID,3,8)
    a.rect(1378,777,124,95,BLACK,MID,2,3)
    a.text(1392,837,'PI 5',26,WHITE)
    a.text(1320,1035,'BCM numbering',21,MID)
    a.text(1320,1068,'for GPIOxx',21,MID)

    # Display with distinct power and ribbon terminals.
    a.text(90,260,'01 / TOUCH DISPLAY 2',27,RED)
    a.rect(90,285,610,255,LIGHT,BLACK,3,12)
    a.rect(113,307,410,209,BLACK,BLACK,2,9)
    a.rect(131,325,374,171,WHITE,MID,2,3)
    a.rect(144,337,348,146,BLACK,None)
    a.text(165,382,'JUST ONE MORE',25,WHITE)
    a.text(165,419,'MOMENT_',32,RED)
    a.text(165,459,'+ one more moment',19,WHITE)
    a.text(552,487,'DSI',23)
    cable(a,700,1010,480,'ribbon')
    a.text(730,462,'VIDEO + TOUCH',21)
    a.text(1040,488,'CAM/DISP / DSI',24,WHITE)

    # Button: contact pair and LED pair have generous separation.
    a.text(90,584,'02 / ILLUMINATED ARCADE BUTTON',27,RED)
    a.rect(90,610,610,300,LIGHT,BLACK,3,12)
    a.circle(285,748,101,BLACK,None)
    a.circle(285,743,85,WHITE,MID,7)
    a.circle(285,743,70,WHITE,BLACK,2)
    a.text(239,753,'+TIME',24,RED)
    a.text(151,885,'33 mm / WHITE LED',21)
    a.line([(535,757),(677,757)],MID,2)

    # Two software inputs, not switches in the USB or supply wiring.
    toggle(a,995,'03 / SW01 / AI MODE',('LOCAL AI /','CLOUD AI + CAM'))
    toggle(a,1205,'04 / SW02 / LANGUAGE',('EN / DE',''))

    # Eleven emitters are shown in a recognisable vertical strip. Terminal
    # positions on this illustration are functional, not a solder-pad template.
    a.text(1910,260,'05 / WS2812B / 11 LEDs',27,RED)
    a.rect(1910,285,600,445,LIGHT,BLACK,3,12)
    a.rect(2255,316,150,382,BLACK,BLACK,2,6)
    for i in range(11):
        y=330+i*29
        a.rect(2281,y,23,23,WHITE,MID,1,2)
        a.rect(2287,y+6,11,11,RED,None)
        a.text(2323,y+18,f'{i+1:02}',20,WHITE)
    a.text(1940,692,'DIN -> PIXEL 01',23)
    a.text(1940,721,'-> ... -> PIXEL 11',20)

    # Camera and PSU have their own cable category, unlike GND wires.
    a.text(1910,823,'06 / LOGITECH C270',27,RED)
    a.rect(1910,848,600,220,LIGHT,BLACK,3,12)
    a.rect(2130,883,320,126,BLACK,BLACK,3,18)
    a.rect(2147,899,285,85,GREY,None,0,9)
    a.circle(2290,941,42,BLACK,WHITE,3)
    a.circle(2290,941,24,BLACK,RED,3)
    a.circle(2280,931,6,WHITE,None)
    a.rect(2250,1009,80,20,BLACK,None,0,3)
    a.text(1940,1047,'USB / VISUAL CONTEXT',22)
    cable(a,1590,1910,950)
    a.text(1680,930,'USB',23)
    a.text(1495,958,'USB',24,WHITE)
    a.text(1940,938,'USB',23)

    a.text(1910,1158,'07 / OFFICIAL POWER SUPPLY',27,RED)
    a.rect(1910,1185,600,170,LIGHT,BLACK,3,12)
    a.rect(2140,1205,300,130,BLACK,BLACK,3,10)
    a.text(2180,1257,'27 W',33,WHITE)
    a.text(2170,1304,'USB-C PSU',24,WHITE)
    cable(a,1590,1910,1270)
    a.text(1660,1250,'USB-C',23)
    a.text(1460,1278,'USB-C',24,WHITE)
    a.text(1940,1258,'USB-C',23)

    # Every GPIO lead is one horizontal line with a terminal name at the
    # component and the physical pin plus BCM function on the Pi.
    for n,label,y,side,kind in CONNECTIONS:
        x1,x2=(700,1010) if side=='left' else (1590,1910)
        a.wire([(x1,y),(x2,y)],kind)
        color=RED if kind=='power' else BLACK
        end_dot(a,x1,y,color);end_dot(a,x2,y,color)
        pin_label=f'P{n} / {PIN_NAMES[n-1]}'
        if side=='left':
            right_text(a,677,y+8,label,23)
            a.text(1040,y+8,pin_label,24,WHITE)
        else:
            right_text(a,1560,y+8,pin_label,24,WHITE)
            a.text(1938,y+8,label,24)

    # Realistic D1 body inserted directly in the red P4 -> +V lead. The band
    # is on the strip/right side. Separate labels never cover a conductor.
    a.text(1610,305,'D1 / MIC 1N4001',22,RED)
    a.rect(1670,339,145,42,BLACK,BLACK,2,6)
    a.rect(1783,339,14,42,MID,None)
    a.text(1675,414,'A',23)
    a.text(1785,414,'K',23)
    a.text(1660,449,'RING -> STRIP',21)

    # Dedicated locator: actual physical pin positions in a clearly oriented
    # top view, independent of the grouped connection view above.
    a.line([(85,1425),(2515,1425)],BLACK,2)
    a.text(90,1473,'J8 / PHYSICAL PIN LOCATOR',27,RED)
    a.rect(110,1500,1240,195,LIGHT,BLACK,2,10)
    a.text(150,1537,'TOP VIEW / USB PORTS AT RIGHT',22)
    for n in range(1,41):
        x=165+((n-1)//2)*57
        y=1580 if n%2==0 else 1640
        a.rect(x-21,y-21,42,42,RED if n in USED else WHITE,BLACK,3 if n==1 else 1,3)
        right_text(a,x+(8 if n<10 else 16),y+9,str(n),26,WHITE if n in USED else GREY)
    for y in (1563,1623):
        a.rect(1314,y,55,40,BLACK,None,0,3)
    a.text(90,1732,'P1 = lower left. Red pins are used in my wiring.',22)
    a.line([(1410,1457),(1410,1828)],MID,2)

    a.text(1470,1473,'WHY I USE D1',27,RED)
    a.text(1470,1522,'I lower the strip supply with D1 so it can',23)
    a.text(1470,1561,'recognize 3.3 V data more reliably.',23)
    a.text(1470,1600,'GPIO10 itself stays at 3.3 V.',23)
    a.text(1470,1658,'Cathode ring -> strip +V. DIN -> GPIO10.',23)
    a.text(1470,1715,'SW01 and SW02 are software inputs.',23)
    a.text(1470,1754,'SW01 does not switch the USB camera cable.',23)
    a.text(1470,1812,'I disconnect power before changing wires.',22)

    # Compact key using the exact line styles in the main drawing.
    for x,label,kind in [(90,'5 V / +V','power'),(485,'GND','ground'),(800,'GPIO / 3.3 V','signal')]:
        a.wire([(x,1790),(x+75,1790)],kind)
        a.text(x+93,1798,label,22)
    a.text(90,1840,'Component and port positions in the main view are grouped for clarity.',21,GREY)
    a.save(OUT/'wiring-overview.svg')
    subprocess.run(['pdftoppm','-singlefile','-scale-to','3000','-png',str(OUT/'wiring-overview.pdf'),str(OUT/'wiring-overview')],check=True)
    print('Generated wiring SVG, A3 PDF and PNG. All 13 GPIO connections are explicit.')


if __name__=='__main__':main()
