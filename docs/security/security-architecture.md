# Segurança da Informação e Arquitetura de Acesso

## 1. Objetivo

Estabelecer os controles de segurança, identidade, autorização, auditoria e privacidade do sistema.

## 2. Premissas

- O sistema opera com dados mockados, mas deve ser construído como se os dados fossem reais.
- O canal Telegram não deve ser tratado como fronteira suficiente de segurança.
- O modelo deve operar sob princípio do menor privilégio.

## 3. Classificação de dados

### Pública

- endereço
- contatos
- calendário público
- FAQ institucional
- processos gerais de matrícula

### Interna

- documentos operacionais internos
- escalas
- comunicados administrativos restritos

### Sensível pessoal

- notas
- frequência
- ocorrências
- histórico acadêmico
- contratos
- boletos
- status financeiro
- vínculos familiares

## 4. Identidade

### Provedor

- `Keycloak`

### Fluxo

- usuário pode iniciar conversa pública no Telegram;
- ao solicitar dado protegido, recebe fluxo de vinculação;
- vínculo ocorre via portal web autenticado;
- conta Telegram é associada ao usuário escolar por processo controlado.

## 5. Autorização

Camadas:

- `Keycloak` para papéis e identidade;
- `OPA` para decisão contextual;
- `PostgreSQL RLS` para enforcement adicional sobre dados.
- papel de aplicação dedicado no banco, sem `SUPERUSER`, distinto do papel administrativo usado para bootstrap, migração e seed.

Regra geral:

- `default deny`

Exemplos:

- responsável vê apenas alunos vinculados;
- aluno vê apenas seus próprios dados;
- professor vê apenas turmas atribuídas;
- financeiro acessa domínio financeiro, não acadêmico amplo;
- tabelas auxiliares como `classes`, `guardian_student_links`, `teacher_assignments`, `grade_items` e `calendar_events` também seguem escopo mínimo por papel;
- conversas, mensagens, `tool_calls` e handoffs seguem a mesma lógica de escopo próprio vs visão global interna;
- notas internas de operador não devem aparecer no detalhe de handoff para o solicitante final;
- direção tem acesso ampliado com auditoria reforçada.

## 6. Telegram

### Regras

- validar `secret_token` do webhook;
- registrar idempotência por update;
- limitar taxa por chat e por IP de entrada;
- não tratar o Telegram como meio apropriado para despejar dados altamente sensíveis.

### Observação de segurança

Inferência a partir da documentação oficial do Telegram: a criptografia ponta a ponta é documentada para `Secret Chats`. Como bots operam pela `Bot API` e webhooks, o sistema não deve alegar E2E nas conversas com o bot.

## 7. Logs e auditoria

### Princípios

- logs estruturados;
- mascaramento de PII;
- correlation id por conversa;
- trilha de acessos sensíveis;
- retenção por classe de evento.

### Ferramentas

- `pgAudit`
- trilhas de aplicação em `audit_events`
- observabilidade com `OTel`, `Loki` e `Tempo`

## 8. Ameaças principais

- prompt injection em documentos;
- exfiltração de dados por perguntas maliciosas;
- autorização quebrada;
- vazamento por logs;
- erro na classificação de documentos;
- excesso de dados sensíveis no contexto da LLM;
- execução de tools além do necessário.

## 9. Mitigações

- filtro de visibilidade antes do retrieval;
- contracts rígidos para tools;
- contexto mínimo para o modelo;
- negação explícita por policy;
- avaliação adversarial contínua;
- revisão de curadoria documental;
- observabilidade de acessos críticos;
- segregação de segredos.

## 10. Segredos e credenciais

- usar variáveis de ambiente apenas em dev;
- preferir `Docker secrets` quando possível;
- rotação documentada de segredos;
- não registrar tokens em logs;
- chaves de API de LLM isoladas por ambiente.

## 11. LGPD orientativa

Mesmo com dados mockados, a arquitetura deve nascer compatível com:

- minimização;
- finalidade;
- rastreabilidade de acesso;
- segregação de perfis;
- retenção;
- revisão de acesso;
- base legal e consentimento quando aplicável.

## 12. Critérios mínimos de segurança para o MVP

- autenticação funcional;
- policy engine ativo;
- RLS habilitado em tabelas sensíveis;
- RLS também habilitado nas tabelas auxiliares que sustentam respostas acadêmicas, docentes e calendárias restritas;
- runtime do `api-core`, `ai-orchestrator` e `worker` executando com usuário de aplicação não-superuser;
- webhook protegido;
- auditoria de acessos sensíveis;
- logs sem PII crua;
- testes de negação indevida e acesso indevido.
