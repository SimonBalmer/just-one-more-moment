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


def pin(n):return (1000+((n-1)//2)*34,610 if n%2==0 else 650)


def terminal(a,x,y,label,side='left',color=BLACK,textcolor=None):
    a.circle(x,y,7,WHITE,color,3)
    a.text(x+16 if side=='left' else x-220,y-11,label,19,textcolor or color)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    desc=('My Raspberry Pi 5 wiring: display power pins 2/6; button COM/NO pins 9/11; '
          'button LED pins 13/14; switch 1 pins 15/20; switch 2 pins 16/25; '
          '12 NeoPixels DIN pin 19 GPIO10. The diode is in the 5 V supply with its cathode band toward the strip. '
          'NeoPixel power uses physical pin 4 through a MIC 1N4001 diode; pin 34 is the ground selected for this plan. '
          'SW01 is local AI or cloud AI plus camera; SW02 selects English or German. USB webcam and DSI display link included.')
    a=Art(W,H,OUT/'wiring-overview.pdf',desc)
    a.rect(0,0,W,H,WHITE,None)
    a.rect(55,45,2490,1810,WHITE,BLACK,2)
    a.text(85,88,'PHKI / HSLU / SIMON BALMER',21,RED)
    end=pixel(a,85,112,'JUST ONE MORE MOMENT',7)
    a.rect(end+12,112,22,49,RED,None)
    a.text(1850,110,'WIRING OVERVIEW',30)
    a.text(1850,149,'REV 03 / 28 OCT 2026',21,RED)

    # Recognisable top-view components; neutral technical geometry, not to scale.
    a.text(100,250,'01 / TOUCH DISPLAY 2',27,RED)
    a.rect(100,275,560,285,BLACK,BLACK,4,14)
    a.rect(122,296,510,225,WHITE,MID,2,6)
    a.rect(142,315,470,187,BLACK,None,0,3)
    a.text(173,368,'JUST ONE MORE',30,WHITE)
    a.text(173,411,'MOMENT_',36,RED)
    a.text(173,468,'remaining: ...',21,WHITE)
    for x in [116,644]:
        for y in [289,545]:a.circle(x,y,5,WHITE,None)
    a.text(110,600,'POWER: P2 / P6',21)
    a.text(110,628,'VIDEO + TOUCH: DSI / FFC',21)

    a.text(100,850,'02 / ILLUMINATED ARCADE BUTTON',27,RED)
    a.rect(100,875,500,320,LIGHT,BLACK,3,10)
    a.circle(260,1010,101,BLACK,BLACK,3)
    a.circle(260,1004,85,WHITE,MID,7)
    a.circle(260,1004,70,WHITE,BLACK,2)
    a.text(214,1012,'+TIME',24,RED)
    a.text(130,1158,'33 mm / WHITE LED',21)

    for label,y in [('03 / SW01 / AI MODE',300),('04 / SW02 / LANGUAGE',700)]:
        a.text(1970,y-20,label,27,RED)
        a.rect(1970,y,460,180,LIGHT,BLACK,3,8)
        a.circle(2240,y+90,46,BLACK,BLACK,2)
        a.circle(2240,y+90,34,MID,BLACK,2)
        a.line([(2240,y+90),(2215,y+26)],BLACK,20)
        a.circle(2215,y+26,13,WHITE,BLACK,3)
    a.text(2000,460,'LOCAL AI / CLOUD AI + CAM',19)
    a.text(2000,860,'EN / DE',23)

    a.text(1110,220,'05 / LOGITECH C270',27,RED)
    a.rect(1110,245,350,145,BLACK,BLACK,3,20)
    a.rect(1130,263,310,100,GREY,None,0,12)
    a.circle(1285,314,45,BLACK,WHITE,3)
    a.circle(1285,314,27,BLACK,RED,3)
    a.circle(1275,304,7,WHITE,None)
    a.rect(1238,390,95,30,BLACK,None,0,4)
    a.text(1110,454,'USB / VISUAL CONTEXT',21)

    # Pi board in the same orientation as the reference: GPIO top, USB right.
    a.rect(930,580,830,570,BLACK,BLACK,4,24)
    a.rect(945,595,800,540,None,GREY,2,15)
    for x,y in [(955,606),(1732,607),(956,1123),(1730,1122)]:
        a.circle(x,y,14,MID,WHITE,3);a.circle(x,y,7,WHITE,None)
    a.rect(987,590,676,80,GREY,WHITE,2,5)
    a.rect(1000,850,175,110,MID,WHITE,2,3)
    a.rect(1230,945,145,140,MID,WHITE,2,3)
    a.rect(1248,962,109,104,LIGHT,GREY,3,2)
    a.rect(1475,785,140,110,GREY,MID,2,3)
    for x in range(1000,1150,25):
        a.rect(x,1000,15,28,MID,None)
        a.rect(x,1045,15,14,MID,None)
    for y in [750,900]:
        a.rect(1690,y,100,100,MID,WHITE,2,3)
        a.rect(1701,y+12,79,27,BLACK,None)
        a.rect(1701,y+58,79,27,BLACK,None)
    a.rect(1670,1030,125,112,MID,WHITE,2,3)
    a.rect(1680,1060,105,62,BLACK,None)
    a.text(1495,722,'USB',18,WHITE)
    a.text(1490,1115,'CAM/DISP',17,WHITE)
    a.rect(1460,1040,28,88,LIGHT,GREY,2)
    a.rect(1000,1125,72,36,MID,WHITE,2,4)
    a.text(930,1198,'USB-C',20)
    a.text(990,1110,'RASPBERRY PI 5 / 8 GB',26,WHITE)

    # External leads. A break/halo at each crossing means no electrical junction.
    a.wire([(660,350),(750,350),(750,180),(1000,180),pin(2)],'power')
    a.wire([(660,390),(785,390),(785,210),(1068,210),pin(6)],'ground')
    a.wire([pin(9),(1136,730),(700,730),(700,940),(600,940)],'ground')
    a.wire([pin(11),(1170,760),(730,760),(730,980),(600,980)])
    a.wire([pin(13),(1204,790),(760,790),(760,1060),(600,1060)])
    a.wire([pin(14),(1204,550),(900,550),(900,1100),(600,1100)],'ground')
    a.wire([pin(15),(1238,850),(1850,850),(1850,390),(1970,390)])
    a.wire([pin(20),(1306,510),(1880,510),(1880,430),(1970,430)],'ground')
    a.wire([pin(16),(1238,480),(1820,480),(1820,790),(1970,790)])
    a.wire([pin(25),(1408,880),(1880,880),(1880,830),(1970,830)],'ground')
    a.wire([pin(19),(1306,910),(1700,910),(1700,1240),(1760,1240)])
    a.wire([(1460,315),(1920,315),(1920,800),(1790,800)],'ground')
    # P4 and the free ground P34 define the NeoPixel supply in this plan.
    a.wire([pin(4),(1034,240),(2470,240),(2470,1395),(1600,1395),(1600,1160),(1760,1160)],'power')
    a.wire([pin(34),(1544,525),(2505,525),(2505,1460),(1645,1460),(1645,1320),(1760,1320)],'ground')
    # DSI ribbon: wider grey flat cable, not a GPIO lead.
    ribbon=[(660,500),(850,500),(850,1220),(1474,1220),(1474,1128)]
    a.line(ribbon,BLACK,28);a.line(ribbon,MID,22);a.line(ribbon,WHITE,2)
    a.text(1120,1264,'DSI / FFC',21)
    # USB-C power supply and cable.
    a.line([(1036,1161),(1036,1300)],BLACK,16)
    a.rect(935,1300,205,140,BLACK,BLACK,3,9)
    a.text(963,1345,'OFFICIAL',22,WHITE)
    a.text(971,1382,'27 W',28,WHITE)
    a.text(962,1415,'USB-C PSU',18,WHITE)

    # Header drawn last to make every attachment and physical number explicit.
    for n in range(1,41):
        x,y=pin(n)
        a.rect(x-14,y-14,28,28,RED if n in USED else LIGHT,WHITE,1.5,2)
        a.text(x-(6 if n<10 else 11),y+6,str(n),17,WHITE if n in USED else GREY)
    a.text(963,710,'J8 / PIN 1',18,WHITE)
    a.line([(988,689),(988,680),(1000,666)],RED,2)
    a.text(1410,505,'GPIO / TOP VIEW',21)

    # Component-side terminal labels keep BCM and physical numbering together.
    terminal(a,660,350,'P2 / 5 V','right',RED)
    terminal(a,660,390,'P6 / GND','right',textcolor=WHITE)
    terminal(a,600,940,'COM / P9','right')
    terminal(a,600,980,'NO / P11 / GPIO17','right')
    terminal(a,600,1060,'LED+ P13 / GPIO27','right')
    terminal(a,600,1100,'LED- / P14','right')
    terminal(a,1970,390,'P15 / GPIO22')
    terminal(a,1970,430,'P20 / GND')
    terminal(a,1970,790,'P16 / GPIO23')
    terminal(a,1970,830,'P25 / GND')

    # NeoPixel strip: exactly 12 visible emitters and three distinct rails.
    a.text(1810,1080,'06 / WS2812B / 12 LEDs',27,RED)
    a.rect(1760,1120,670,220,BLACK,BLACK,3,5)
    for i in range(12):
        x=1808+i*49
        a.rect(x,1175,36,36,LIGHT,GREY,2,3)
        a.rect(x+9,1184,18,18,RED,None,0,2)
        a.text(x+7,1240,f'{i+1:02}',17,WHITE)
    a.text(1830,1294,'DIN -> PIXEL 01 -> ... -> PIXEL 12',20,WHITE)
    a.text(1760,1375,'P19 / GPIO10 -> DIN',24)

    # D1 is in the 5 V lead only; the band faces upward toward strip +V.
    a.text(1250,1372,'P4 / 5 V -> D1 -> STRIP +V',21,RED)
    a.rect(1583,1194,34,90,BLACK,BLACK,2,5)
    a.rect(1583,1204,34,12,MID,None)
    a.text(1260,1288,'D1 / MIC 1N4001',22,RED)
    a.text(1330,1320,'BAND / K',20)
    a.line([(1460,1310),(1567,1210)],GREY,2)
    a.text(1760,1440,'P34 / COMMON GND',21)
    terminal(a,1760,1160,'+V','left',RED)
    terminal(a,1760,1240,'DIN','left',textcolor=WHITE)
    terminal(a,1760,1320,'GND','left',textcolor=WHITE)

    # Notes / enlarged diode detail are part of the drawing, not assumed wiring.
    a.line([(85,1510),(2515,1510)],BLACK,2)
    a.text(90,1556,'READ THE DRAWING',25,RED)
    a.wire([(95,1600),(190,1600)],'power');a.text(220,1607,'5 V supply',21)
    a.wire([(95,1645),(190,1645)],'ground');a.text(220,1652,'GND / common return',21)
    a.wire([(95,1690),(190,1690)]);a.text(220,1697,'GPIO signal (3.3 V)',21)
    a.text(90,1750,'Pxx = physical header pin.',21)
    a.text(90,1785,'Crossings do not join wires.',21)
    a.text(90,1820,'Component views are not to scale.',19,GREY)

    a.text(790,1556,'D1 / MIC 1N4001 / 5 V LEAD',25,RED)
    a.line([(800,1630),(1310,1630)],RED,8)
    a.rect(970,1592,180,76,BLACK,BLACK,2,10)
    a.rect(1116,1592,17,76,MID,None)
    a.text(795,1592,'PI 5 V',21,RED)
    a.text(1180,1592,'STRIP +V',21,RED)
    a.text(978,1710,'A',22);a.text(1110,1710,'K',22)
    a.text(790,1760,'Cathode band faces the strip.',22)
    a.text(790,1795,'DIN connects directly to GPIO10.',21)
    a.text(790,1825,'I use the Adafruit supply-drop method.',19,GREY)

    a.text(1700,1556,'WHY I USE THE DIODE',25,RED)
    a.text(1700,1607,'D1 lowers the strip supply voltage.',21)
    a.text(1700,1652,'This helps it read 3.3 V data as HIGH.',21)
    a.text(1700,1697,'GPIO10 itself stays at 3.3 V.',21)
    a.text(1700,1742,'P4 = 5 V / P34 = common GND.',21)
    a.text(1700,1787,'Power off before changing wires.',21)
    a.text(1700,1825,'USB/DSI port positions: illustrative.',19,GREY)

    a.save(OUT/'wiring-overview.svg')
    subprocess.run(['pdftoppm','-singlefile','-scale-to','2600','-png',str(OUT/'wiring-overview.pdf'),str(OUT/'wiring-overview')],check=True)

    # Shared retro graphic for the Markdown documentation.
    banner=Art(1600,220,description='Just One More Moment - my PHKI project documentation')
    banner.rect(0,0,1600,220,BLACK,None)
    banner.rect(0,0,14,220,RED,None)
    banner.text(52,48,'SIMON BALMER / PHKI / HSLU',22,WHITE)
    end=pixel(banner,52,78,'JUST ONE MORE MOMENT',7,WHITE)
    banner.rect(end+12,78,22,49,RED,None)
    banner.text(52,187,'AI / EMPATHY / RESPONSIBILITY',23,RED)
    banner.save(OUT/'project-banner.svg')
    print('Generated wiring SVG, PDF, PNG and retro project banner.')


if __name__=='__main__':main()
