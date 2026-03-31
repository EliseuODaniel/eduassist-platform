# Mockgen

Ferramentas de geracao de dados mockados para a plataforma.

Arquivos atuais:

- `seed_foundation.py`: cria a base foundation inicial para identidade, escola, academico, financeiro, calendario, documentos, conversa e auditoria.
- `seed_school_expansion.py`: enriquece uma base já existente com fundamental II, ensino médio, novos responsaveis, turmas, disciplinas, notas, frequencia, contratos, faturas e calendario ampliado.
- `seed_operational_load.py`: amplia a fila humana com handoffs incrementais, prioridades, operadores, historico e SLAs para testes operacionais.
- `seed_deep_population.py`: adiciona novos responsaveis, alunos, operadores internos, contratos, artefatos documentais, eventos e cenarios operacionais para uma base mais densa e mais realista.
- `seed_benchmark_scenarios.py`: adiciona casos dirigidos a benchmark, incluindo escopos parciais de responsavel, pagamento parcial, transferencia, visita institucional e cenarios de recuperacao.
- `sync_auth_bindings.py`: sincroniza identidades federadas mockadas no banco para os usuarios semeados.

Execucao recomendada:

1. `make db-upgrade`
2. `make db-seed-foundation`
3. `make db-seed-school-expansion`
4. `make db-seed-operational-load`
5. `make db-seed-deep-population`
6. `make db-seed-benchmark-scenarios`
7. `make db-seed-auth-bindings`
