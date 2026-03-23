# Article Export

Tooling simples para exportar o artigo academico do projeto para `.docx`.

Arquivos de entrada:

- `docs/article/eduassist-platform-academic-article.md`
- `docs/article/article-export-metadata.yaml`

Saida padrao:

- `artifacts/article/eduassist-platform-academic-article.docx`

Comando principal:

- `make article-docx`

Observacoes:

- o exportador cobre headings, paragrafos e listas;
- a capa usa os metadados versionados no repositório;
- caso necessario, os campos de autor, instituicao e orientacao podem ser ajustados no arquivo YAML antes de gerar o `.docx`.
