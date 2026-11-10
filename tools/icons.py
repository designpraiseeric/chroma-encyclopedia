import math,os
from PIL import Image,ImageDraw,ImageFilter
OUT=os.path.join(os.path.dirname(__file__),'..','assets');os.makedirs(OUT,exist_ok=True)
HUES=[(227,24,55),(255,106,0),(255,209,0),(46,204,64),(0,116,217),(128,0,128),(255,20,147),(227,24,55)]
def lerp(a,b,t):return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def conic(n):
    im=Image.new('RGB',(n,n));px=im.load();c=n/2
    for y in range(n):
        for x in range(n):
            a=(math.atan2(y-c,x-c)+math.pi/2)%(2*math.pi)/(2*math.pi)*(len(HUES)-1);i=int(a);px[x,y]=lerp(HUES[i],HUES[i+1],a-i)
    return im
def mark(S,bg=True,scale=1.0):
    n=1024;g=conic(n)
    m=Image.new('L',(n,n),0);d=ImageDraw.Draw(m);r=n*0.36*scale;w=n*0.11*scale;c=n/2
    d.ellipse((c-r,c-r,c+r,c+r),fill=255);d.ellipse((c-r+w,c-r+w,c+r-w,c+r-w),fill=0)
    # gap to make a "C"
    d.pieslice((c-r-4,c-r-4,c+r+4,c+r+4),-28,28,fill=0)
    base=Image.new('RGBA',(n,n),(5,5,7,255) if bg else (0,0,0,0))
    glow=Image.new('RGBA',(n,n),(0,0,0,0));glow.paste(g,(0,0),m.filter(ImageFilter.GaussianBlur(18)).point(lambda v:int(v*.55)))
    base.alpha_composite(glow);ring=Image.new('RGBA',(n,n),(0,0,0,0));ring.paste(g,(0,0),m);base.alpha_composite(ring)
    dot=ImageDraw.Draw(base);rr=n*0.055*scale;dot.ellipse((c+r*0.62-rr,c-rr,c+r*0.62+rr,c+rr),fill=(244,244,245,255))
    return base.resize((S,S),Image.LANCZOS)
mark(1024).save(f'{OUT}/icon-only.png')
mark(1024,bg=False,scale=0.72).save(f'{OUT}/icon-foreground.png')
Image.new('RGBA',(1024,1024),(5,5,7,255)).save(f'{OUT}/icon-background.png')
sp=Image.new('RGBA',(2732,2732),(5,5,7,255));sp.alpha_composite(mark(900,bg=False),(916,916));sp.save(f'{OUT}/splash.png');sp.save(f'{OUT}/splash-dark.png')
for s in (192,512):mark(s).save(f'{OUT}/pwa-{s}.png')
mark(512,scale=0.78).save(f'{OUT}/pwa-maskable-512.png')
mark(180).convert('RGB').save(f'{OUT}/apple-touch-icon.png')
mark(64).save(f'{OUT}/favicon.png')
print('ok')
