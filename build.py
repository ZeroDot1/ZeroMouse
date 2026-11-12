#!/usr/bin/env python3
"""Build ZeroMouse XCursor binaries from resolution-independent Pillow drawings."""
from pathlib import Path
import math, struct
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "zeromouse" / "cursors"
SIZES = (24, 32, 36, 48, 64, 72, 96, 128, 256, 512)
GREEN = (190, 255, 0, 255)
YELLOW = (234, 255, 72, 255)
DARK = (17, 35, 8, 255)
WHITE = (250, 255, 218, 255)

def scaled_poly(draw, points, color, s, outline=None, width=1):
    pts=[(round(x*s),round(y*s)) for x,y in points]
    draw.polygon(pts, fill=color)
    if outline: draw.line(pts+[pts[0]], fill=outline, width=max(1,round(width*s)), joint="curve")

def draw_pointer(im):
    s=im.width/64; d=ImageDraw.Draw(im)
    p=[(8,4),(8,48),(19,37),(27,55),(35,52),(27,34),(43,34)]
    scaled_poly(d,p,GREEN,s,DARK,2.5)
    d.line([(10*s,9*s),(10*s,42*s),(17*s,34*s)], fill=YELLOW,width=max(1,round(2*s)))

def draw_hand(im):
    s=im.width/64; d=ImageDraw.Draw(im)
    # Pointing hand with rounded palm and extended index finger.
    coords=[(26,8),(35,8),(37,31),(42,27),(48,28),(51,33),(58,35),(60,40),(57,47),(49,54),(39,57),(28,55),(20,49),(13,41),(12,36),(16,33),(20,35),(25,40)]
    scaled_poly(d,coords,GREEN,s,DARK,2.5)
    d.line([(29*s,13*s),(31*s,34*s)],fill=YELLOW,width=max(1,round(2*s)))

def draw_text(im):
    s=im.width/64; d=ImageDraw.Draw(im)
    d.line([(14*s,7*s),(14*s,52*s)],fill=DARK,width=max(1,round(6*s)))
    d.line([(14*s,7*s),(14*s,52*s)],fill=GREEN,width=max(1,round(3*s)))
    for y in (7,52):
        d.line([(8*s,y*s),(21*s,y*s)],fill=DARK,width=max(1,round(5*s)))
        d.line([(8*s,y*s),(21*s,y*s)],fill=YELLOW,width=max(1,round(2*s)))
    for x in (25,31,37,43,49):
        d.ellipse((x*s,26*s,(x+2)*s,28*s),fill=GREEN)

