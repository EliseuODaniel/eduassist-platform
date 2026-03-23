# ADR 0001: Rebuild completo do zero

## Status

Aceito

## Contexto

O repositório anterior serviu como protótipo de validação conceitual. Ele cumpriu função importante de contexto de domínio, mas não oferece base adequada para a próxima fase do projeto, que exige:

- arquitetura mais robusta;
- segurança da informação como requisito central;
- bancos reais com dados mockados consistentes;
- separação clara entre canal, domínio, IA, identidade e policy;
- documentação adequada para orientar implementação e redação técnica.

Também há divergência entre o escopo agora desejado e o escopo original do protótipo:

- o novo sistema deve atender múltiplos perfis institucionais;
- o novo sistema deve operar sobre um ecossistema escolar mais completo;
- o novo sistema deve ser pensado para execução local controlada e expansão futura.

## Decisão

O projeto será reiniciado em um novo repositório, com nova arquitetura e nova documentação, sem compromisso de reaproveitamento de código do protótipo anterior.

O protótipo anterior será tratado apenas como:

- referência de domínio;
- referência histórica;
- insumo para reformulação do documento acadêmico.

## Consequências

### Positivas

- reduz dívida técnica herdada;
- permite modelagem correta de segurança desde o início;
- evita acoplamentos incorretos entre IA, Telegram e banco;
- melhora a clareza arquitetural;
- facilita documentação e governança.

### Negativas

- o tempo até a primeira versão funcional será maior do que fazer remendos no protótipo;
- todo bootstrap inicial terá de ser refeito;
- decisões de escopo e contratos precisarão ser formalizadas desde o começo.

## Diretrizes derivadas

- usar `Docker Compose` como ambiente base;
- adotar `Python + FastAPI` para backend principal;
- adotar `Next.js` para painel administrativo;
- usar `PostgreSQL`, `Redis`, `MinIO`, `Keycloak`, `OPA` e `OpenTelemetry`;
- usar orquestração de IA governada, com ferramentas auditáveis;
- documentar todas as decisões relevantes em ADRs subsequentes.

