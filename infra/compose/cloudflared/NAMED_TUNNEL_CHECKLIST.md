# Named Tunnel Checklist

Use este checklist para tirar o Telegram do `TryCloudflare` e passar para um `named tunnel` estável nesta branch.

## Objetivo

Deixar o webhook do Telegram apontando para uma URL pública estável, usando:

- `CLOUDFLARED_TUNNEL_TOKEN`
- `TELEGRAM_PUBLIC_BASE_URL`

Fluxo final esperado:

```bash
make telegram-public-up-stable
make telegram-webhook-health
make telegram-webhook-info
```

## Pré-requisitos

- Docker Desktop funcionando
- stack local da branch disponível
- `TELEGRAM_BOT_TOKEN` configurado no `.env`
- `TELEGRAM_WEBHOOK_SECRET` configurado no `.env`
- acesso ao dashboard da Cloudflare da zona que hospedará o hostname público

## 1. Criar ou escolher o hostname público

Escolha um hostname estável para o webhook, por exemplo:

- `eduassist-bot.seudominio.com`

Esse hostname será usado em:

- `TELEGRAM_PUBLIC_BASE_URL=https://eduassist-bot.seudominio.com`

## 2. Criar o named tunnel na Cloudflare

No dashboard da Cloudflare:

1. Vá em `Networking > Tunnels`.
2. Crie um novo tunnel remoto.
3. Dê um nome claro, por exemplo:
   - `eduassist-telegram-local`
4. Copie o token do tunnel.

Alternativa por API:

- a doc oficial mostra criação remota de tunnel por API e retorno de `id` e `token`

## 3. Configurar o public hostname do tunnel

Ainda na Cloudflare, associe o tunnel ao hostname público escolhido:

- hostname: `eduassist-bot.seudominio.com`
- service/origin: o serviço publicado será o `telegram-gateway` desta branch

Nesta branch, o `cloudflared` já aponta para:

- `CLOUDFLARED_TARGET_URL=http://telegram-gateway:8000`

Então o `named tunnel` deve rotear esse hostname para o container local via `cloudflared`.

## 4. Preencher o `.env` local

Adicione no `.env` da branch:

```env
CLOUDFLARED_TUNNEL_TOKEN=eyJ...
TELEGRAM_PUBLIC_BASE_URL=https://eduassist-bot.seudominio.com
CLOUDFLARED_ALLOW_QUICK_TUNNEL=false
```

Garanta também que estes valores já existam:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_WEBHOOK_SECRET=...
INTERNAL_API_TOKEN=...
```

## 5. Subir o caminho estável

Execute:

```bash
make telegram-public-up-stable
```

Esse alvo:

- sobe `telegram-gateway`
- sobe `cloudflared`
- recusa `quick tunnel` se o token estável não estiver configurado
- registra o webhook do Telegram

## 6. Validar a URL pública

Cheque se a URL pública configurada responde:

```bash
make telegram-webhook-health
```

Resultado esperado:

- `ok: true`
- `public_base_url` igual ao hostname estável
- `healthcheck_url` apontando para `https://.../healthz`

## 7. Confirmar o webhook no Telegram

Execute:

```bash
make telegram-webhook-info
```

Verifique:

- `url` termina com `/webhooks/telegram`
- `pending_update_count` não cresce indefinidamente
- não há `last_error_message`

## 8. Validar o caminho end-to-end

Confirme localmente:

- `telegram-gateway` saudável
- runtime dedicado alvo saudável
- webhook público saudável

Depois mande uma mensagem real no bot e confira:

- entrega no Telegram
- logs do `telegram-gateway`
- resposta do runtime dedicado

## 9. Critério de pronto

Considere o named tunnel pronto quando:

- o `cloudflared` subir sem `trycloudflare`
- o webhook do Telegram apontar para o hostname estável
- o `telegram-webhook-health` responder `ok`
- o bot responder no Telegram sem depender de reciclar URL pública efêmera

## 10. Troubleshooting rápido

Se `make telegram-public-up-stable` falhar:

- confira se `CLOUDFLARED_TUNNEL_TOKEN` está preenchido
- confira se `TELEGRAM_PUBLIC_BASE_URL` está preenchido
- confira se o hostname público configurado no dashboard bate exatamente com o `.env`

Se `make telegram-webhook-health` falhar:

- valide o roteamento do hostname no dashboard da Cloudflare
- confira logs do container `eduassist-cloudflared`
- confira se `telegram-gateway` está saudável

Se `make telegram-webhook-info` mostrar erro:

- confira `TELEGRAM_BOT_TOKEN`
- confira `TELEGRAM_WEBHOOK_SECRET`
- registre de novo com `make telegram-public-up-stable`

## Referências oficiais

- Cloudflare Tunnel overview:
  - https://developers.cloudflare.com/tunnel/
- Set up Cloudflare Tunnel:
  - https://developers.cloudflare.com/tunnel/setup/
- Tunnel run parameters (`token`):
  - https://developers.cloudflare.com/tunnel/advanced/run-parameters/
- Tunnel tokens:
  - https://developers.cloudflare.com/tunnel/advanced/tunnel-tokens/
- Quick Tunnels:
  - https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/
