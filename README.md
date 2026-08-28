# Hackathon Jovens Talentos AI Builder 2026 — Seazone

> **Vídeo (3 min):** https://drive.google.com/drive/folders/16GcQvyIdf5C9w3o67ukRRo7KqxO9cLLv?usp=sharing

📄 **[Relatório completo → `relatorio.md`](relatorio.md)**
📊 **[Dashboard → `dashboard/index.html`](dashboard/index.html)**
O dashboard é uma página HTML autocontida com gráficos e tabelas mostrando **por que Morretes é a melhor opção**. Abra `dashboard/index.html` no navegador.

## 🎯 Recomendação final (resumo)

**Invista em apartamentos de 2 a 3 quartos no bairro de Morretes (~R$ 790–845 mil).** Yield líquido de ~8,1% ao ano no cenário base (35% de ocupação), payback de ~12 anos.

**Posição sobre a tese interna dos compactos no Centro: os dados NÃO a sustentam.** O Centro é o bairro mais caro por m² (R$ 19.905), tem a menor demanda relativa (2,8 reviews/ano) e o maior risco de ociosidade (7,8% sem reviews) → yield baixo de 4,9%, abaixo da meta de ~6% e longe dos ~8% de Morretes.

---

## Como rodar a análise

Pré-requisito: Python 3.12.

```bash
# 1. criar o ambiente e instalar dependências
python -m venv .venv
.venv/Scripts/python.exe -m pip install pandas numpy matplotlib

# 2. executar toda a análise de uma vez
.venv/Scripts/python.exe scripts/run_all.py

# (opcional) executar passo a passo, na ordem
.venv/Scripts/python.exe scripts/01_prep.py             # prepara e cruza as bases
.venv/Scripts/python.exe scripts/02_revenue.py          # modelo de receita
.venv/Scripts/python.exe scripts/03_yield.py            # yield líquido (compra)
.venv/Scripts/python.exe scripts/04_dashboard_charts.py # gera gráficos do dashboard
```

Saídas em `output/`:
- `output/clean/` — bases consolidadas (listings com preço, preço por imóvel, VivaReal normalizado).
- `output/revenue/` — preço por perfil, demanda/competição por bairro, cenários de receita.
- `output/yield/` — yield líquido por perfil e cenário de ocupação.

- **`relatorio.md`** — recomendação final e posição sobre a tese dos compactos no Centro.
- **`ai-log/`** — sessão de trabalho com a IA exportada em texto (parte da avaliação).


## Sobre a atuação da IA

O opencode foi utilizado como assistente na criação dessa analise, em geral seu uso foi extremamente satisfatório com algumas ressalvas em momentos que ele delirou ou inventou coisas, um exemplo que tive que corrigir depois de revisar foi que em versões anteriores do relatorio ele definiu em 15% a "taxa da seazone", apos revisar perguntei de que parte dos dados ele tirou isso e ele disse que inventou usando padroes de mercado, pedi para que ele deixasse isso claro no relatorio. Outra situacao foi quanto a "taxa de ociosidade" que inicialmente ele tratou como fato mas apos eu perguntar de onde ele tirou essa taxa ele tratou como uma logica que ele criou baseado nos padroes comparando os dados, entao ela entra mais como um proxy do que um fato. Pedi para que ele deixasse esses dois pontos claros no relatorio para manter a transparencia.

## Sobre os dados

Análise feita sobre o snapshot do mercado imobiliário de **Itapema (SC)**, com anúncios de Airbnb e de venda (VivaReal), localizados em `data/`:

| Arquivo | Conteúdo |
|---|---|
| `Details_Itapema.csv` | Anúncios de Airbnb (tipo, quartos, reviews, ratings) |
| `Hosts_ids_Itapema.csv` | Dados dos anfitriões |
| `Mesh_Ids_Data_Itapema.csv` | Bairro + coordenadas dos anúncios |
| `Price_AV_Itapema.csv` | Preço por anúncio e data |
| `VivaReal_Itapema.csv` | Anúncios de venda (mercado de compra) |
