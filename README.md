# PiPA — Painel Pedagógico e Comparativo de Simulados

Dois painéis estáticos (HTML + Chart.js, arquivo único cada), sem dependências
de build ou backend.

| Página | O que mostra |
|---|---|
| `index.html` | Painel Pedagógico do **2º Simulado 2026** — 128 alunos, 4 turmas, 50 questões, 9 disciplinas. |
| `comparativo.html` | Comparativo entre o **1º e o 2º Simulado 2026** — evolução de alunos, turmas e disciplinas. |

O `index.html` é o painel original e **não foi alterado** além de um botão de
navegação no cabeçalho ("Comparativo 1º × 2º Simulado") que leva ao
`comparativo.html`. Nenhum gráfico, filtro, cálculo ou dado do Painel 2 foi
tocado. O comparativo é um arquivo à parte, com seus próprios dados e sua
própria lógica — os dois nunca leem um do outro.

---

## Arquivos

| Arquivo | Função |
|---|---|
| `index.html` | Painel do 2º Simulado. Dados na constante `DATA`. |
| `comparativo.html` | Comparativo 1º × 2º Simulado. Dados nas constantes `DATA1` (1º) e `DATA2` (2º). |
| `dados/1_Simulado_EvaBee_Lucas.xlsx` | Planilha do 1º Simulado, só com as abas usadas (`Reports`, `Página1`). |
| `dados/2_Simulado_2026.xlsx` | Planilha do 2º Simulado, sem a aba de cadastro pessoal (`Reports ORIGINAL`, `Leticia`). |
| `atualizar_dados.py` | Regenera o `DATA` do `index.html` a partir da planilha do 2º Simulado. |
| `atualizar_comparativo.py` | Regenera `DATA1`/`DATA2` do `comparativo.html` a partir das duas planilhas. |
| `netlify.toml` / `.gitignore` | Configuração de publicação e proteção contra versionar as planilhas originais. |

---

## Metodologia do comparativo — o que foi verificado antes de calcular qualquer coisa

**Correspondência entre simulados.** Feita pela matrícula (`Núm. da lista`),
que é o mesmo identificador nas duas planilhas — não pelo nome, para não
juntar pessoas diferentes por coincidência de grafia. Resultado: **115 alunos
comuns** aos dois simulados, **9** só têm registro no 1º e **13** só no 2º.
Nenhum desses 22 casos é tratado como falta, reprovação ou queda — apenas
como dado indisponível para comparação.

**Duas populações, dois usos diferentes:**
- *Coorte completa de cada simulado* (todos os alunos daquela prova, comuns
  ou não): usada em média geral, participação, melhor desempenho, comparativo
  por turma e na matriz turma × disciplina — porque essas visões descrevem a
  turma como instituição, não uma pessoa específica.
- *Apenas os alunos comuns*: usada em evolução individual, comparativo por
  disciplina e distribuição de evolução — porque aí a comparação só faz
  sentido entre exatamente a mesma pessoa nos dois momentos.

Essa divisão está documentada também dentro da própria página, no aviso
amarelo do topo, e no rótulo de cada seção.

**Margem de estabilidade.** Variações entre **-5 e +5 pontos percentuais**
são classificadas como "Estável"; fora disso, "Subiu" ou "Caiu". Esse valor é
uma constante (`LIMIAR`) no início do script — mude-o ali se quiser um
critério mais ou menos rígido.

**Por que percentual de acerto, e não nota bruta.** As duas provas têm a
mesma estrutura: 50 questões, mesmas 9 disciplinas, nos mesmos intervalos de
questão. Isso permite comparar tanto por percentual quanto por acertos brutos
— o comparativo usa percentual como métrica principal (mais robusta a
qualquer diferença futura no número de questões) e mostra os acertos brutos
como apoio nos KPIs gerais.

### Uma divergência encontrada e como foi tratada

A planilha do 1º Simulado tem duas abas com totais de acerto já calculados:
`Reports_LUCAS` e `Consulta Profes.`. Elas **divergem em 72 dos 123 alunos em
comum entre as duas**, sempre pela mesma margem: `Consulta Profes.` está
sistematicamente **1 acerto a mais**. Recalculando a partir da aba bruta
`Reports` (alternativa marcada × gabarito × pontuação oficial, questão a
questão), o valor de `Reports_LUCAS` bate exatamente — `Consulta Profes.`
está errada.

Por isso o comparativo, assim como o Painel 2, **nunca lê totais
pré-calculados**: ele recalcula os acertos de cada aluno diretamente das
respostas e do gabarito da aba `Reports` (1º Simulado) / `Reports ORIGINAL`
(2º Simulado). Isso também é o que já fazia o Painel 2 para o 2º Simulado; o
mesmo padrão foi replicado aqui para o 1º.

**Efeito prático:** se qualquer relatório antigo do 1º Simulado foi montado a
partir de `Consulta Profes.`, seus números de acerto por aluno estão, em
média, superestimados. Vale avisar quem usou aquela aba antes.

**Duplas marcações.** 19 questões no 1º Simulado e 17 no 2º têm duas
alternativas marcadas pelo aluno na mesma questão. Em ambos os casos a
correção oficial pontua como erro — o comparativo segue essa mesma regra dos
dois lados, para não inflar nenhum dos dois simulados.

**Mudança de turma.** Um aluno (matrícula 1234) migrou da Turma 1 para a
Turma 2 entre os dois simulados. Ele entra na Turma 1 quando o comparativo
olha para o 1º Simulado e na Turma 2 quando olha para o 2º — cada seção usa a
turma que o aluno tinha *naquela* prova, exceto o comparativo individual, que
mostra sempre a turma mais recente.

