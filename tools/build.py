"""Build the offline web app (www/) from the encyclopedia source.
Usage: python3 tools/build.py <source_dir_with_html_frames_stills>"""
import os,sys,re,json,shutil,hashlib
from PIL import Image
SRC=sys.argv[1];ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));W=os.path.join(ROOT,'www')
shutil.rmtree(W,ignore_errors=True)
for d in ('frames','stills','fonts','icons'):os.makedirs(os.path.join(W,d))
# 1 frames: resize + recompress
for f in sorted(os.listdir(f'{SRC}/frames')):
    if not f.endswith('.jpg'):continue
    im=Image.open(f'{SRC}/frames/{f}').convert('RGB')
    if im.width>1200:im=im.resize((1200,round(im.height*1200/im.width)),Image.LANCZOS)
    im.save(f'{W}/frames/{f}',quality=76,optimize=True,progressive=True,subsampling=2)
# 2 stills (user grabs), keep as-is
stills={}
for f in sorted(os.listdir(f'{SRC}/stills')):
    shutil.copy(f'{SRC}/stills/{f}',f'{W}/stills/{f}')
    m=re.match(r'(.+)\.(jpg|webp|png)$',f)
    if m and not f.startswith('_'):stills.setdefault(m.group(1),f)
# 3 fonts
FS=os.path.join(ROOT,'node_modules/@fontsource');css=[]
for fam,dir_,ws,ital in (('Inter','inter',(300,400,500,600),False),('Playfair Display','playfair-display',(400,600,700),True)):
    for w in ws:
        for st in (('normal','italic') if ital else ('normal',)):
            for sub,rng in (('latin','U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'),('latin-ext','U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF')):
                fn=f'{dir_}-{sub}-{w}-{st}.woff2';shutil.copy(f'{FS}/{dir_}/files/{fn}',f'{W}/fonts/{fn}')
                css.append(f"@font-face{{font-family:'{fam}';font-style:{st};font-weight:{w};font-display:swap;src:url(fonts/{fn}) format('woff2');unicode-range:{rng}}}")
# 4 icons
A=os.path.join(ROOT,'assets')
for f in ('pwa-192.png','pwa-512.png','pwa-maskable-512.png','apple-touch-icon.png','favicon.png'):shutil.copy(f'{A}/{f}',f'{W}/icons/{f}')
# 5 html
h=open(f'{SRC}/chroma_encyclopedia.html',encoding='utf-8').read()
h=re.sub(r'<link href="https://fonts.googleapis.com[^>]*>','<style>'+''.join(css)+'</style>',h)
head='''<meta name="theme-color" content="#050507"><meta name="color-scheme" content="dark">
<link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="icons/favicon.png"><link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"><meta name="apple-mobile-web-app-title" content="Chroma">
<script>window.STILLS=%s</script>'''%json.dumps(stills)
h=h.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">','<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">\n'+head,1)
# tiles: load a user still only if it exists, otherwise go straight to the AI re-enactment (no 404 chain offline)
old='src="stills/${k}.jpg" alt=""'
assert old in h
h=h.replace(old,'src="${STILLS[k]?"stills/"+STILLS[k]:"frames/ref-"+k+".jpg"}"${STILLS[k]?"":" data-r=\\"1\\""} alt=""')
h=h.replace('function nx(img){','function nx(img){if(img.dataset.r){img.remove();return}')
h=h.replace('padding:56px 24px;display:flex','padding:56px max(24px,env(safe-area-inset-right)) 56px max(24px,env(safe-area-inset-left));display:flex')
h=h.replace('#ixbtn{display:none;position:fixed;left:14px;bottom:14px;','#ixbtn{display:none;position:fixed;left:14px;bottom:calc(14px + env(safe-area-inset-bottom));')
# offline note + SW registration
sw='''<script>
const OFF=document.createElement("div");OFF.id="offbar";OFF.textContent="Offline: everything here works; FILMGRAB and image-search links need a connection.";document.body.appendChild(OFF);
const upd=()=>OFF.classList.toggle("on",!navigator.onLine);addEventListener("online",upd);addEventListener("offline",upd);upd();
if("serviceWorker"in navigator&&/^https?:$/.test(location.protocol)&&!window.Capacitor){navigator.serviceWorker.register("sw.js").then(r=>{r.addEventListener("updatefound",()=>{const n=r.installing;n&&n.addEventListener("statechange",()=>{if(n.state==="installed"&&navigator.serviceWorker.controller){const t=document.getElementById("toast");if(t){t.textContent="Updated: reload for the new version";t.classList.add("show");setTimeout(()=>t.classList.remove("show"),5000)}}})})})}
if(window.Capacitor){document.addEventListener("click",e=>{const a=e.target.closest('a[href^="http"]');if(a){e.preventDefault();e.stopImmediatePropagation();const B=window.Capacitor.Plugins&&window.Capacitor.Plugins.Browser;B?B.open({url:a.href,toolbarColor:"#050507"}):window.open(a.href,"_blank")}},true)}
</script>'''
h=h.replace('</style>','#offbar{position:fixed;top:0;left:0;right:0;z-index:50;background:#3a2a12;color:#f4e2c0;font:500 12.5px Inter;text-align:center;padding:calc(6px + env(safe-area-inset-top)) 12px 6px;transform:translateY(-100%);transition:transform .25s}#offbar.on{transform:none}\n</style>',1)
i=h.rfind('</body>');h=h[:i]+sw+h[i:]
open(f'{W}/index.html','w',encoding='utf-8').write(h)
# 6 manifest
json.dump({"name":"Chroma: Cinematic Color Encyclopedia","short_name":"Chroma","description":"Offline reference on color in film: hue psychology, palettes, narrative devices, auteurs, with Nigerian-context frames.","start_url":"./","scope":"./","display":"standalone","orientation":"any","background_color":"#050507","theme_color":"#050507","categories":["education","reference","photo"],
 "icons":[{"src":"icons/pwa-192.png","sizes":"192x192","type":"image/png"},{"src":"icons/pwa-512.png","sizes":"512x512","type":"image/png"},{"src":"icons/pwa-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]},open(f'{W}/manifest.webmanifest','w'),indent=1)
# 7 service worker: precache everything, versioned by content hash
files=[]
for dp,_,fs in os.walk(W):
    for f in fs:
        rel=os.path.relpath(os.path.join(dp,f),W).replace(os.sep,'/')
        if rel!='sw.js':files.append(rel)
files.sort();hs=hashlib.sha1()
for f in files:hs.update(f.encode());hs.update(open(os.path.join(W,f),'rb').read())
ver=hs.hexdigest()[:10]
open(f'{W}/sw.js','w').write(f'''const V="chroma-{ver}",FILES={json.dumps(["./"]+files)};
self.addEventListener("install",e=>{{e.waitUntil(caches.open(V).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()))}});
self.addEventListener("activate",e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});
self.addEventListener("fetch",e=>{{const u=new URL(e.request.url);if(e.request.method!=="GET"||u.origin!==location.origin)return;
 e.respondWith(caches.match(e.request,{{ignoreSearch:true}}).then(r=>r||fetch(e.request).catch(()=>new Response("",{{status:404}}))))}});
''')
open(f'{W}/.nojekyll','w').close()
tot=sum(os.path.getsize(os.path.join(W,f)) for f in files)
print(f'{len(files)} files, {tot/1e6:.1f} MB, version {ver}, stills {len(stills)}')
