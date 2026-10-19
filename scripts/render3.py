import sys,subprocess,io,os,numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
par=int(sys.argv[1]);FPS=60;SUB=2;nf=1440;CH=120
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto('file:///home/claude/watch/w3.html');pg.wait_for_timeout(800)
    for ci,c in enumerate(range(0,nf,CH)):
        if ci%2!=par:continue
        out=f'seg3/{c:05d}.mp4'
        if os.path.exists(out):continue
        ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',out+'.tmp.mp4'],stdin=subprocess.PIPE)
        for f in range(c,min(c+CH,nf)):
            acc=None
            for s in range(SUB):
                t=(f+(s+.5)/SUB-.5)/FPS;pg.evaluate(f'seek({max(t,0)})')
                a=np.asarray(Image.open(io.BytesIO(pg.screenshot(type='jpeg',quality=92))),dtype=np.float32)
                acc=a if acc is None else acc+a
            bio=io.BytesIO();Image.fromarray((acc/SUB).astype(np.uint8)).save(bio,'JPEG',quality=95);ff.stdin.write(bio.getvalue())
        ff.stdin.close();ff.wait();os.rename(out+'.tmp.mp4',out)
    b.close()
