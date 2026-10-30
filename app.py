"""Triagem de Currículos com IA: descrição da vaga + currículos -> ranking justificado."""

import base64
import csv
import io
from typing import Literal

import streamlit as st
from pydantic import BaseModel, Field

from ia import ErroIA, extrair


class Requisito(BaseModel):
    requisito: str
    atende: Literal["sim", "parcial", "não"]
    evidencia: str = Field(description="Trecho ou fato do currículo que sustenta a avaliação, ou 'Não mencionado'")


class Avaliacao(BaseModel):
    nome: str
    nota: int = Field(description="Aderência à vaga de 0 a 100")
    resumo: str = Field(description="2 frases sobre o perfil do candidato")
    requisitos: list[Requisito]
    pontos_fortes: list[str]
    lacunas: list[str]
    recomendacao: Literal["entrevistar", "talvez", "não avançar"]
    perguntas_entrevista: list[str] = Field(description="3 perguntas para investigar as lacunas")


INSTRUCOES = """Você ajuda um recrutador a fazer a primeira triagem de currículos.
Compare o currículo com os requisitos da vaga, um por um, citando a evidência do
currículo. Avalie só competências e experiência: ignore idade, gênero, estado civil,
foto, endereço e qualquer outro dado pessoal que não tenha relação com o trabalho.
Não presuma competências que o currículo não mostra. A decisão final é do recrutador."""

TIPOS = {"pdf": "application/pdf", "txt": "text/plain", "md": "text/plain"}


def bloco_do_curriculo(nome: str, dados: bytes) -> dict:
    tipo = TIPOS[nome.rsplit(".", 1)[-1].lower()]
    if tipo == "application/pdf":
        fonte = {"type": "base64", "media_type": tipo, "data": base64.standard_b64encode(dados).decode()}
    else:
        fonte = {"type": "text", "media_type": "text/plain", "data": dados.decode("utf-8", errors="ignore")}
    return {"type": "document", "source": fonte, "title": nome}


def avaliar(vaga: str, nome: str, dados: bytes) -> Avaliacao:
    conteudo = [
        bloco_do_curriculo(nome, dados),
        {"type": "text", "text": f"<vaga>\n{vaga}\n</vaga>\n\nAvalie o currículo acima para esta vaga."},
    ]
    return extrair(conteudo, Avaliacao, INSTRUCOES)


def ranking_em_csv(avaliacoes: list[Avaliacao]) -> str:
    saida = io.StringIO()
    escritor = csv.writer(saida)
    escritor.writerow(["nome", "nota", "recomendacao", "pontos_fortes", "lacunas"])
    for a in avaliacoes:
        escritor.writerow([a.nome, a.nota, a.recomendacao, " | ".join(a.pontos_fortes), " | ".join(a.lacunas)])
    return saida.getvalue()


ICONE = {"entrevistar": "🟢", "talvez": "🟡", "não avançar": "🔴"}
MARCA = {"sim": "✅", "parcial": "➖", "não": "❌"}

st.set_page_config(page_title="Triagem de Currículos com IA", page_icon="🧑‍💼", layout="wide")
st.title("🧑‍💼 Triagem de Currículos com IA")
st.caption("Cole a vaga, envie os currículos e receba um ranking com a justificativa de cada nota. A decisão continua sendo sua.")

esquerda, direita = st.columns(2)
vaga = esquerda.text_area("Descrição da vaga", height=300, placeholder="Cargo, requisitos obrigatórios, diferenciais…")
curriculos = direita.file_uploader("Currículos (PDF ou TXT)", type=list(TIPOS), accept_multiple_files=True)

if st.button("Avaliar candidatos", type="primary", disabled=not (vaga.strip() and curriculos)):
    avaliacoes: list[Avaliacao] = []
    progresso = st.progress(0.0)
    for i, arq in enumerate(curriculos, start=1):
        try:
            avaliacoes.append(avaliar(vaga, arq.name, arq.getvalue()))
        except ErroIA as e:
            st.warning(f"{arq.name}: {e}")
        progresso.progress(i / len(curriculos), text=f"{i} de {len(curriculos)}")
    st.session_state["avaliacoes"] = sorted(avaliacoes, key=lambda a: a.nota, reverse=True)

avaliacoes: list[Avaliacao] = st.session_state.get("avaliacoes", [])
if avaliacoes:
    st.markdown("### Ranking")
    st.dataframe(
        [{"#": i, "candidato": a.nome, "nota": a.nota, "recomendação": f"{ICONE[a.recomendacao]} {a.recomendacao}"}
         for i, a in enumerate(avaliacoes, start=1)],
        use_container_width=True, hide_index=True,
        column_config={"nota": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d")},
    )

    for a in avaliacoes:
        with st.expander(f"{ICONE[a.recomendacao]} {a.nome} · {a.nota}/100"):
            st.write(a.resumo)
            st.markdown("**Requisitos**")
            for r in a.requisitos:
                st.markdown(f"{MARCA[r.atende]} **{r.requisito}**: {r.evidencia}")
            c1, c2 = st.columns(2)
            c1.markdown("**Pontos fortes**\n" + "\n".join(f"- {p}" for p in a.pontos_fortes))
            c2.markdown("**Lacunas**\n" + "\n".join(f"- {l}" for l in a.lacunas))
            st.markdown("**Perguntas para a entrevista**\n" + "\n".join(f"1. {q}" for q in a.perguntas_entrevista))

    st.download_button("Baixar ranking (.csv)", ranking_em_csv(avaliacoes), "ranking.csv", "text/csv")
