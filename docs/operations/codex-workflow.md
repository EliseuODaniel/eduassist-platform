# Workflow de Codex, MCP, Skills e AGENTS.md

## 1. Objetivo

Definir como `Codex` e os recursos associados serão usados no desenvolvimento deste projeto de forma alinhada às práticas mais atuais da documentação oficial.

## 2. O que entra neste projeto

- `AGENTS.md` na raiz do repositório
- `.codex/config.toml` com `MCP` de documentação oficial
- `.vscode/mcp.json` para integração no VS Code
- agentes customizados em `.codex/agents/`
- skill de sincronização arquitetural em `.agents/skills/`

## 3. Papel de cada recurso

### `AGENTS.md`

- fonte principal de instruções específicas do repositório;
- define convenções locais;
- força uso do MCP oficial da OpenAI quando o assunto for OpenAI/Codex.

### `MCP`

- usado para buscar e ler documentação oficial da OpenAI;
- reduz drift e especulação em decisões sobre `Responses API`, `Codex`, `MCP`, `skills`, `AGENTS.md` e subagents.

### `Skills`

- encapsulam workflows repetíveis;
- ajudam a manter consistência documental;
- devem ser estreitas, claras e acionáveis.

### `Custom agents`

- usados para tarefas estreitas e opinadas;
- devem ser `read-only` por padrão quando seu papel for pesquisa ou revisão;
- neste projeto, a primeira leva cobre pesquisa documental e revisão de segurança.

## 4. Diretriz de melhores práticas

### Para OpenAI/Codex

- usar documentação oficial como fonte primária;
- preferir `Responses API` em fluxos agentic/tool-using quando OpenAI for o provedor escolhido;
- registrar no repositório quando uma decisão for específica de provedor.

### Para subagents

- usar apenas quando a tarefa for naturalmente paralelizável ou exigir revisão independente;
- manter escopo estreito;
- evitar profundidade excessiva;
- manter `max_depth = 1` e `max_threads = 4` neste projeto.

### Para skills

- skill deve ter propósito claro;
- skill deve sincronizar documentos, não espalhar instruções conflitantes;
- skill não substitui documentação de arquitetura.

## 5. Arquivos do projeto

- [AGENTS.md](/home/edann/projects/eduassist-platform/AGENTS.md)
- [.codex/config.toml](/home/edann/projects/eduassist-platform/.codex/config.toml)
- [.vscode/mcp.json](/home/edann/projects/eduassist-platform/.vscode/mcp.json)
- [.codex/agents/docs-researcher.toml](/home/edann/projects/eduassist-platform/.codex/agents/docs-researcher.toml)
- [.codex/agents/security-reviewer.toml](/home/edann/projects/eduassist-platform/.codex/agents/security-reviewer.toml)
- [eduassist-architecture-sync skill](/home/edann/projects/eduassist-platform/.agents/skills/eduassist-architecture-sync/SKILL.md)

## 6. Recomendação de uso neste projeto

- usar `docs_researcher` para decisões sobre OpenAI, Codex, MCP e APIs;
- usar `security_reviewer` para revisão de risco, autorização e auditoria;
- usar a skill `eduassist-architecture-sync` sempre que houver alteração transversal no plano.

## 7. Benefício esperado

Essa camada não muda o runtime do produto, mas melhora muito o processo de engenharia:

- menos deriva documental;
- menos arquitetura acidental;
- mais consistência nas decisões de IA;
- melhor uso das capacidades do Codex;
- maior aderência às práticas oficiais mais atuais.

