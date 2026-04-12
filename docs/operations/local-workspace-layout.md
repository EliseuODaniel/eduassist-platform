# Layout local do workspace

## Objetivo

Definir uma regra simples para o workspace local, evitando que o EduAssist fique espalhado em múltiplas pastas com papéis ambíguos.

## Regra principal

Use apenas **um** repositório ativo do EduAssist no workspace principal.

Hoje, o repositório ativo é:

- `eduassist-platform`

Tudo o que não for fonte ativa de verdade deve ficar fora da área principal de trabalho ou claramente marcado como histórico.

## Layout recomendado

```text
<workspace>/
├── eduassist-platform/              # único repo ativo do produto
└── _archive/
    └── eduassist/
        ├── studio-legacy/           # protótipo anterior
        └── notes/                   # materiais locais antigos, se necessário
```

## O que entra no repositório ativo

- código de produto;
- infraestrutura e operação;
- testes e evals;
- documentação formal do sistema;
- planos de experimento que ainda façam sentido para a arquitetura atual.

## O que não deve competir com o repo ativo

- worktrees antigos já mergeados;
- protótipos anteriores com arquitetura diferente;
- documentos salvos em outro repo “por conveniência”;
- artefatos locais e rascunhos fora do fluxo atual do produto.

## Worktrees

`git worktree` pode ser útil para trabalho temporário, mas não deve permanecer como uma segunda cópia oficial do projeto.

Boas práticas:

- criar worktree só para branches temporárias;
- remover a worktree após merge, abandono ou integração;
- nunca usar uma worktree antiga como referência principal de arquitetura depois que a `main` já incorporou a mudança.

## Protótipos e estudos

Se um protótipo antigo ainda precisar ser preservado:

- mova para `_archive/eduassist/`;
- mantenha o nome claro, como `studio-legacy`;
- não use esse diretório para trabalho ativo do produto.

## Documentação e experimentos

Planos de experimento ainda relevantes para o produto ativo devem viver neste repositório, em local explícito, por exemplo:

- `docs/experiments/`

Materiais puramente locais e acadêmicos continuam em:

- `tmp/`

## Sinalização rápida para quem chega no projeto

Qualquer pessoa nova no workspace deve conseguir responder rapidamente:

1. qual é o repositório ativo?
2. onde estão os arquivos históricos?
3. onde estão os experimentos futuros ainda válidos?

Se a resposta não estiver óbvia em menos de um minuto, o layout precisa ser simplificado.
