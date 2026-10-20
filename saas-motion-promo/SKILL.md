---
name: "saas-motion-promo"
description: "Cria vídeo promocional em motion design (16:9 ou 9:16) de um produto SaaS com HyperFrames: abertura de problema, frases de impacto, cenas por função, trilha e SFX gerados e CTA."
---

# Vídeo promo SaaS (HyperFrames)

Responder em pt-BR, conciso. Entregar MP4 + resumo curto do que tem em cada cena.

## 1. Marca e conteúdo
- WebFetch do site: headline, funções, números, CTA, theme-color.
- Cores/fonte reais: procurar repo do produto (`list_repos`, clonar, ler tokens CSS/tailwind). Logo: copiar do repo se existir.
- Se não achar logo/cores: usar wordmark em texto + theme-color, avisar e pedir o SVG.
- Dados no vídeo sempre fictícios (clientes, CNPJ, chaves, placas). Nunca copiar dados reais de prints do usuário.

## 2. Projeto
- `npx hyperframes init <nome>`; reaproveitar `node_modules` de projeto anterior via symlink.
- GSAP local (`npm i gsap`) e fonte local via `@fontsource/<fonte>` com `@font-face` apontando para `node_modules/.../files/*.woff2`.
- Chromium: `export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (download do headless-shell falha).

## 3. Roteiro (padrão aprovado)
1. **Abertura problema (~9s):** relógio odômetro rolando (dígitos em strip, `y: -n*altura`), notificações empilhando (nova na frente, antigas sobem/encolhem/esmaecem), elementos de caos; final varre tudo e entra frase de dor.
2. **Frases (~4s):** fundo da cor da marca com listras, abertura em `clip-path: circle()`, 3 frases batendo palavra a palavra (escala 2.2→1).
3. **Hook (~4s):** nome grande + "O sistema que" + palavras trocando (rotateX).
4. **Uma cena por função (5,5–9s):** chip numerado "0N · Função", título com marca-texto animado, UI recriada com ação real (digitação, consulta, card movendo, contador, carimbo, toast WhatsApp). Alternar fundo claro/escuro.
5. **CTA (~4,5s):** flash, nome, headline do site, número do site, botão com clique, URL.
- Wipes entre cenas (2 camadas, cor marca + escura) e barra de progresso por função.
- Formato 16:9 (1920×1080) é o preferido; 9:16 (1080×1920) quando pedido.

## 4. Regras técnicas (já deram problema)
- IDs únicos por cena (prefixo da cena). ID repetido faz uma animação mexer em outra.
- Só animar transform/opacity: nada de `left/top/letterSpacing` em tween (lint `gsap_non_transform_motion`).
- Contadores: `fromTo` com `textContent` + `modifiers` + `immediateRender: false`.
- Tweens extras no mesmo alvo (shake, pulse): `fromTo(..., immediateRender: false)`.
- Wipe: estado escondido só via tween (`xPercent`/`yPercent`), nunca `transform` no CSS.
- Determinismo: RNG próprio (LCG), sem `Math.random`/`Date.now`.
- Contraste: textos pequenos em pílula azul clara usar azul escuro (#1447b8); timestamps em balão escuro usar #c3cdd3.
- Avisos aceitáveis no check: sobreposição de notificações empilhadas, páginas de calendário, texto só contorno, dígitos ocultos do relógio.

## 5. Áudio (gerado, sem direitos)
- `audio/synth.py` (numpy+scipy): trilha 120 BPM (pad, baixo, arpejo, kick/snare/hat), intro tensa sem bateria, drop na cena de frases, riser + impacto no CTA.
- SFX no tempo exato das animações: pop, blip, click, tecla, sino/notificação, whoosh nos cortes, carimbo, obturador, telefone, caixa registradora, sucesso.
- Duas faixas `<audio>` (bgm 0.8, sfx 1.0) com `data-start=0` e duração total.

## 6. Verificar e entregar
- `npx hyperframes@<versão do package.json> snapshot --at t1,t2,... --no-end -o /tmp/x .` por cena; ler contact sheet e corrigir.
- `npm run check`, depois `npm run render`.
- Contact sheet do MP4 com ffmpeg (14 quadros, tile 4x4) + `volumedetect`.
- Enviar com SendUserFile (display render) e resumo por cena + o que é fictício.