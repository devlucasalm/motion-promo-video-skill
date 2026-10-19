import numpy as np,subprocess
from scipy.io import wavfile
from scipy.signal import butter,lfilter,fftconvolve
SR=44100;D=24.0;N=int(SR*D);rng=np.random.default_rng(11);B=60/90
def lp(x,f,o=2):b,a=butter(o,f,fs=SR);return lfilter(b,a,x)
def hp(x,f,o=2):b,a=butter(o,f,'high',fs=SR);return lfilter(b,a,x)
def bp(x,f1,f2,o=2):b,a=butter(o,[f1,f2],'band',fs=SR);return lfilter(b,a,x)
def add(buf,t,x,g=1):
    i=int(t*SR)
    if i<0 or i>=N:return
    x=x[:N-i];buf[i:i+len(x)]+=x*g
tt=lambda d:np.arange(int(d*SR))/SR
def thump(d=1.0):t=tt(d);return (np.sin(2*np.pi*(46+50*np.exp(-t*12))*t)*np.exp(-t*4.5))
def impact(d=1.8):
    t=tt(d);n=lp(rng.standard_normal(len(t)),700)*np.exp(-t*5)*.6
    return thump(d)+n
def riser(d=1.3):
    t=tt(d);n=rng.standard_normal(len(t));out=np.zeros(len(t));blk=512
    for i in range(0,len(t),blk):
        f=500+4500*(i/len(t))**2;b,a=butter(2,[f*.6,min(f*1.5,20000)],'band',fs=SR);out[i:i+blk]=lfilter(b,a,n[i:i+blk])
    return out*(t/d)**2.2*1.1
def swish(d=.35):
    t=tt(d);n=bp(rng.standard_normal(len(t)),1800,5500);return n*np.sin(np.pi*t/d)**2*.55
def shimmer(f=1760,d=2.4):
    t=tt(d);return sum(a*np.sin(2*np.pi*f*r*t+i)*np.exp(-t*(1.6+i*.6)) for i,(r,a) in enumerate([(1,1),(2.01,.5),(2.76,.35),(4.1,.2)]))*np.minimum(t/.01,1)
def tick(f=900):
    t=tt(.05);return np.sin(2*np.pi*f*t)*np.exp(-t*90)*.9
def pad(f,d):
    t=tt(d);w=sum(np.sin(2*np.pi*f*r*t+ph) for r,ph in [(1,0),(1.004,1.3),(.996,2.1)]);return lp(w,1400)*np.minimum(t/1.2,1)*np.minimum((d-t)/1.0,1)
def pluck(f,d=1.2):
    t=tt(d);return (np.sin(2*np.pi*f*t)+.35*np.sin(4*np.pi*f*t)+.12*np.sin(6*np.pi*f*t))*np.exp(-t*3.2)*np.minimum(t/.004,1)
sfx=np.zeros(N)
for w in (4,8,12,16,20):
    add(sfx,w-1.4,riser(1.3),.5);add(sfx,w-.12,impact(1.8),.9);add(sfx,w+.15,shimmer(1568,2.2),.10)
for t in (.5,2.55,5.4,5.75,8.4,8.65,13.2,13.5,14.4,16.4,16.65,21.3,21.8):add(sfx,t-.1,swish(),.55)
add(sfx,4.55,impact(2.2),.7);add(sfx,4.6,shimmer(1318,3.0),.14);add(sfx,20.45,impact(2.2),.7);add(sfx,20.5,shimmer(1318,3.0),.14)
for t in (9.5,10.05,10.6,17.3,17.85,18.4):add(sfx,t,tick(800),.45);add(sfx,t,shimmer(2093,.9),.05)
add(sfx,22.6,shimmer(1046,3.0),.16);add(sfx,22.65,shimmer(1318,3.0),.12);add(sfx,22.7,shimmer(1568,3.0),.10)
for t in np.arange(.5,4.0,.5):add(sfx,t,tick(1100),.3)
for t in (.5,2.55):add(sfx,t,tick(600),.18)
ir=rng.standard_normal(int(SR*2.2))*np.exp(-np.arange(int(SR*2.2))/SR*2.4);ir=lp(ir,6000);ir[0]=0
sfx=sfx+.28*fftconvolve(sfx,ir)[:N]
m=np.zeros(N)
ch=[(73.4,110,146.8,174.6),(58.3,87.3,116.5,146.8),(87.3,130.8,174.6,220),(65.4,98,130.8,164.8),(73.4,110,146.8,174.6),(55,82.4,110,138.6)]
for k,c in enumerate(ch):
    for f in c:add(m,k*4,pad(f,4.6),.09*(1.4 if f<90 else 1))
nb=int(D/B)
arp=[293.7,349.2,440,523.3,440,349.2]
for b in range(nb):
    t=b*B
    if t>=4 and b%2==0:add(m,t,thump(.7),.32)
    if t>=8 and b%2==1:add(m,t+B/2,hp(rng.standard_normal(int(SR*.05)),6500)*np.exp(-tt(.05)*70),.05)
    if t>=4 and b%2==0:
        f=arp[(b//2)%6]*(1 if (t//4)%2==0 else .75);add(m,t+B*.5,lp(pluck(f),3200),.08)
m=lp(m,9000,1);dl=int(B*.75*SR);m2=m.copy();m2[dl:]+=.28*m[:-dl];m=m2
m=m+.2*fftconvolve(m,ir)[:N]
x=m*.9+sfx*.9
x[:int(.05*SR)]*=np.linspace(0,1,int(.05*SR));x[-int(1.5*SR):]*=np.linspace(1,0,int(1.5*SR))
x=x/np.abs(x).max()*.85;wavfile.write('aw3.wav',SR,(x/np.abs(x).max()*.9*32767).astype(np.int16))
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','aw3.wav','-af','loudnorm=I=-16:TP=-2:LRA=11','-ar','44100','aw3n.wav'])
