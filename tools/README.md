# Tools

Diretório reservado para ferramentas de suporte, incluindo:

- `mockgen`
- importadores
- scripts de seed
- validações operacionais

Estado atual:

- `tools/mockgen/seed_foundation.py` gera a base transacional inicial mockada;
- a seed e idempotente e pensada para ser executada apos `make db-upgrade`.
