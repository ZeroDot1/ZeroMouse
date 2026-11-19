#!/usr/bin/env python3
"""Build ZeroMouse XCursor binaries from resolution-independent Pillow drawings."""
from pathlib import Path
import struct
from math import hypot
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "zeromouse" / "cursors"
SIZES = (24, 32, 36, 48, 64, 72, 96, 128, 256, 512)
SUPERSAMPLE = 4
GREEN = (190, 255, 0, 255)
YELLOW = (234, 255, 72, 255)
DARK = (17, 35, 8, 255)

def scaled_poly(draw, points, color, s, outline=None, width=1):
    pts=[(round(x*s),round(y*s)) for x,y in points]
    draw.polygon(pts, fill=color)
    if outline: draw.line(pts+[pts[0]], fill=outline, width=max(1,round(width*s)), joint="curve")

def cubic(p0,p1,p2,p3,steps=16):
    points=[]
    for i in range(1,steps+1):
        t=i/steps; u=1-t
        points.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],
                       u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
    return points

def draw_pointer(im):
    s=im.width/64; d=ImageDraw.Draw(im)
    p=[(8,4),(8,48),(19,37),(27,55),(35,52),(27,34),(43,34)]
    scaled_poly(d,p,GREEN,s,DARK,2.5)
    d.line([(10*s,9*s),(10*s,42*s),(17*s,34*s)], fill=YELLOW,width=max(1,round(2*s)))

def draw_hand(im):
    s=im.width/64; d=ImageDraw.Draw(im)
    # A rounded pointing hand: upright index finger, thumb, and curled fingers.
    hand=[(24,40),(24,12)]
    hand+=cubic((24,12),(24,7),(27,4),(32,4))
    hand+=cubic((32,4),(37,4),(40,7),(40,12))
    hand += [(40,31),(47,26)]
    hand+=cubic((47,26),(51,23),(55,26),(55,30))
    hand+=cubic((55,30),(61,27),(64,33),(60,38))
    hand+=cubic((60,38),(63,42),(60,46),(57,48))
    hand += [(52,56)]
    hand+=cubic((52,56),(50,60),(46,62),(41,62))
    hand += [(31,62)]
    hand+=cubic((31,62),(26,62),(22,60),(19,56))
    hand += [(9,45)]
    hand+=cubic((9,45),(6,42),(7,38),(10,36))
    hand+=cubic((10,36),(13,34),(16,35),(19,38))
    hand += [(24,44)]
    coords=[(round(x*s),round(y*s)) for x,y in hand]
    d.polygon(coords,fill=GREEN)
    d.line(coords+[coords[0]],fill=DARK,width=max(1,round(2.6*s)),joint="curve")
    # One restrained crease separates the curled fingers from the palm.
    index=[(round(28*s),round(11*s)),(round(28*s),round(35*s))]
    d.line(index,fill=YELLOW,width=max(1,round(1.35*s)),joint="curve")
    if im.width >= 4*36:
        crease=[(39,40)]+cubic((39,40),(43,37),(48,36),(53,37))
        d.line([(round(x*s),round(y*s)) for x,y in crease],fill=DARK,width=max(1,round(1.0*s)),joint="curve")

def draw_text(im):
    s=im.width/64; d=ImageDraw.Draw(im)
    d.line([(14*s,7*s),(14*s,52*s)],fill=DARK,width=max(1,round(6*s)))
    d.line([(14*s,7*s),(14*s,52*s)],fill=GREEN,width=max(1,round(3*s)))
    for y in (7,52):
        d.line([(8*s,y*s),(21*s,y*s)],fill=DARK,width=max(1,round(5*s)))
        d.line([(8*s,y*s),(21*s,y*s)],fill=YELLOW,width=max(1,round(2*s)))

