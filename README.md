# PiPA — Painel Pedagógico — 2º Simulado 2026

Painel estático (HTML + Chart.js, arquivo único) com os resultados do 2º Simulado 2026
do Instituto PiPA. Projeto independente do Modelo 1 — nada do repositório anterior é
alterado por este.

**128 alunos · 4 turmas · 50 questões · 9 disciplinas**

---

## Arquivos

| Arquivo | Função |
|---|---|
| `index.html` | O painel inteiro, autocontido. Os dados vivem na constante `DATA`, no início do bloco `<script>`. |
| `dados/2_Simulado_2026.xlsx` | Planilha do simulado, **sem a aba de cadastro pessoal**. Fonte dos dados. |
| `atualizar_dados.py` | Lê a planilha e gera `data_block.js` para atualizar o painel. |
| `netlify.toml` | Configuração de publicação. |
| `.gitignore` | Impede o versionamento acidental da planilha original. |

---

## Antes de subir: a planilha original não vai para o GitHub

A planilha recebida tem três abas. A terceira, chamada `.`, é o cadastro completo dos
alunos: nome civil, data de nascimento, idade, gênero, cor, telefone do aluno, nome e
telefone dos responsáveis legais e autorização de atendimento psicológico. São 136
registros de menores de idade.

Essa aba **não é usada pelo painel** e **não pode ir para um repositório público**.
O arquivo em `dados/` é uma cópia com as duas abas necessárias apenas:

- `Reports ORIGINAL` — alternativa marcada (`Q n Options`), gabarito (`Q n Key`) e
  pontuação oficial (`Q n Marks`). É a fonte autoritativa.
- `Leticia` — usada só pela linha 2, que mapeia disciplina → questão.

O `.gitignore` já bloqueia o nome do arquivo original. Se for necessário guardar o
arquivo completo em algum lugar, use o Drive do instituto, não o Git.

### Sobre os nomes no painel publicado

O painel exibe o nome completo de cada aluno e a posição no ranking. Publicado no
Netlify sem proteção, isso fica acessível a qualquer pessoa com o link. Duas opções, se
quiser restringir:

- **Netlify → Site configuration → Access control → Password protection** (plano pago).
- Trocar os nomes por primeiro nome + inicial do sobrenome no `atualizar_dados.py`.

---

## Executar localmente

```bash
python3 -m http.server 8000
# abrir http://localhost:8000
```

Abrir o `index.html` direto no navegador também funciona.

## Atualizar para um próximo simulado

```bash
pip install openpyxl
python3 atualizar_dados.py                        # usa dados/2_Simulado_2026.xlsx
python3 atualizar_dados.py outra/planilha.xlsx    # ou aponte para outro arquivo
```

O script grava `data_block.js`. Abra o `index.html`, localize a linha que começa com
`const DATA = ` e substitua-a inteira pelo conteúdo do arquivo gerado. Pronto — o
painel se ajusta sozinho ao novo número de alunos, turmas, questões e disciplinas.

O script recusa o trabalho se a soma da coluna `Marks` divergir do `Total de marcas`
declarado para qualquer aluno, e lista ao final todas as questões com dupla marcação.

## Publicar no GitHub

```bash
git init
git add .
git commit -m "Painel Pedagógico — 2º Simulado 2026"
git branch -M main
git remote add origin git@github.com:SEU_USUARIO/pipa-simulado-2026.git
git push -u origin main
```

Confira `git status` antes do commit: a planilha original não deve aparecer.

## Publicar no Netlify

1. Netlify → **Add new site** → **Import an existing project** → GitHub → escolher o repositório.
2. Build command: vazio. Publish directory: `.`
3. **Deploy site**.
4. **Site configuration → Change site name** para definir a URL, ex.: `pipa-simulado-2026`.

Sem Git: arraste a pasta para o **Netlify Drop** (app.netlify.com/drop).

## Conferir a publicação

- Deploy marcado como **Published** no painel do Netlify.
- Cabeçalho mostrando 128 alunos / 50 questões / 4 turmas / 9 disciplinas.
- Filtros de turma, disciplina e faixa recalculando os gráficos.
- Clique numa linha do ranking (abre o perfil) e numa barra de questão (abre o detalhe).
- Console do navegador (F12) sem erros.
- Teste em tela estreita pelo modo dispositivo do DevTools.

---

## Notas de apuração

- **17 questões com dupla marcação** (o aluno preencheu duas alternativas). A correção
  oficial pontua todas como zero; o painel as mostra em roxo, marcadas `2×`.
- **3 questões em branco** no simulado inteiro.
- A aba `Leticia` desloca as respostas dos alunos com dupla marcação, porque a vírgula
  ocupa uma célula própria. Por isso os cálculos vêm da aba `Reports ORIGINAL`, e não
  daquela. Recalcular pela `Leticia` produziria média 25,23 em vez dos 25,59 reais.