def draw_special(im, kind):
    s=im.width/64; d=ImageDraw.Draw(im)
    def line(a,b):
        d.line([(a[0]*s,a[1]*s),(b[0]*s,b[1]*s)],fill=DARK,width=max(1,round(7*s)))
        d.line([(a[0]*s,a[1]*s),(b[0]*s,b[1]*s)],fill=GREEN,width=max(1,round(3*s)))
    def head(p,dr):
        x,y=p; dx,dy=dr; px,py=-dy,dx
        scaled_poly(d,[(x+dx*9,y+dy*9),(x-dx*2+px*5,y-dy*2+py*5),(x-dx*2-px*5,y-dy*2-py*5)],YELLOW,s,DARK,1.5)
    if kind=="move":
        line((32,12),(32,52)); line((12,32),(52,32))
        for p,dr in [((32,8),(0,-1)),((32,56),(0,1)),((8,32),(-1,0)),((56,32),(1,0))]: head(p,dr)
    elif kind in ("ew-resize","ns-resize"):
        a,b=((12,32),(52,32)) if kind=="ew-resize" else ((32,12),(32,52))
        dr=(-1,0) if kind=="ew-resize" else (0,-1)
        end=(1,0) if kind=="ew-resize" else (0,1)
        line(a,b); head((a[0]+dr[0]*4,a[1]+dr[1]*4),dr); head((b[0]+end[0]*4,b[1]+end[1]*4),end)
    elif kind in ("nwse-resize","nesw-resize"):
        a,b=((12,12),(52,52)) if kind=="nwse-resize" else ((52,12),(12,52))
        da,db=((-1,-1),(1,1)) if kind=="nwse-resize" else ((1,-1),(-1,1))
        line(a,b); head((a[0]+da[0]*4,a[1]+da[1]*4),da); head((b[0]+db[0]*4,b[1]+db[1]*4),db)
    elif kind=="crosshair":
        line((32,7),(32,57)); line((7,32),(57,32))
        d.ellipse((27*s,27*s,37*s,37*s),outline=YELLOW,width=max(1,round(2*s)))
    elif kind=="not-allowed":
        d.ellipse((9*s,9*s,55*s,55*s),outline=DARK,width=max(1,round(8*s)))
        d.ellipse((9*s,9*s,55*s,55*s),outline=GREEN,width=max(1,round(4*s)))
        d.line([(19*s,45*s),(45*s,19*s)],fill=DARK,width=max(1,round(8*s)))
        d.line([(19*s,45*s),(45*s,19*s)],fill=YELLOW,width=max(1,round(4*s)))
    elif kind=="help":
        d.ellipse((9*s,9*s,55*s,55*s),outline=DARK,width=max(1,round(7*s)))
        d.ellipse((9*s,9*s,55*s,55*s),outline=GREEN,width=max(1,round(3*s)))
        d.arc((21*s,17*s,43*s,39*s),195,525,fill=YELLOW,width=max(1,round(4*s)))
        d.line([(32*s,37*s),(32*s,43*s)],fill=YELLOW,width=max(1,round(4*s)))
        d.ellipse((30*s,47*s,34*s,51*s),fill=YELLOW)
    elif kind in ("zoom-in","zoom-out"):
        d.ellipse((8*s,6*s,42*s,40*s),outline=DARK,width=max(1,round(8*s)))
        d.ellipse((8*s,6*s,42*s,40*s),outline=GREEN,width=max(1,round(4*s)))
        d.line([(36*s,36*s),(55*s,55*s)],fill=DARK,width=max(1,round(9*s)))
        d.line([(36*s,36*s),(55*s,55*s)],fill=YELLOW,width=max(1,round(4*s)))
        d.line([(16*s,23*s),(34*s,23*s)],fill=YELLOW,width=max(1,round(3*s)))
        if kind=="zoom-in": d.line([(25*s,14*s),(25*s,32*s)],fill=YELLOW,width=max(1,round(3*s)))
    elif kind=="pencil":
        scaled_poly(d,[(13,45),(43,15),(51,23),(21,53),(11,56)],GREEN,s,DARK,2)
        scaled_poly(d,[(43,15),(49,9),(57,17),(51,23)],YELLOW,s,DARK,1.5)
        d.line([(16*s,47*s),(21*s,52*s)],fill=YELLOW,width=max(1,round(2*s)))

def draw_hourglass(im, phase=0):
    s=im.width/64; d=ImageDraw.Draw(im)
    # Bright frame, narrow waist and moving grains rendered per frame.
    top=[(13,8),(51,8),(46,15),(37,25),(34,31),(37,37),(46,47),(51,54),(13,54),(18,47),(27,37),(30,31),(27,25),(18,15)]
    scaled_poly(d,top,GREEN,s,DARK,2.5)
    d.line([(17*s,12*s),(47*s,12*s)],fill=YELLOW,width=max(1,round(2*s)))
    d.line([(17*s,50*s),(47*s,50*s)],fill=YELLOW,width=max(1,round(2*s)))
    # Sand pile in upper chamber drains to the lower chamber.
    frac=(phase%6)/5
    upper_h=max(2,round((13*(1-frac))*s))
    d.polygon([(20*s,14*s),(44*s,14*s),(32*s,(14+upper_h)*s)],fill=YELLOW)
    d.line([(32*s,29*s),(32*s,34*s)],fill=YELLOW,width=max(1,round(2*s)))
    lower_h=max(1,round((2+10*frac)*s))
    d.polygon([(21*s,48*s),(43*s,48*s),(32*s,(48-lower_h)*s)],fill=YELLOW)

def draw_rocket(im, phase=0):
    s=im.width/64; d=ImageDraw.Draw(im)
    # plume pulses and extends down as the rocket lifts off
    length=(9,13,18,14)[phase%4]
    d.polygon([(27*s,42*s),(37*s,42*s),(32*s,(42+length)*s)],fill=YELLOW)
    d.polygon([(30*s,43*s),(34*s,43*s),(32*s,(43+max(3,length-4))*s)],fill=GREEN)
    # nose points upward, three fins and a porthole
    body=[(32,5),(40,17),(42,34),(37,44),(27,44),(22,34),(24,17)]
    scaled_poly(d,body,GREEN,s,DARK,2.5)
    scaled_poly(d,[(24,31),(15,39),(24,40)],YELLOW,s,DARK,1.5)
    scaled_poly(d,[(40,31),(49,39),(40,40)],YELLOW,s,DARK,1.5)
    d.ellipse((28*s,20*s,36*s,28*s),fill=DARK,outline=YELLOW,width=max(1,round(2*s)))
    d.line([(31*s,9*s),(26*s,20*s)],fill=YELLOW,width=max(1,round(2*s)))