def draw_special(im, kind):
    s=im.width/64; d=ImageDraw.Draw(im)
    def line(a,b):
        d.line([(a[0]*s,a[1]*s),(b[0]*s,b[1]*s)],fill=DARK,width=max(1,round(7*s)))
        d.line([(a[0]*s,a[1]*s),(b[0]*s,b[1]*s)],fill=GREEN,width=max(1,round(3*s)))
    def head(p,dr):
        x, y = p
        length = hypot(*dr)
        dx, dy = (component / length for component in dr)
        px, py = -dy, dx
        scaled_poly(d,[(x+dx*9,y+dy*9),(x-dx*2+px*5,y-dy*2+py*5),(x-dx*2-px*5,y-dy*2-py*5)],YELLOW,s,DARK,1.5)
    if kind=="move":
        line((32,12),(32,52)); line((12,32),(52,32))
        for p,dr in [((32,11),(0,-1)),((32,53),(0,1)),((11,32),(-1,0)),((53,32),(1,0))]: head(p,dr)
    elif kind in ("ew-resize","ns-resize"):
        a,b=((12,32),(52,32)) if kind=="ew-resize" else ((32,12),(32,52))
        dr=(-1,0) if kind=="ew-resize" else (0,-1)
        end=(1,0) if kind=="ew-resize" else (0,1)
        line(a,b); head((a[0]+dr[0],a[1]+dr[1]),dr); head((b[0]+end[0],b[1]+end[1]),end)
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
        # A solid dark field holds the glyph together over any background.
        d.ellipse((7*s,7*s,57*s,57*s), fill=DARK,
                  outline=GREEN, width=max(1, round(3*s)))
        question = [(23,24)]
        question += cubic((23,24),(23,13),(42,13),(42,24))
        question += cubic((42,24),(42,31),(32,31),(32,37))
        width = max(1, round(5*s))
        d.line([(round(x*s), round(y*s)) for x,y in question],
               fill=YELLOW, width=width, joint="curve")
        for x, y in (question[0], question[-1]):
            d.ellipse(((x-2.5)*s,(y-2.5)*s,(x+2.5)*s,(y+2.5)*s), fill=YELLOW)
        d.ellipse((29*s,43*s,35*s,49*s), fill=YELLOW)
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
    scaled_poly(d, [(19,15),(45,15),(32,29)], DARK, s)
    scaled_poly(d, [(32,34),(45,48),(19,48)], DARK, s)
    # Sand drains from the upper chamber into the lower chamber.
    frac=(phase%6)/5
    upper_h=11*(1-frac)
    if upper_h > 0:
        half_width = upper_h * 0.8
        d.polygon([((32-half_width)*s,(28-upper_h)*s),
                   ((32+half_width)*s,(28-upper_h)*s),(32*s,28*s)],fill=YELLOW)
    d.line([(32*s,29*s),(32*s,34*s)],fill=YELLOW,width=max(1,round(2*s)))
    lower_h=max(1,round(2+10*frac))
    d.polygon([(22*s,47*s),(42*s,47*s),(32*s,(47-lower_h)*s)],fill=YELLOW)

def draw_rocket(im, phase=0):
    s=im.width/64
    layer=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    # The body rises while the exhaust lengthens, giving the loop a clear
    # lift-off motion instead of a static rocket with a blinking flame.
    phase=phase%4
    lift=(0,1,2.25,3.5)[phase]
    length=(8,11,14,17)[phase]
    d.polygon([(27*s,42*s),(37*s,42*s),(32*s,(42+length)*s)],fill=GREEN)
    d.polygon([(30*s,43*s),(34*s,43*s),(32*s,(43+max(3,length-4))*s)],fill=YELLOW)
    # Faceted nose and swept fins keep the launch symbol technical and spare.
    body=[(32,5),(40,17),(42,34),(37,44),(27,44),(22,34),(24,17)]
    scaled_poly(d,body,GREEN,s,DARK,2.5)
    scaled_poly(d,[(24,30),(16,40),(25,39)],GREEN,s,DARK,1.5)
    scaled_poly(d,[(40,30),(48,40),(39,39)],GREEN,s,DARK,1.5)
    d.line([(28*s,35*s),(36*s,35*s)],fill=YELLOW,width=max(1,round(1.5*s)))
    offset=round(lift*s)
    im.alpha_composite(layer.crop((0,offset,im.width,im.height)),(0,0))

