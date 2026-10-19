---
name: "motion-promo-video"
description: "Cria vídeos promocionais de motion design premium (9:16 / 16:9, 60fps, com SFX/música) para produtos, SaaS, relógios etc. a partir de HTML+Playwright+ffmpeg. Use para pedidos de motion, vídeo de anúncio, reels, promo animado."
---

# Motion promo video (HTML → MP4)

Entrega: MP4 pronto (H.264, yuv420p, AAC) enviado com SendUserFile. Responda em pt-BR, curto.

## 1. Briefing mínimo (não pergunte demais)
Defina por padrão e só pergunte o que muda o resultado:
- Formato: 9:16 (1080×1920) padrão; 16:9 (1920×1080) se pedido. Duração: anúncio Insta 20–35 s; pacing LENTO (cada passo ~1,5–4 s) — o usuário já reclamou de "parece 2x".
- Público: jovem/SaaS → SFX brilhantes (sinos, pops, clicks). Público mais velho/premium (relógios, joias) → sóbrio: pads, impactos suaves, whooshes, shimmers; NADA de pop infantil.
- Marca: paleta, fonte, logo, CTA (WhatsApp/URL), prints/fotos. Música: se o usuário citar uma faixa (Spotify etc.), você NÃO acessa o áudio — avise, use trilha original e ofereça sincronizar se ele enviar o mp3 (e lembre da licença para anúncios).

## 2. Preparar assets
- Fotos de produto: tirar fundo com `rembg` (modelo isnet-general-use) → PNG com alpha para efeito "3D" (flutuar, rotateY/rotateX com perspective, brilho `sheen` mascarado pelo alpha do PNG via `-webkit-mask-image`).
- Prints de baixa resolução: upscale Lanczos 3× + UnsharpMask. Remova textos de anúncio da foto original quando o usuário pedir "sem anúncio".
- Fontes: Inter / Inter Display ExtraBold (SaaS, estilo flat), Lora serif + itálico dourado (premium), Poppins.

## 3. Estilo que o usuário aprovou
- Blocos de cor chapados, cards grandes, tipografia gigante com reveal por palavra mascarada, muito movimento contínuo (parallax lento, zoom lento 1→1.15, estrelas/partículas), cortes por wipes de 3 painéis coloridos sincronizados com o beat.
- SEM tremida de câmera (o usuário rejeitou shake): shake ×0.12 no máximo, sem rotação de câmera, drift ≤3 px.
- Estrutura narrativa: gancho/problema → solução → 2–3 features/integração → prova/benefício → CTA. Cada cena 3–5 s, wipe entre elas. Em SaaS, mostrar o PROBLEMA de forma concreta (mensagem sem resposta, venda perdida −R$) antes da solução.
- Textos curtos, 2–4 palavras por linha, em pt-BR, com uma palavra destacada (cor/itálico). Respeitar safe zone do Instagram (evitar ~250 px topo e ~400 px base em 9:16 para CTA/legenda).

## 4. Engine (HTML determinístico)
Um arquivo `video.html` com `window.seek(T)` que posiciona TUDO em função do tempo T (sem requestAnimationFrame/CSS animations). Núcleo:
```js
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)),lerp=(a,b,p)=>a+(b-a)*p;
const E={outBack:(p,c=1.8)=>1+(c+1)*Math.pow(p-1,3)+c*Math.pow(p-1,2),outExpo:p=>p>=1?1:1-Math.pow(2,-10*p),outQuart:p=>1-Math.pow(1-p,4),inOutQuart:p=>p<.5?8*p**4:1-Math.pow(-2*p+2,4)/2,inOutCubic:p=>p<.5?4*p**3:1-Math.pow(-2*p+2,3)/2,lin:p=>p,inCubic:p=>p**3,inOutSine:p=>-(Math.cos(Math.PI*p)-1)/2};
const ez=(T,a,d,f=E.outExpo)=>f(cl((T-a)/d));
function mk(parent,html,cls='',style=''){const d=document.createElement('div');d.className='abs '+cls;d.style.cssText=style;d.innerHTML=html;parent.appendChild(d);return d} // .abs{position:absolute;left:50%;top:50%}
function P(el,o){const x=o.x||0,y=o.y||0,s=o.s==null?1:o.s,op=o.o==null?1:o.o,r=o.r||0,rx=o.rx||0,ry=o.ry||0;el.style.transform=`perspective(2400px) translate(-50%,-50%) translate(${x}px,${y}px) rotateX(${rx}deg) rotateY(${ry}deg) rotate(${r}deg) scale(${s})`;el.style.opacity=op;el.style.visibility=op<=.003?'hidden':'visible'}
function words(el,arr){el.innerHTML=arr.map(w=>`<span class="mk"><span class="wd ${w[1]||''}">${w[0]}</span></span>`).join(' ')} // .mk{display:inline-block;overflow:hidden;padding:.14em .05em .24em;margin:-.14em -.05em -.24em}
function lineIO(el,T,tin,tout,step=.1,d=1.0){[...el.querySelectorAll('.wd')].forEach((w,i)=>{const a=ez(T,tin+i*step,d,E.outQuart),b=tout?ez(T,tout+i*step*.5,.5,E.inCubic):0;w.style.transform=`translateY(${(1-a)*118-b*118}%)`;w.style.opacity=cl(a*2.2,0,1)*(1-b)})}
function addScene(a,b,bg,build,upd,cam){/* cria div.sc com bg, inner; scenes.push({a,b,root,inner,obj:build(inner),upd,cam}) */}
function runScenes(T){/* display só se T em [a-.02,b+.02]; inner.style.transform=translate/scale da cam(t,T); s.upd(t,obj,T) */}
// wipes: 3 painéis [cor escura, dourado/accent, cor do fundo da próxima cena], cada um ez(T,t0+i*.09,.38,E.inOutQuart) entrando e saindo (t0=wipe-.55); alternar direção x / xr
function seek(T){runScenes(T);drawWipes(T);drawFX(T);drawGrain(T);/* fade preto final */}
```
Camadas fixas acima do mundo: canvas de poeira/partículas, wipes, grão de filme (alpha .07), vinheta, véu preto para fade-in/out.
Efeito 3D de produto: `P(hero,{ry:Math.sin(T*.7)*8, rx:Math.sin(T*.5)*3, y:Math.sin(T*1.1)*14, s})` + `sweep()` (faixa de brilho `mix-blend-mode:soft-light` mascarada pelo PNG) + glow radial dourado atrás + sombra `drop-shadow`.
Abertura tipo relógio (aprovada pelo usuário na v1 dos relógios): SVG 760 px com 60 ticks (a cada 5 mais grossos/dourados), arco dourado que se desenha (stroke-dashoffset), ponteiro que avança 6° a cada 0,5 s com `E.outBack`, ticks já percorridos acendem; texto "O tempo passa pra todo mundo. / Poucos deixam marca."; estrelinhas ✦ girando. Reuse esse tipo de abertura temática quando o produto permitir.
Timeline com velocidade variável: `SEG=[[ini,fim,fator],…]` aplicado em `seek` E na função `M(t)` do áudio para os SFX seguirem os cortes.

