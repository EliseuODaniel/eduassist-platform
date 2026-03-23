# PRD - Plataforma de Atendimento Escolar com IA

## 1. Resumo executivo

Este documento define os requisitos do produto `EduAssist Platform`, uma plataforma de atendimento escolar via Telegram com dados institucionais mockados sobre infraestrutura real. O sistema deve atender usuários internos e externos de uma escola fictícia de ensino médio, responder perguntas institucionais, consultar dados acadêmicos e financeiros autorizados e operar sob políticas fortes de segurança da informação.

## 2. Problema

Instituições escolares concentram grande volume de dúvidas recorrentes, solicitações operacionais e consultas a dados pessoais. Em geral, o atendimento é fragmentado, manual e dependente de múltiplos setores. O projeto busca simular uma solução robusta para esse problema, preservando realismo técnico e segurança, ainda que os dados de conteúdo sejam totalmente mockados.

## 3. Objetivos do produto

- Oferecer atendimento conversacional 24x7 via Telegram.
- Responder perguntas sobre a instituição com grounding e citações.
- Consultar dados escolares mockados de modo seguro e auditável.
- Suportar perfis diversos com regras distintas de acesso.
- Criar base operacional para testes, pesquisa aplicada e futura evolução.

## 4. Não objetivos

- Não construir inicialmente um ERP escolar completo.
- Não integrar com bases reais de produção.
- Não usar o Telegram como mecanismo único de confiança para dados sensíveis.
- Não permitir ao modelo acesso irrestrito a banco ou execução livre de consultas.

## 5. Personas

### 5.1 Responsável

Quer acompanhar notas, frequência, eventos, financeiro e comunicados de seu filho.

### 5.2 Aluno

Quer consultar notas, faltas, horários, provas e calendários.

### 5.3 Professor

Quer ver turmas, horários, calendário acadêmico e informações operacionais permitidas.

### 5.4 Secretaria

Quer apoiar atendimento, verificar status e encaminhar solicitações.

### 5.5 Financeiro

Quer verificar contratos, cobranças, bolsas e pendências.

### 5.6 Coordenação e Direção

Quer visibilidade ampliada, com forte trilha de auditoria.

### 5.7 Operador do sistema

Quer monitorar qualidade, incidentes, handoffs e bases documentais.

## 6. Casos de uso principais

- FAQ institucional pública
- Consulta de calendário escolar
- Consulta de notas e frequência
- Consulta de situação financeira
- Consulta de horários de aula
- Consulta de comunicados e regulamentos
- Solicitação de segunda via ou documento
- Abertura de ticket
- Encaminhamento para atendimento humano

## 7. Requisitos funcionais

### 7.1 Canal

- O sistema deve receber mensagens do Telegram via webhook.
- O sistema deve responder no mesmo canal.
- O sistema deve suportar mensagens de texto como canal prioritário do MVP.

### 7.2 Identidade

- O sistema deve permitir atendimento público sem autenticação apenas para informações não sensíveis.
- O sistema deve exigir vinculação de identidade para acesso a dados pessoais.
- O sistema deve suportar fluxo de vínculo entre conta Telegram e perfil escolar.

### 7.3 Autorização

- O sistema deve restringir acesso por papel, vínculo e escopo.
- O sistema deve registrar toda decisão de acesso sensível.
- O sistema deve negar explicitamente consultas sem autorização.

### 7.4 Conteúdo documental

- O sistema deve responder com base em documentos institucionais indexados.
- O sistema deve citar fontes relevantes quando a resposta vier de base documental.
- O sistema deve diferenciar conteúdo público e privado.

### 7.5 Dados estruturados

- O sistema deve consultar dados acadêmicos mockados.
- O sistema deve consultar dados financeiros mockados.
- O sistema deve consultar calendário e comunicados estruturados.
- O sistema deve usar serviços internos determinísticos para esse acesso.

### 7.6 Operação

- O sistema deve permitir handoff para humano.
- O sistema deve registrar feedback do usuário.
- O sistema deve expor painel administrativo para monitoramento e curadoria.

## 8. Requisitos não funcionais

- Segurança por padrão
- Auditoria de acessos sensíveis
- Observabilidade ponta a ponta
- Execução local em máquina pessoal
- Reprodutibilidade por containers
- Arquitetura modular
- Portabilidade futura para Kubernetes

## 9. Restrições

- Todos os dados devem ser mockados.
- A infraestrutura deve ser real.
- O sistema deve ser executável localmente.
- A LLM pode ser consumida por API remota paga.
- O canal principal é Telegram.

## 10. Métricas de sucesso

- taxa de resposta correta para FAQ pública
- taxa de groundedness com citações válidas
- taxa de negação correta por política
- taxa de handoff nos casos de baixa confiança
- latência média por tipo de fluxo
- custo médio por conversa
- satisfação por feedback explícito

## 11. Critérios de aceitação do MVP

- responder FAQ pública com fontes citadas;
- responder calendário escolar com fontes ou dados estruturados;
- autenticar e vincular um responsável a um aluno mockado;
- permitir consulta autorizada de notas e financeiro desse aluno;
- negar corretamente consulta a dados de terceiro;
- registrar trilha de auditoria;
- operar via Compose local com documentação reproduzível.

## 12. Riscos

- erro de policy levando a vazamento;
- classificação documental incorreta;
- excesso de contexto sensível enviado à LLM;
- baixa qualidade do vínculo de identidade;
- problemas de latência/custo com LLM remota.

## 13. Estratégia de MVP

Priorizar:

1. FAQ institucional pública
2. calendário escolar
3. vínculo de identidade
4. consulta acadêmica protegida
5. consulta financeira protegida
6. handoff e painel básico

