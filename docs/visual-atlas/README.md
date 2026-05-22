# EduAssist Visual Atlas

Documentação visual curada do EduAssist Platform, criada no próprio repositório a partir do código e dos documentos canônicos.

## Rodar localmente

```bash
cd docs/visual-atlas
npm install
npm run dev
```

Abra `http://127.0.0.1:5174`.

## O que documenta

- Fluxo real de atendimento Telegram.
- Fronteira entre dados protegidos determinísticos e RAG documental.
- Papel dos quatro runtimes dedicados.
- Serviços, recursos, endpoints e arquivos-fonte relevantes.
- Gates de release, scorecard e observabilidade.
- Navegação por profundidade: visão macro, microfluxos por componente e links para arquivos.
- Modos de leitura: explicação, how-to, referência e tutorial.
- Links compartilháveis por hash para preservar trilha, microfluxo, nó selecionado e busca.

O conteúdo foi montado a partir dos documentos canônicos em `docs/` e de arquivos reais em `apps/`, `packages/` e `tools/`.

## Critérios de design

- C4: o atlas separa leitura de sistema, componente e proximidade com código.
- Diátaxis: a lateral ajuda a escolher a documentação pela intenção de leitura.
- arc42: o inspetor explicita evidências, guardrails e pontos de atenção por nó.
