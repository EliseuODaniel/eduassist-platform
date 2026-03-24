# Mockgen

Ferramentas de geracao de dados mockados para a plataforma.

Arquivos atuais:

- `seed_foundation.py`: cria a base foundation inicial para identidade, escola, academico, financeiro, calendario, documentos, conversa e auditoria.
- `seed_school_expansion.py`: enriquece uma base já existente com fundamental II, ensino médio, novos responsaveis, turmas, disciplinas, notas, frequencia, contratos, faturas e calendario ampliado.
- `seed_operational_load.py`: amplia a fila humana com handoffs incrementais, prioridades, operadores, historico e SLAs para testes operacionais.

Execucao recomendada:

1. `make db-upgrade`
2. `make db-seed-foundation`
3. `make db-seed-school-expansion`
4. `make db-seed-operational-load`
