# Packages

Diretório reservado para bibliotecas compartilhadas:

- contratos de API
- utilitários
- observabilidade
- clients internos
- schemas compartilhados
- camadas de entrada e guardrails compartilhados

Pacotes de maior impacto hoje:

- `observability/python`: tracing, métricas e integração OTEL;
- `semantic-ingress/python`: classificação semântica compartilhada de atos de entrada como `greeting`, `auth_guidance`, `language_preference`, `input_clarification` e `scope_boundary`.

Esse desenho permite compartilhar:

- contrato semântico de entrada;
- observabilidade;
- invariantes de segurança e abstention;

sem apagar a diferenciação arquitetural entre `langgraph`, `python_functions`, `llamaindex` e `specialist_supervisor`.
