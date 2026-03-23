# Modelo de Dados e Estratégia de Dados Mockados

## 1. Objetivo

Definir a modelagem inicial de dados do sistema e a estratégia para geração de bases mockadas consistentes.

## 2. Abordagem

O sistema usará:

- dados estruturados em `PostgreSQL`;
- documentos em `MinIO`;
- índices vetoriais e textuais associados ao catálogo documental;
- dados 100% mockados, mas coerentes entre si.

## 3. Schemas planejados

### `identity`

- `users`
- `roles`
- `telegram_accounts`
- `user_telegram_links`
- `consents`
- `sessions`

### `school`

- `students`
- `guardians`
- `guardian_student_links`
- `teachers`
- `staff`
- `school_units`
- `classes`
- `subjects`
- `enrollments`

### `academic`

- `grade_items`
- `grades`
- `attendance_records`
- `student_reports`
- `incidents`
- `teacher_assignments`

### `finance`

- `contracts`
- `invoices`
- `invoice_items`
- `payments`
- `scholarships`
- `discounts`
- `payment_negotiations`

### `calendar`

- `calendar_events`
- `exam_schedule`
- `meetings`
- `holidays`
- `school_announcements`

### `documents`

- `document_sets`
- `documents`
- `document_versions`
- `document_chunks`
- `document_embeddings`
- `retrieval_labels`

### `conversation`

- `conversations`
- `messages`
- `conversation_summaries`
- `tool_calls`
- `feedback`
- `handoffs`

### `audit`

- `audit_events`
- `access_decisions`
- `sensitive_queries`
- `admin_actions`
- `policy_evaluations`

## 4. Relações de negócio importantes

- um responsável pode estar vinculado a múltiplos alunos;
- um aluno pode ter múltiplos responsáveis;
- um professor pode lecionar em múltiplas turmas;
- contratos financeiros pertencem a aluno e responsável;
- avaliações e frequência pertencem ao aluno dentro de uma matrícula;
- documentos possuem visibilidade, vigência e categoria.

## 5. Estratégia de mock data

O gerador de dados deve produzir um ecossistema escolar crível:

- 1 escola de ensino médio;
- 3 séries;
- 20-40 turmas;
- 600-1500 alunos;
- 1000+ cobranças;
- 5000+ registros acadêmicos;
- eventos de calendário completos;
- professores, funcionários e organograma coerentes.

## 6. Regras de consistência

- todo aluno matriculado pertence a turma válida;
- toda nota pertence a item avaliativo válido;
- toda cobrança pertence a contrato válido;
- todo vínculo de responsável deve ser consistente;
- calendário de provas deve refletir série, turma ou disciplina;
- documentos devem ter metadados de visibilidade.

## 7. Estratégia de geração

Ferramenta planejada:

- `tools/mockgen`

Características:

- seeds determinísticas;
- uso de `Faker`;
- geração por domínio;
- validação pós-carga;
- cenários normais e edge-cases.

## 8. Documentos e retrieval

Para cada documento:

- id
- título
- versão
- categoria
- visibilidade
- vigência
- público-alvo
- unidade escolar
- idioma
- origem do arquivo

Para cada chunk:

- referência ao documento
- ordem
- texto
- contexto resumido
- embedding
- labels de segurança

## 9. Estratégia de consulta

### Documental

- `FTS + vector search + reranking`

### Estruturada

- queries parametrizadas por services internos

### Híbrida

- combinação de fontes documentais e estruturadas com prioridade para source of truth estruturada quando aplicável

## 10. Regras para acesso de IA aos dados

- o modelo nunca recebe acesso direto ao banco;
- o modelo só enxerga resultados de tools;
- tools devolvem payload mínimo;
- dados sensíveis entram no contexto apenas quando já aprovados por policy.