def draw_extra(im, kind):
    s = im.width / 64
    d = ImageDraw.Draw(im)
    if kind == "up-arrow":
        scaled_poly(d, [(32,5),(51,28),(39,28),(39,56),(25,56),(25,28),(13,28)],
                    GREEN, s, DARK, 3)
    elif kind == "grab":
        palm = [(10,34),(16,31),(23,37),(23,12),(27,8),(31,12),(31,25),
                (32,8),(36,5),(40,9),(40,25),(42,12),(46,10),(50,14),
                (49,29),(51,20),(55,18),(59,22),(56,44),(46,58),
                (26,58),(20,52)]
        scaled_poly(d, palm, GREEN, s, DARK, 2.8)
    elif kind == "grabbing":
        fist = [(8,35),(16,27),(20,20),(26,18),(32,20),(36,16),
                (43,18),(46,22),(52,21),(57,26),(57,40),(48,55),
                (23,55),(14,46)]
        scaled_poly(d, fist, GREEN, s, DARK, 2.8)
        d.line([(20*s,35*s),(29*s,28*s),(40*s,33*s),(49*s,30*s)],
               fill=DARK, width=max(1, round(2.8*s)), joint="curve")
    elif kind == "vertical-text":
        draw_text(im)
        # Shift the original I-beam hotspot to the center after rotation.
        rotated = im.transpose(Image.Transpose.ROTATE_90)
        im.paste((0,0,0,0), (0,0,im.width,im.height))
        im.paste(rotated, (0,-round(18*s)))
    else:
        draw_pointer(im)
        d.rounded_rectangle((34*s,34*s,61*s,61*s), radius=5*s,
                            fill=DARK, outline=GREEN, width=max(1, round(2*s)))
        if kind == "copy":
            marks = [[(40,47),(55,47)],[(47.5,40),(47.5,55)]]
        elif kind == "context-menu":
            marks = [[(41,y),(54,y)] for y in (41,47,53)]
        else:
            marks = [[(41,54),(54,41)],[(44,41),(54,41),(54,51)]]
        for mark in marks:
            d.line([(x*s,y*s) for x,y in mark], fill=YELLOW,
                   width=max(1, round(3*s)), joint="curve")


EXTRA_ARTWORK = {
    "up-arrow", "grab", "grabbing", "vertical-text", "copy", "link",
    "context-menu", "blank",
}


def render(kind, size, phase=0):
    scaled_size=size*SUPERSAMPLE
    im=Image.new("RGBA",(scaled_size,scaled_size),(0,0,0,0))
    funcs={"left_ptr":draw_pointer,"hand":draw_hand,"text":draw_text}
    if kind in funcs: funcs[kind](im)
    elif kind in ("move","ew-resize","ns-resize","nwse-resize","nesw-resize","crosshair","not-allowed","help","zoom-in","zoom-out","pencil"): draw_special(im,kind)
    elif kind=="watch": draw_hourglass(im,phase)
    elif kind=="progress": draw_rocket(im,phase)
    elif kind in EXTRA_ARTWORK - {"blank"}: draw_extra(im,kind)
    # Resample in premultiplied-alpha space for smooth edges with no dark halos.
    return im.convert("RGBa").resize((size,size),Image.Resampling.LANCZOS).convert("RGBA")

