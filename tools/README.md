# Tools

Diretório reservado para ferramentas de suporte, incluindo:

- `mockgen`
- importadores
- scripts de seed
- validações operacionais

Estado atual:

- `tools/mockgen/seed_foundation.py` gera a base transacional inicial mockada;
- `tools/mockgen/sync_auth_bindings.py` sincroniza as identidades federadas locais com os usuarios do realm `eduassist`;
- `tools/ops/check_db_runtime_role.py` valida que o runtime do banco está usando um papel não-superuser;
- `tools/ops/check_db_rls.py` valida a barreira de `RLS` diretamente com o papel `eduassist_app`;
- o corpus documental inicial esta versionado em [data/corpus/public](/home/edann/projects/eduassist-platform/data/corpus/public);
- a seed e idempotente e pensada para ser executada apos `make db-upgrade`.