def render(kind, size, phase=0):
    im=Image.new("RGBA",(size,size),(0,0,0,0))
    funcs={"left_ptr":draw_pointer,"hand":draw_hand,"text":draw_text}
    if kind in funcs: funcs[kind](im)
    elif kind in ("move","ew-resize","ns-resize","nwse-resize","nesw-resize","crosshair","not-allowed","help","zoom-in","zoom-out","pencil"): draw_special(im,kind)
    elif kind=="watch": draw_hourglass(im,phase)
    elif kind=="progress": draw_rocket(im,phase)
    return im

# Xcursor file format: 16-byte header, table of contents, then image chunks.
MAGIC=0x72756358
IMAGE_TYPE=0xfffd0002
def write_xcursor(path, kind, phases, hotspot):
    entries=[]; chunks=[]; offset=16+12*(len(phases)*len(SIZES))
    for phase, delay in phases:
        for size in SIZES:
            im=render(kind,size,phase)
            hx,hy=hotspot(size)
            rgba = im.get_flattened_data()
            pixels=b"".join(struct.pack("<I", (a<<24)|(r<<16)|(g<<8)|b) for r,g,b,a in rgba)
            chunk=struct.pack("<IIIIIIIII",36,IMAGE_TYPE,size,1,size,size,hx,hy,delay)+pixels
            entries.append(struct.pack("<III",IMAGE_TYPE,size,offset)); chunks.append(chunk); offset+=len(chunk)
    # Header fields are magic, header size, 16.16 version, then TOC count.
    path.write_bytes(struct.pack("<IIII",MAGIC,16,0x00010000,len(entries))+b"".join(entries)+b"".join(chunks))

