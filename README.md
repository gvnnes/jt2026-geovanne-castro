# Hackathon Jovens Talentos AI Builder 2026 — Seazone

> **Vídeo (3 min):** [ADICIONE AQUI O LINK DO GOOGLE DRIVE — compartilhamento "qualquer pessoa com o link"]

## 🎯 Recomendação final (resumo)

**Invista em apartamentos de 2 a 3 quartos no bairro de Morretes (~R$ 790–845 mil).** Yield líquido de ~8,1% ao ano no cenário base (35% de ocupação), payback de ~12 anos.

**Posição sobre a tese interna dos compactos no Centro: os dados NÃO a sustentam.** O Centro é o bairro mais caro por m² (R$ 19.905), tem a menor demanda relativa (2,8 reviews/ano) e o maior risco de ociosidade (7,8% sem reviews) → yield baixo de 4,9%, abaixo da meta de ~6% e longe dos ~8% de Morretes.

📄 **[Relatório completo → `relatorio.md`](relatorio.md)** · 🎬 **[Roteiro do vídeo → `roteiro-video.md`](roteiro-video.md)** · 📊 **[Dashboard → `dashboard/index.html`](dashboard/index.html)**

O dashboard é uma página HTML autocontida com gráficos e tabelas mostrando **por que Morretes é a melhor opção**. Abra `dashboard/index.html` no navegador.

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
- **`roteiro-video.md`** — roteiro do vídeo de 3 minutos.
- **`ai-log/`** — sessão de trabalho com a IA exportada em texto (parte da avaliação).

## Sobre os dados

Análise feita sobre o snapshot do mercado imobiliário de **Itapema (SC)**, com anúncios de Airbnb e de venda (VivaReal), localizados em `data/`:

| Arquivo | Conteúdo |
|---|---|
| `Details_Itapema.csv` | Anúncios de Airbnb (tipo, quartos, reviews, ratings) |
| `Hosts_ids_Itapema.csv` | Dados dos anfitriões |
| `Mesh_Ids_Data_Itapema.csv` | Bairro + coordenadas dos anúncios |
| `Price_AV_Itapema.csv` | Preço por anúncio e data |
| `VivaReal_Itapema.csv` | Anúncios de venda (mercado de compra) |
