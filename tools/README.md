# Tools

Diretório reservado para ferramentas de suporte, incluindo:

- `mockgen`
- importadores
- scripts de seed
- validações operacionais

Estado atual:

- `tools/mockgen/seed_foundation.py` gera a base transacional inicial mockada;
- `tools/mockgen/sync_auth_bindings.py` sincroniza as identidades federadas locais com os usuarios do realm `eduassist`;
- a seed e idempotente e pensada para ser executada apos `make db-upgrade`.