OUT.mkdir(parents=True,exist_ok=True)
aliases={
 "left_ptr":"left_ptr", "default":"left_ptr", "top_left_arrow":"left_ptr", "arrow":"left_ptr",
 "center_ptr":"left_ptr", "cross":"crosshair", "diamond_cross":"crosshair",
 "target":"left_ptr", "tcross":"left_ptr", "dot":"left_ptr", "dotbox":"left_ptr",
 "pointer":"hand", "hand":"hand", "hand2":"hand", "link":"hand", "openhand":"hand",
 "closedhand":"hand", "grab":"hand", "grabbing":"hand", "hand1":"hand", "pointing_hand":"hand", "context-menu":"hand",
 "copy":"hand", "alias":"hand", "dnd-link":"hand", "dnd-copy":"hand", "dnd-none":"hand", "dnd-move":"move",
 "text":"text", "xterm":"text", "ibeam":"text", "vertical-text":"text",
 "watch":"watch", "wait":"watch", "progress":"progress", "left_ptr_watch":"progress", "half-busy":"progress",
 "no-drop":"not-allowed", "dnd-no-drop":"not-allowed", "forbidden":"not-allowed", "not-allowed":"not-allowed", "crossed_circle":"not-allowed", "X_cursor":"left_ptr", "x-cursor":"left_ptr",
 "move":"move", "fleur":"move", "all-scroll":"move", "row-resize":"ns-resize",
 "col-resize":"ew-resize", "ew-resize":"ew-resize", "ns-resize":"ns-resize", "nesw-resize":"nesw-resize",
 "nwse-resize":"nwse-resize", "n-resize":"ns-resize", "s-resize":"ns-resize", "e-resize":"ew-resize",
 "w-resize":"ew-resize", "ne-resize":"nesw-resize", "nw-resize":"nwse-resize", "se-resize":"nwse-resize",
 "sw-resize":"nesw-resize", "top_side":"ns-resize", "bottom_side":"ns-resize", "left_side":"ew-resize",
 "right_side":"ew-resize", "top_left_corner":"nwse-resize", "top_right_corner":"nesw-resize",
 "bottom_left_corner":"nesw-resize", "bottom_right_corner":"nwse-resize", "top_tee":"ns-resize",
 "bottom_tee":"ns-resize", "left_tee":"ew-resize", "right_tee":"ew-resize",
 "h_double_arrow":"ew-resize", "sb_h_double_arrow":"ew-resize", "size_hor":"ew-resize",
 "v_double_arrow":"ns-resize", "sb_v_double_arrow":"ns-resize", "size_ver":"ns-resize",
 "size-hor":"ew-resize", "size-ver":"ns-resize", "size-fdiag":"nesw-resize",
 "size_fdiag":"nesw-resize", "size-bdiag":"nwse-resize", "size_bdiag":"nwse-resize",
 "size_all":"move", "ll_angle":"nwse-resize", "ur_angle":"nwse-resize",
 "lr_angle":"nesw-resize", "ul_angle":"nesw-resize", "right_ptr":"left_ptr",
 "left-arrow":"left_ptr", "right-arrow":"left_ptr", "up-arrow":"left_ptr", "down-arrow":"left_ptr",
 "arrow":"left_ptr", "based_arrow_down":"left_ptr", "based_arrow_up":"left_ptr",
 "boat":"left_ptr", "bogosity":"left_ptr", "cell":"crosshair", "circle":"crosshair",
 "color-picker":"crosshair", "draft":"left_ptr", "help":"help", "question_arrow":"help",
 "left_ptr_help":"help", "whats_this":"help", "pencil":"pencil", "plus":"crosshair",
 "pirate":"left_ptr", "zoom-in":"zoom-in", "zoom-out":"zoom-out", "wayland-cursor":"left_ptr",
 "split_h":"ew-resize", "split_v":"ns-resize",
 "00000000000000020006000e7e9ffc3f":"ns-resize", "00008160000006810000408080010102":"move",
 "03b6e0fcb3499374a867c041f52298f0":"ew-resize", "08e8e1c95fe2fc01f976f1e063a24ccd":"ew-resize",
 "1081e37283d90000800003c07f3ef6bf":"ns-resize", "3085a0e285430894940527032f8b26df":"ns-resize",
 "3ecb610c1bf2410f44200f48c40d3599":"nwse-resize", "4498f0e0c1937ffe01fd06f973665830":"nesw-resize",
 "5c6cd98b3f3ebcb1f9c7f1c204630408":"nesw-resize", "6407b0e94181790501fd1e167b474872":"ew-resize",
 "640fb0e74195791501fd1ed57b41487f":"ns-resize", "9081237383d90e509aa00f00170e968f":"ns-resize",
 "9d800788f1b08800ae810202380a0822":"nesw-resize", "a2a266d0498c3104214a47bd64ab0fc8":"nwse-resize",
 "b66166c04f8c3109214a4fbd64a50fc8":"nwse-resize", "d9ce0ab605698f320427677b458ad60b":"nesw-resize",
 "e29285e634086352946a0e7090d73106":"ew-resize", "fcf21c00b30f7e3f83fe0dfd12e71cff":"ns-resize",
}
static={"left_ptr": ("left_ptr",lambda n:(int(n*.13),int(n*.08))),
        "hand": ("hand",lambda n:(int(n*.50),int(n*.17))),
        "text": ("text",lambda n:(int(n*.23),int(n*.50))),
        "move": ("move",lambda n:(n//2,n//2)),
        "ew-resize": ("ew-resize",lambda n:(n//2,n//2)),
        "ns-resize": ("ns-resize",lambda n:(n//2,n//2)),
        "nwse-resize": ("nwse-resize",lambda n:(n//2,n//2)),
        "nesw-resize": ("nesw-resize",lambda n:(n//2,n//2)),
        "crosshair": ("crosshair",lambda n:(n//2,n//2)),
        "not-allowed": ("not-allowed",lambda n:(n//2,n//2)),
        "help": ("help",lambda n:(n//2,n//2)),
        "zoom-in": ("zoom-in",lambda n:(int(n*.3),int(n*.3))),
        "zoom-out": ("zoom-out",lambda n:(int(n*.3),int(n*.3))),
        "pencil": ("pencil",lambda n:(int(n*.18),int(n*.82)))}
for name,(shape,hot) in static.items():
    p=OUT/name
    if p.is_symlink(): p.unlink()
    write_xcursor(p,shape,[(0,0)],hot)
write_xcursor(OUT/"watch","watch",[(i,110) for i in range(6)],lambda n:(n//2,n//2))
write_xcursor(OUT/"progress","progress",[(i,100) for i in range(4)],lambda n:(n//2,int(n*.28)))
for alias,target in aliases.items():
    if alias!=target:
        try: (OUT/alias).unlink()
        except FileNotFoundError: pass
        (OUT/alias).symlink_to(target)
