# Fluxo Detalhado do CrewAI

## 1. Adapter no runtime principal

![diagram](./mermaid-assets/crewai/dual-stack-crewai-visual-flow-1.svg)

## 2. Slice public

![diagram](./mermaid-assets/crewai/dual-stack-crewai-visual-flow-2.svg)

## 3. Slice protected

![diagram](./mermaid-assets/crewai/dual-stack-crewai-visual-flow-3.svg)

Notas:

- o `CrewAI` roda em servico isolado
- `Flow` e persistido por slice
- quando o piloto nao consegue devolver `answer_text`, o adapter pode cair em fallback explicito
