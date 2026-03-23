# Plano de Refatoração do Documento Acadêmico

## 1. Ponto de partida

O arquivo anterior, [8 resultados preliminares.docx](/home/edann/projects/studio/8%20resultados%20preliminares.docx), descreve um protótipo preliminar de chatbot escolar. Ele é útil como histórico do problema e do domínio, mas não representa mais a arquitetura ou a ambição do novo sistema.

## 2. Mudança de tese

### Tese antiga

Validar um protótipo funcional multiagente para atendimento escolar.

### Nova tese

Projetar e implementar uma plataforma robusta, segura, auditável e local-first de atendimento escolar com IA, baseada em dados mockados sobre infraestrutura real e acesso governado a informações institucionais, acadêmicas e financeiras.

## 3. O que deve ser removido ou reescrito

- centralidade em Genkit como decisão final;
- foco excessivo em três agentes como arquitetura definitiva;
- linguagem de “protótipo já validado” quando o novo sistema ainda será construído;
- afirmações frágeis sobre segurança do Telegram;
- descrição do painel e fluxos antigos como se fossem produto final.

## 4. O que deve entrar no novo documento

- requisitos do domínio escolar;
- matriz de papéis e acesso;
- arquitetura em camadas;
- identidade, autenticação e autorização;
- modelo de dados mockados;
- retrieval híbrido e grounding;
- observabilidade e auditoria;
- LGPD e segurança da informação;
- plano experimental e evals;
- roadmap de implementação.

## 5. Estrutura sugerida

1. Título
2. Resumo
3. Introdução
4. Problema e motivação
5. Requisitos do domínio escolar
6. Arquitetura proposta
7. Estratégia de IA
8. Segurança da informação e controle de acesso
9. Modelagem de dados mockados
10. Infraestrutura local e operação
11. Plano experimental e avaliação
12. Roadmap de implementação
13. Limitações
14. Considerações finais
15. Referências

## 6. Figuras recomendadas

- diagrama geral da arquitetura
- fluxo de autenticação e vínculo Telegram
- fluxo de FAQ pública
- fluxo de consulta protegida
- diagrama lógico do modelo de dados
- pipeline de ingestão e retrieval

## 7. Tom acadêmico recomendado

- menos “demonstração do protótipo”;
- mais “proposta arquitetural e plano de execução”;
- explicitar limites, ameaças e critérios de avaliação;
- separar claramente o que já existe do que será implementado.

## 8. Resultado desejado

Um novo documento consistente com o estado atual do projeto e capaz de servir como:

- base de artigo;
- base de qualificação técnica;
- documentação de arquitetura;
- referência para implementação.

## 9. Estado atual da refatoração

O outline acima ja foi materializado em um rascunho academico completo em [eduassist-platform-academic-draft.md](/home/edann/projects/eduassist-platform/docs/article/eduassist-platform-academic-draft.md).

Esse rascunho:

- substitui a tese antiga centrada em prototipo multiagente;
- descreve a arquitetura real do repositório atual;
- explicita o que ja foi implementado e o que ainda esta pendente;
- pode servir como base imediata para conversao posterior em `.docx` ou artigo formal.