## 5. Render (deterministico, retomável)
- Playwright Chromium viewport 1080×1920 (ou 1920×1080), `page.evaluate('seek(t)')` + `screenshot(type='jpeg',quality=92)`.
- 60 fps com motion blur: 2 sub-quadros por frame (t=(f+(s+.5)/2-.5)/60), média em numpy float32 → JPEG q95 → `ffmpeg -f image2pipe -c:v mjpeg -i - -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p seg/NNNNN.mp4`.
- Chunks de 120 frames em `seg/`, 2 processos paralelos (chunks pares/ímpares), pula chunk existente (container pode reiniciar). Rode com `setsid nohup ./go.sh &` e use Monitor com until-loop num arquivo done (sleep em foreground é bloqueado; reative o Monitor se expirar em 30 min). ~0,38 s por screenshot, 2 CPUs: 24 s ≈ 1440 frames ≈ 25–30 min.
- Alterou só o começo? Apague só os chunks afetados e re-renderize; se só o áudio mudou, remuxe com `-c:v copy`.
- Concat: `ffmpeg -f concat -safe 0 -i list.txt -i audio.wav -c:v libx264 -crf 21 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart out.mp4`.
- Antes de renderizar tudo, tire 2–4 screenshots de `seek()` em tempos-chave e CONFIRA texto cortado/overflow nos dois formatos (já aconteceu com fonte grande demais), e erros JS (`page.on('pageerror')`).

## 6. Áudio (numpy/scipy, sintetizado)
Helpers: `lp/hp/bp` (butter), `add(buf,t,x,g)`, `tt(d)`; sons: `thump` (seno 46–96 Hz decaindo), `impact` (thump+ruído lp 700), `riser` (ruído com banda subindo), `swish` (ruído bp 1.8–5.5 kHz, janela sin²), `shimmer` (parciais inarmônicos com decaimento), `tick` (seno ~900 Hz, decay 90), `pad` (3 senos desafinados lp 1.4 kHz com fade), `pluck`; reverb por convolução com ruído decaindo.
- SaaS/jovem: sinos brilhantes, pops, clicks, whooshes — NÃO usar graves pesados (o usuário detestou "tudo grave").
- Premium/velho: riser+impact nos wipes, swish nos reveals de texto, shimmer na entrada do produto, ticks nas listas, tick de relógio a cada 0,5 s na abertura de relógio, pads em acordes lentos (Dm–Bb–F–C), batida suave ~90 bpm. Beat 80–90 bpm combina com cortes a cada 4 s.
- MASTERIZAÇÃO (evita "estourado"): NUNCA `tanh` num mix quente. Faça `x=x/np.abs(x).max()*.85`, salve wav e rode `ffmpeg -af loudnorm=I=-16:TP=-2:LRA=11 -ar 44100`. Verifique pico < −1 dBFS e crest factor > 10 dB.

## 7. Entrega e iteração
Envie o MP4 com legenda de 1 linha; mencione o que mudou e o que NÃO foi verificado (ex.: "conferi quadros e métricas, não ouvi"). Feedbacks típicos e resposta: "muito rápido" → escale a timeline ×1.5; "tremido" → reduza shake; "som ruim" → troque o perfil de SFX (brilhante vs. sóbrio); "estourado" → remasterize só o áudio e remuxe; "gostei da animação X da v1" → traga a cena X de volta, re-render só dos chunks afetados.
Se o usuário pedir um prompt/documentação reutilizável, gere um doc com este fluxo.