# Xcursor file format: 16-byte header, table of contents, then image chunks.
MAGIC=0x72756358
IMAGE_TYPE=0xfffd0002
def write_xcursor(path, kind, phases, hotspot):
    entries=[]; chunks=[]; offset=16+12*(len(phases)*len(SIZES))
    for phase, delay in phases:
        for size in SIZES:
            im=render(kind,size,phase)
            hx,hy=hotspot(size)
            rgba = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
            pixels=b"".join(struct.pack("<I", (a<<24)|(r<<16)|(g<<8)|b) for r,g,b,a in rgba)
            chunk=struct.pack("<IIIIIIIII",36,IMAGE_TYPE,size,1,size,size,hx,hy,delay)+pixels
            entries.append(struct.pack("<III",IMAGE_TYPE,size,offset)); chunks.append(chunk); offset+=len(chunk)
    # Header fields are magic, header size, 16.16 version, then TOC count.
    path.write_bytes(struct.pack("<IIII",MAGIC,16,0x00010000,len(entries))+b"".join(entries)+b"".join(chunks))

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
static={"left_ptr": ("left_ptr",lambda n:(round(n*8/64),round(n*4/64))),
        "hand": ("hand",lambda n:(round(n*32/64),round(n*5/64))),
        "text": ("text",lambda n:(int(n*.23),int(n*.50))),
        "move": ("move",lambda n:(n//2,n//2)),
        "ew-resize": ("ew-resize",lambda n:(n//2,n//2)),
        "ns-resize": ("ns-resize",lambda n:(n//2,n//2)),
        "nwse-resize": ("nwse-resize",lambda n:(n//2,n//2)),
        "nesw-resize": ("nesw-resize",lambda n:(n//2,n//2)),
        "crosshair": ("crosshair",lambda n:(n//2,n//2)),
        "not-allowed": ("not-allowed",lambda n:(n//2,n//2)),
        "help": ("help",lambda n:(n//2,n//2)),
        "zoom-in": ("zoom-in",lambda n:(round(n*25/64),round(n*23/64))),
        "zoom-out": ("zoom-out",lambda n:(round(n*25/64),round(n*23/64))),
        "pencil": ("pencil",lambda n:(round(n*11/64),round(n*56/64)))}
# Qt, Wayland and historical X11 names that are still requested by applications.
aliases.update({
    "left_arrow": "left_ptr", "up_arrow": "up-arrow", "all-resize": "move",
    "bd_double_arrow": "nesw-resize", "fd_double_arrow": "nwse-resize",
    "size_bdiag": "nesw-resize", "size-bdiag": "nesw-resize",
    "size_fdiag": "nwse-resize", "size-fdiag": "nwse-resize",
    "cross_reverse": "crosshair", "wayland_cursor": "left_ptr",
    "dnd-ask": "help", "dnd-copy": "copy", "dnd-link": "link",
    "alias": "link", "openhand": "grab", "closedhand": "grabbing",
    "none": "blank", "pointer-move": "move", "dot_box_mask": "crosshair",
    "clock": "watch", "double_arrow": "ns-resize", "exchange": "move",
    "sizing": "move", "iron_cross": "crosshair", "draft_large": "left_ptr",
    "draft_small": "left_ptr", "sb_up_arrow": "up-arrow",
    "sb_down_arrow": "ns-resize", "sb_left_arrow": "ew-resize",
    "sb_right_arrow": "ew-resize",
    "0426c94ea35c87780ff01dc239897213": "watch",
    "028006030e0e7ebffc7f7070c0600140": "ew-resize",
    "50585d75b494802d0151028115016902": "nesw-resize",
    "fcf1c3c7cd4491d801f1e1c78f100000": "nesw-resize",
    "38c5dff7c7b8962045400281044508d2": "nwse-resize",
    "c7088f0f3e6c8088236ef8e1e3e70000": "nwse-resize",
    "2870a09082c103050810ffdffffe0204": "ns-resize",
    "c07385c7190e701020ff7ffffd08103c": "ns-resize",
    "043a9f68147c53184671403ffa811cc5": "ew-resize",
    "14fef782d02440884392942c11205230": "ew-resize",
    "e29285e634086352946a0e7090d73106": "hand",
    "03b6e0fcb3499374a867c041f52298f0": "not-allowed",
    "5c6cd98b3f3ebcb1f9c7f1c204630408": "help",
    "d9ce0ab605698f320427677b458ad60b": "help",
    "00000000000000020006000e7e9ffc3f": "progress",
    "08e8e1c95fe2fc01f976f1e063a24ccd": "progress",
    "00008160000006810000408080010102": "ns-resize",
    "5aca4d189052212118709018842178c0": "grab",
    "9d800788f1b08800ae810202380a0822": "grab",
    "208530c400c041818281048008011002": "grabbing",
})
for name in EXTRA_ARTWORK:
    aliases[name] = name
    if name == "up-arrow":
        hotspot = lambda n: (n // 2, round(n * 5 / 64))
    elif name in {"copy", "link", "context-menu"}:
        hotspot = static["left_ptr"][1]
    else:
        hotspot = lambda n: (n // 2, n // 2)
    static[name] = (name, hotspot)


def build_theme():
    OUT.mkdir(parents=True,exist_ok=True)
    for name,(shape,hot) in static.items():
        p=OUT/name
        if p.is_symlink(): p.unlink()
        write_xcursor(p,shape,[(0,0)],hot)
    write_xcursor(OUT/"watch","watch",[(i,110) for i in range(6)],lambda n:(n//2,n//2))
    write_xcursor(OUT/"progress","progress",[(i,100) for i in range(4)],lambda n:(n//2,round(n*5/64)))
    for alias,target in aliases.items():
        if alias!=target:
            try: (OUT/alias).unlink()
            except FileNotFoundError: pass
            (OUT/alias).symlink_to(target)

if __name__ == "__main__":
    build_theme()