---

## Indicadores implementados

- **Média geral** — acertos médios 1º × 2º, variação absoluta, escala
  dinâmica conforme o total de questões do recorte (disciplina ou prova
  inteira).
- **Taxa média de acertos** — percentual 1º × 2º, diferença em p.p.
- **Participação** — alunos por simulado, comuns, exclusivos de cada um.
- **Evolução dos alunos** — subiram / estáveis / caíram, com o critério de
  ±5 p.p. documentado na tela.
- **Melhor desempenho** — aluno com mais acertos em cada simulado
  (independentes um do outro, já que o melhor do 1º pode não ser o melhor do
  2º).
- **Desempenho por disciplina** — maior evolução e maior queda média, sempre
  sobre os alunos comuns.
- **Comparativo por disciplina** — gráfico de barras agrupadas, gráfico de
  variação, tabela com questões/percentuais/variação/alunos considerados.
- **Comparativo por turma** — gráfico agrupado, tabela com alunos avaliados e
  variação, cada simulado com sua própria coorte.
- **Comparativo individual** — tabela buscável e ordenável, com a disciplina
  de maior variação de cada aluno; clique abre o perfil com gráfico de barras
  1º × 2º por disciplina.
- **Matriz de evolução turma × disciplina** — heatmap com a variação em p.p.
  de cada cruzamento.
- **Distribuição da evolução** — quantos alunos evoluíram, mantiveram-se
  estáveis ou caíram.
- **Leitura pedagógica** — cartões de texto gerados a partir dos dados
  filtrados no momento (tendência geral, disciplina que mais evoluiu, maior
  queda, cobertura da comparação).

Filtros: turma, disciplina e busca por nome, combináveis, mais um alternador
que decide se a tabela individual mostra só os alunos comuns ou também os
exclusivos de um simulado.

## Limitações conhecidas

- 22 alunos (9 do 1º, 13 do 2º) não entram nas métricas de evolução por não
  terem registro nos dois simulados — o motivo real (transferência, ausência
  pontual, entrada tardia) não está nos dados e não foi inferido.
- A matriz turma × disciplina e o comparativo por turma comparam coortes
  completas, não os mesmos indivíduos — uma turma pode "evoluir" em parte por
  troca de alunos, não só por aprendizado. Isso está declarado no rótulo de
  cada seção.
- Não há boxplot nem heatmap aluno × disciplina no comparativo (o do Painel 2
  já cobre o 2º Simulado isoladamente); ficou de fora para manter a página
  legível com duas provas ao mesmo tempo. Pode ser adicionado depois, se for
  útil.

## Testes realizados

- Recálculo independente (fora do navegador) de: alunos por simulado (124 e
  128), alunos comuns (115), média de acertos de cada simulado (22,99/50 e
  25,59/50), evolução por disciplina e por turma, e o caso do aluno que
  mudou de turma — todos batendo com o que a página exibe.
- Verificação de que `DATA2` dentro do `comparativo.html` é byte a byte
  idêntico ao `DATA` usado no `index.html` — a mesma fonte, a mesma
  correção, sem duas versões divergentes dos dados do 2º Simulado circulando.
- Sintaxe do JavaScript de ambas as páginas validada antes da publicação.
- Conferido que o `index.html` continua funcionando exatamente como antes:
  nenhum seletor, função ou variável existente foi removido ou renomeado; a
  única adição é o link de navegação e uma regra CSS nova para estilizá-lo.

---

## Executar localmente

```bash
python3 -m http.server 8000
# abrir http://localhost:8000  (Painel 2)
# abrir http://localhost:8000/comparativo.html (Comparativo)
```

## Atualizar os dados

Depois de um novo simulado, rode os dois scripts (são independentes):

```bash
pip install openpyxl

# Atualiza só o Painel 2 (index.html)
python3 atualizar_dados.py

# Atualiza só o Comparativo (comparativo.html) — pode apontar para
# quaisquer duas planilhas no mesmo formato
python3 atualizar_comparativo.py
python3 atualizar_comparativo.py caminho/simulado_antigo.xlsx caminho/simulado_novo.xlsx
```

Cada script grava um `.js` com o(s) bloco(s) de dados prontos; copie o
conteúdo por cima da linha `const DATA = ...` (ou `DATA1`/`DATA2`) no HTML
correspondente. Ambos recusam o trabalho se a soma de acertos calculada não
bater com o total declarado na planilha para qualquer aluno.

## Publicar no GitHub e no Netlify

Igual ao processo já em uso:

```bash
git init
git add .
git commit -m "Painel Pedagógico + Comparativo 1º x 2º Simulado 2026"
git branch -M main
git remote add origin git@github.com:SEU_USUARIO/pipa-simulado-2026.git
git push -u origin main
```

No Netlify: publish directory `.`, build command vazio. Como as duas páginas
são arquivos estáticos na raiz, nenhuma configuração de rota extra é
necessária — `/index.html` e `/comparativo.html` funcionam direto.

## Conferir a publicação

- `index.html` abre exatamente como antes, incluindo o novo botão vermelho
  "Comparativo 1º × 2º Simulado" no cabeçalho.
- O botão leva ao `comparativo.html`; o link "← Voltar ao Painel do 2º
  Simulado" no topo do comparativo volta sem perder nada.
- Aviso metodológico visível logo abaixo do cabeçalho do comparativo.
- Filtros de turma, disciplina e busca recalculando KPIs, gráficos e tabelas.
- Clique numa linha da tabela individual abrindo o perfil do aluno.
- Console do navegador (F12) sem erros em nenhuma das duas páginas.
