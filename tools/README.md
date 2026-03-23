# Tools

Diretório reservado para ferramentas de suporte, incluindo:

- `mockgen`
- importadores
- scripts de seed
- validações operacionais

Estado atual:

- `tools/mockgen/seed_foundation.py` gera a base transacional inicial mockada;
- `tools/mockgen/seed_operational_load.py` adiciona carga operacional incremental para filas humanas, prioridades e SLAs mais realistas;
- `tools/mockgen/sync_auth_bindings.py` sincroniza as identidades federadas locais com os usuarios do realm `eduassist`;
- `tools/graphrag-benchmark` prepara um workspace opt-in para benchmark seletivo de `GraphRAG` sobre o corpus institucional publico, com bootstrap, dataset de perguntas e runner comparativo contra o baseline hibrido;
- `tools/ops/check_db_runtime_role.py` valida que o runtime do banco está usando um papel não-superuser;
- `tools/ops/check_db_rls.py` valida a barreira de `RLS` diretamente com o papel `eduassist_app`;
- `tools/ops/backup_local_stack.sh` gera backup local de `Postgres`, `Qdrant` e `MinIO` com manifesto;
- `tools/ops/verify_local_backup.sh` executa restore de verificação em banco, coleção e bucket temporários;
- o corpus documental inicial esta versionado em [data/corpus/public](/home/edann/projects/eduassist-platform/data/corpus/public);
- as seeds sao idempotentes e pensadas para serem executadas apos `make db-upgrade`.
