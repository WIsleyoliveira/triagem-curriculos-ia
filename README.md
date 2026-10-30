# 🧑‍💼 Triagem de Currículos com IA

Recebe a **descrição de uma vaga** e um lote de **currículos em PDF ou TXT** e devolve um **ranking justificado**: nota de 0 a 100, **requisito por requisito com a evidência tirada do currículo**, pontos fortes, lacunas, recomendação (entrevistar / talvez / não avançar) e perguntas sugeridas para a entrevista.

## O problema

Uma vaga aberta recebe dezenas ou centenas de currículos. A primeira leitura, só para separar quem atende os requisitos mínimos, consome horas do recrutador.

## Como a IA resolve

- O **Claude** lê o PDF direto (sem extrator de texto) e compara com a vaga **requisito por requisito**, citando a evidência. A nota fica explicável, não é uma caixa-preta.
- Saída **validada por esquema Pydantic** (structured outputs), então o ranking é sempre consistente.
- O prompt manda **ignorar dados pessoais** sem relação com o trabalho (idade, gênero, foto, endereço) e não presumir competências que o currículo não mostra.
- A ferramenta **apoia** a decisão: o recrutador vê a justificativa e decide.

## Rodando

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sua-chave"
streamlit run app.py
```

Para testar, use a vaga e os currículos fictícios da pasta [`exemplos/`](exemplos/).

## Estrutura

| Arquivo | O que faz |
|---|---|
| `app.py` | Interface Streamlit, esquema `Avaliacao`/`Requisito`, ranking e exportação |
| `ia.py` | Chamada ao Claude com saída estruturada e tratamento de erros |

## Stack

Python · Streamlit · Anthropic SDK (Claude, leitura de PDF, structured outputs) · Pydantic

## Próximos passos

- Processar lotes grandes com a Batch API (metade do custo)
- Anonimizar o currículo antes da avaliação (remover nome e contatos)
