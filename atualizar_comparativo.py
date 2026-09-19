"""
PiPA — Comparativo Pedagógico (1º x 2º Simulado)
Gera os blocos `const DATA1 = {...};` e `const DATA2 = {...};` do comparativo.html
a partir das duas planilhas de simulado.

Este script é independente do atualizar_dados.py (que cuida só do Painel 2 /
index.html) — rodar um nunca afeta o outro.

Uso:
    python3 atualizar_comparativo.py
    python3 atualizar_comparativo.py planilha_s1.xlsx planilha_s2.xlsx

Saída: comparativo_data.js, com as duas linhas `const DATA1 = ...;` e
`const DATA2 = ...;`. Copie-as por cima das linhas equivalentes dentro do
comparativo.html.

Fonte oficial de cada planilha: a aba "Reports" (1º Simulado) ou
"Reports ORIGINAL" (2º Simulado) — alternativa marcada, gabarito e pontuação
oficial. Nome e turma vêm de "Página1" (1º Simulado, roster limpo) ou da
própria "Reports ORIGINAL" (2º Simulado). A aba "Leticia" do 2º Simulado é
usada só para localizar onde cada disciplina começa e termina.
"""
import json
import sys
from pathlib import Path

import openpyxl

PADRAO_S1 = Path(__file__).parent / "dados" / "1_Simulado_EvaBee_Lucas.xlsx"
PADRAO_S2 = Path(__file__).parent / "dados" / "2_Simulado_2026.xlsx"

# Mesma estrutura de disciplinas nas duas provas (confirmado nas duas planilhas).
DISCIPLINAS = [
    {"nome": "ATUALIDADES", "ini": 1, "fim": 5},
    {"nome": "BIOLOGIA", "ini": 6, "fim": 10},
    {"nome": "INTERPRETAÇÃO DE TEXTO", "ini": 11, "fim": 21},
    {"nome": "HISTÓRIA", "ini": 22, "fim": 26},
    {"nome": "GEOGRAFIA", "ini": 27, "fim": 31},
    {"nome": "MATEMÁTICA", "ini": 32, "fim": 38},
    {"nome": "GRAMÁTICA", "ini": 39, "fim": 40},
    {"nome": "QUÍMICA", "ini": 41, "fim": 45},
    {"nome": "FÍSICA", "ini": 46, "fim": 50},
]


def indexar_questoes(ws):
    hdr = [c.value for c in ws[1]]
    idx: dict[int, dict[str, int]] = {}
    for i, h in enumerate(hdr):
        if h and str(h).startswith("Q "):
            p = str(h).split()
            idx.setdefault(int(p[1]), {})[p[2]] = i
    return idx


def extrair(caminho: Path, aba_reports: str, titulo: str, aba_roster: str | None) -> dict:
    wb = openpyxl.load_workbook(caminho, data_only=True)
    ws = wb[aba_reports]
    idx = indexar_questoes(ws)
    nq = max(idx)
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[2]]

    gab = "".join(
        sorted({str(r[idx[q]["Key"]]).strip() for r in rows if r[idx[q]["Key"]]})[0]
        for q in range(1, nq + 1)
    )

    roster = None
    if aba_roster:
        roster = {
            int(r[0]): (str(r[1]).strip(), str(r[2]).strip())
            for r in wb[aba_roster].iter_rows(min_row=2, values_only=True) if r[0]
        }

    anomalias = []
    alunos = []
    for r in rows:
        matricula = int(str(r[2]).strip())
        if roster is not None:
            if matricula not in roster:
                raise SystemExit(f"[{titulo}] matrícula {matricula} sem correspondência no roster.")
            nome, turma = roster[matricula]
        else:
            nome, turma = str(r[3]).strip(), str(r[4]).strip()

        ans = ""
        for q in range(1, nq + 1):
            v = r[idx[q]["Options"]]
            s = "" if v is None else str(v).strip()
            if s == "":
                ans += "-"
            elif len(s) == 1:
                ans += s
            else:
                ans += "*"
                anomalias.append(f"{nome} — Q{q}: marcou {''.join(c for c in s if c.isalpha())}, gabarito {gab[q-1]}")

        corr = "".join(str(int(float(r[idx[q]["Marks"]]))) for q in range(1, nq + 1))
        declarado_idx = 7 if roster is not None else 5
        declarado = int(float(r[declarado_idx]))
        if corr.count("1") != declarado:
            raise SystemExit(f"[{titulo}] inconsistência em {nome}: soma Marks {corr.count('1')} != declarado {declarado}.")

        alunos.append({"id": matricula, "n": nome, "t": turma, "a": ans, "c": corr})

    alunos.sort(key=lambda s: (-s["c"].count("1"), s["n"]))
    if anomalias:
        print(f"[{titulo}] {len(anomalias)} questão(ões) com dupla marcação (pontuadas como zero):")
        for a in anomalias:
            print("  -", a)
    return {"titulo": titulo, "totalQuestoes": nq, "gabarito": gab, "disciplinas": DISCIPLINAS, "alunos": alunos}


def main(caminho_s1: Path, caminho_s2: Path) -> None:
    d1 = extrair(caminho_s1, "Reports", "1º Simulado 2026", aba_roster="Página1")
    d2 = extrair(caminho_s2, "Reports ORIGINAL", "2º Simulado 2026", aba_roster=None)

    ids1, ids2 = {a["id"] for a in d1["alunos"]}, {a["id"] for a in d2["alunos"]}
    comuns = ids1 & ids2
    saida = Path(__file__).parent / "comparativo_data.js"
    saida.write_text(
        "const DATA1 = " + json.dumps(d1, ensure_ascii=False, separators=(",", ":")) + ";\n"
        "const DATA2 = " + json.dumps(d2, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8",
    )
    print(f"\n1º Simulado: {len(d1['alunos'])} alunos · 2º Simulado: {len(d2['alunos'])} alunos")
    print(f"Comuns aos dois (por matrícula): {len(comuns)} · só no 1º: {len(ids1-ids2)} · só no 2º: {len(ids2-ids1)}")
    print(f"Gravado em {saida}")
    print("Copie as duas linhas desse arquivo por cima das linhas 'const DATA1 =' e 'const DATA2 ='")
    print("dentro de comparativo.html.")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        s1, s2 = Path(sys.argv[1]), Path(sys.argv[2])
    elif len(sys.argv) == 1:
        s1, s2 = PADRAO_S1, PADRAO_S2
    else:
        raise SystemExit("Uso: python3 atualizar_comparativo.py [planilha_s1.xlsx planilha_s2.xlsx]")
    for p in (s1, s2):
        if not p.exists():
            raise SystemExit(f"Planilha não encontrada: {p}")
    main(s1, s2)
