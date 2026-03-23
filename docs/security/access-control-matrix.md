# Matriz de Controle de Acesso

## 1. Objetivo

Definir o modelo inicial de acesso por papel, recurso e ação.

## 2. Convenções

- `Ler`: consultar dados
- `Operar`: executar ação operacional
- `Amplo`: visão ampliada do domínio
- `Negado`: acesso explicitamente proibido
- toda permissão depende também de policy contextual e vínculo quando aplicável

## 3. Matriz resumida

| Papel | FAQ pública | Calendário público | Dados próprios | Dados de dependente | Dados de turma | Financeiro | Operação interna | Auditoria |
|---|---|---|---|---|---|---|---|---|
| Anônimo | Ler | Ler | Negado | Negado | Negado | Negado | Negado | Negado |
| Aluno | Ler | Ler | Ler | Negado | Negado | Limitado | Negado | Negado |
| Responsável | Ler | Ler | Negado | Ler | Negado | Ler do dependente | Negado | Negado |
| Professor | Ler | Ler | Ler limitado | Negado | Ler | Negado | Limitado | Negado |
| Secretaria | Ler | Ler | Limitado | Limitado | Limitado | Limitado | Operar | Negado |
| Financeiro | Ler | Ler | Limitado | Limitado | Negado | Amplo | Operar | Negado |
| Coordenação | Ler | Ler | Limitado | Limitado | Amplo | Limitado | Operar | Limitado |
| Direção | Ler | Ler | Limitado | Limitado | Amplo | Amplo | Operar | Limitado |
| Operador do sistema | Ler | Ler | Negado | Negado | Negado | Negado | Operar sistema | Limitado técnico |
| Admin técnico | Ler | Ler | Negado por padrão | Negado por padrão | Negado por padrão | Negado por padrão | Operar plataforma | Auditoria técnica |

## 4. Regras por domínio

### FAQ institucional

- disponível para todos;
- documentos privados não entram neste fluxo.

### Acadêmico

- aluno vê apenas seus próprios dados;
- responsável vê apenas dados dos alunos vinculados;
- professor vê dados das turmas atribuídas;
- coordenação e direção têm acesso ampliado, sempre auditado.

### Financeiro

- responsável vê apenas contratos e cobranças vinculados;
- aluno pode ter visão limitada, conforme policy;
- setor financeiro tem acesso amplo ao domínio;
- coordenação só acessa o mínimo necessário.

### Secretaria

- acesso operacional por papel;
- consultas mais sensíveis exigem motivo de acesso e trilha auditável.

## 5. Regras específicas de Telegram

- dados sensíveis não devem ser despejados integralmente no chat por padrão;
- alguns fluxos devem retornar resumo curto e link seguro para portal;
- autenticação prévia é obrigatória para consultas protegidas.

## 6. Regras de negação explícita

O sistema deve negar e registrar:

- tentativa de responsável acessar aluno não vinculado;
- tentativa de aluno acessar colega;
- tentativa de professor acessar financeiro individual sem permissão;
- tentativa de operador técnico usar bot como atalho para dados acadêmicos;
- tentativa de prompt injection para exfiltrar conteúdo privado.

## 7. Enforcement técnico

- `Keycloak`: identidade e papel
- `OPA`: decisão contextual
- `PostgreSQL RLS`: barreira final no banco
- services internos: contratos mínimos
- auditoria: acesso sensível e decisão de policy

