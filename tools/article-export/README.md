# Article Export

Tooling simples para exportar o artigo academico local do projeto para `.docx`.

Arquivos de entrada:

- `tmp/tcc/article/eduassist-platform-academic-article.md`
- `tmp/tcc/article/article-export-metadata.yaml`

Saida padrao:

- `artifacts/article/eduassist-platform-academic-article.docx`

Comando principal:

- `make article-docx`

Observacoes:

- o exportador cobre headings, paragrafos e listas;
- a capa usa os metadados mantidos localmente em `tmp/tcc/article`;
- esse fluxo existe para uso local e nao implica publicacao dos textos academicos no repositorio remoto.
