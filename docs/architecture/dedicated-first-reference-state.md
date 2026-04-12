# Dedicated-First Reference State

## O que mudou

Depois do merge da arquitetura de orquestradores independentes, a referência operacional do projeto deixou de ser um único entrypoint central com uma tabela antiga de benchmark. O estado canônico agora combina:

- `ai-orchestrator` como `control plane/router`;
- quatro runtimes dedicados como caminho principal de serving:
  - `langgraph`
  - `python_functions`
  - `llamaindex`
  - `specialist_supervisor`
- validação composta por smoke single-turn, multi-turn, memória longa, Telegram real e parity operacional.
- um contrato compartilhado de `semantic ingress` para atos de entrada de alta precedência, como `greeting`, `auth_guidance`, `language_preference`, `input_clarification` e `scope_boundary`.

## Superfícies de validação recomendadas

### Dedicated runtime smoke

- alvo: `make smoke-dedicated`
- objetivo: validar `/healthz`, `/v1/status` e cenários essenciais de serving em cada runtime dedicado.

### Dedicated multi-turn

- alvo: `make smoke-dedicated-multiturn`
- artefato local típico: `artifacts/dedicated-stack-multiturn-report.json`
- objetivo: cobrir troca de escopo, troca de aluno, boundary público e follow-up curto.

### Dedicated long-memory

- alvo: `make smoke-dedicated-long-memory`
- artefato local típico: `artifacts/dedicated-stack-long-memory-report.json`
- objetivo: cobrir digressões longas, retorno a contexto anterior, correção tardia e retomada de workflow.

### Dedicated semantic ingress

- alvo: `make smoke-dedicated-semantic-ingress`
- artefato local típico: `artifacts/dedicated-stack-semantic-ingress-report.json`
- objetivo: validar a superfície semântica compartilhada de entrada, incluindo saudações variáveis, guidance de autenticação, preferência de idioma, clarificação segura de entradas opacas e abstention segura fora do escopo.

### Telegram dedicated smoke

- alvo: `make smoke-telegram-dedicated`
- artefato local típico: `artifacts/telegram-gateway-dedicated-smoke-report.json`
- objetivo: validar o caminho real `telegram-gateway -> runtime dedicado -> api-core`.

### Runtime parity

- alvo: `make runtime-parity-check`
- artefato local típico: `artifacts/dedicated-runtime-parity-report.json`
- objetivo: detectar drift entre `source mode`, Docker, gateway e runtimes dedicados.

### Promotion gate

- alvo: `make promotion-gate-check`
- artefatos locais típicos:
  - `artifacts/promotion-gate/*.json`
  - `artifacts/promotion-gate/*.md`
- objetivo: consolidar edge pública, smoke dedicado, multi-turn, memória longa, Telegram, parity e scorecard de rollout.

### Scorecard e rollout controlado

- o scorecard canônico agora é carregado automaticamente tanto em Docker quanto em source mode;
- caminhos suportados por padrão:
  - `artifacts/framework-native-scorecard.json`
  - `docs/architecture/framework-native-scorecard.json`
- o rollout só deve sair do modo observacional quando houver:
  - `scorecard` carregado
  - slices explícitos
  - rollout percentual ou allowlist declarados
  - e, quando aplicável, `pilot` saudável

### Política do control plane

- `ai-orchestrator` é `control-plane-router`
- o serving principal de usuário deve sair de um runtime dedicado
- o compat mode do control plane existe apenas para manutenção, smoke legado e debug explícito

## Relação com a documentação histórica

Os documentos abaixo continuam relevantes porque explicam a motivação e o fechamento da migração:

- [Independent Orchestrators Architecture](independent-orchestrators-architecture-20260406.md)
- [Fechamento da Rodada de Avaliacao da Branch de Orquestradores Independentes](independent-orchestrators-eval-closeout-20260406.md)

## Leitura honesta

Hoje, a melhor forma de afirmar que o sistema está saudável não é olhar apenas um score antigo de `50Q`. O estado de referência do projeto precisa combinar:

1. serving correto por runtime dedicado;
2. estabilidade de conversa curta e longa;
3. surface semântica de entrada consistente entre as stacks;
4. caminho real do Telegram;
5. parity operacional;
6. gate de promoção coerente com o scorecard e com a borda pública disponível.

## Risco restante mais importante

O maior risco operacional que ainda pode existir fora do código é a borda pública:

- `TryCloudflare` continua aceitável para desenvolvimento rápido;
- `named tunnel` continua sendo o caminho recomendado para uma borda estável de demonstração prolongada.
