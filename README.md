# 🧑‍💼 Triagem de Currículos com IA

Recebe a **descrição de uma vaga** e um lote de **currículos em PDF ou TXT** e devolve um **ranking justificado**: nota de 0 a 100, **requisito por requisito com a evidência tirada do currículo**, pontos fortes, lacunas, recomendação (entrevistar / talvez / não avançar) e perguntas sugeridas para a entrevista.

## O problema

Uma vaga aberta recebe dezenas ou centenas de currículos. A primeira leitura, só para separar quem atende os requisitos mínimos, consome horas do recrutador.

## Como a IA resolve

- Um modelo **local** do Ollama (`llama3.1:8b` por padrão) recebe o texto do currículo (PDF lido com `pypdf`) e compara com a vaga **requisito por requisito**, citando a evidência. A nota fica explicável, não é uma caixa-preta.
- Saída **validada por esquema Pydantic** (o Ollama gera direto no formato do esquema), então o ranking é sempre consistente.
- O prompt manda **ignorar dados pessoais** sem relação com o trabalho (idade, gênero, foto, endereço) e não presumir competências que o currículo não mostra.
- Currículo tem dado pessoal: rodando local, **nada sai da máquina** (ajuda com a LGPD).
- A ferramenta **apoia** a decisão: o recrutador vê a justificativa e decide.

## Rodando

Precisa do [Ollama](https://ollama.com) instalado e aberto.

```bash
ollama pull llama3.1:8b
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Roda **100% local**: nenhum dado sai da sua máquina e não precisa de chave de API. Para usar outro modelo: `OLLAMA_MODEL=qwen2.5:7b streamlit run app.py`.

Para testar, use a vaga e os currículos fictícios da pasta [`exemplos/`](exemplos/).

## Estrutura

| Arquivo | O que faz |
|---|---|
| `app.py` | Interface Streamlit, esquema `Avaliacao`/`Requisito`, ranking e exportação |
| `ia.py` | Chamada ao Ollama com saída estruturada e tratamento de erros |

## Stack

Python · Streamlit · Ollama (Llama 3.1, local, structured outputs) · pypdf · Pydantic

## Próximos passos

- Processar o lote em paralelo para reduzir o tempo total
- Anonimizar o currículo antes da avaliação (remover nome e contatos)
