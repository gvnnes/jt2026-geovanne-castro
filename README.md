# Hackathon Jovens Talentos AI Builder 2026 — Seazone

> **Vídeo (3 min):** [ADICIONE AQUI O LINK DO GOOGLE DRIVE — compartilhamento "qualquer pessoa com o link"]

## 🎯 Recomendação final (resumo)

**Invista em apartamentos de 2 a 3 quartos no bairro de Morretes (~R$ 790–845 mil).** Yield líquido de ~8,1% ao ano no cenário base (35% de ocupação), payback de ~12 anos.

**Posição sobre a tese interna dos compactos no Centro: os dados NÃO a sustentam.** O Centro é o bairro mais caro por m² (R$ 19.905), tem a menor demanda relativa (2,8 reviews/ano) e o maior risco de ociosidade (7,8% sem reviews) → yield de apenas 4,9%, o menor da cidade.

📄 **[Relatório completo → `relatorio.md`](relatorio.md)** · 🎬 **[Roteiro do vídeo → `roteiro-video.md`](roteiro-video.md)**

---

## 👉 Leia o desafio aqui

### **[ABRIR O DESAFIO COMPLETO](https://seazone-tech.github.io/jovens-talentos-2026-hackathon-data/)**

Lá está tudo: a missão, os dados, **o que entregar**, as regras, o prazo e **como vamos avaliar**.
Leia antes de começar a mexer nos dados.

> Se o link acima não abrir, o mesmo conteúdo está no arquivo [`index.html`](index.html) deste repositório
> (baixe e abra no navegador).

---

## Primeiro passo

**Faça um _fork_ deste repositório.** É nele que você vai trabalhar e é ele que você entrega.

---

## Os dados (`data/`)

Snapshot estático do mercado imobiliário de **Itapema (SC)**, com anúncios de Airbnb e de venda (VivaReal).
É a mesma base para todos os candidatos, para garantir comparação justa.

| Arquivo | O que tem | Como conecta |
|---|---|---|
| `Details_Itapema.csv` | Cada anúncio de Airbnb: título, reviews, star rating, descrição, host_id, nº de quartos, tipo de imóvel | Base principal dos listings |
| `Hosts_ids_Itapema.csv` | Dados do anfitrião: nº de reviews, anos como host, superhost, taxa de resposta | Liga com Details pelo `owner_id` |
| `Mesh_Ids_Data_Itapema.csv` | Latitude/longitude + bairro de cada anúncio | Liga por listing |
| `Price_AV_Itapema.csv` | Preço por anúncio, por data de estadia e por data de captura | Liga por listing |
| `VivaReal_Itapema.csv` | Anúncios de venda: preço, condomínio, área, vendedor | Mercado de compra |

---

## Resumo do que você entrega

1. **Este repositório, forkado e público**, com a sua análise, o `README.md` explicando como rodar,
   a pasta `ai-log/` (conversas com a IA **em texto**) e a recomendação final escrita.
2. **Vídeo de até 3 minutos** no Google Drive, com o link na primeira linha do seu README.

O detalhe de cada item, o prazo e o formulário de entrega estão no
**[desafio completo](https://seazone-tech.github.io/jovens-talentos-2026-hackathon-data/)**.

---

*Seazone — Jovens Talentos AI Builder 2026*

---

## Como rodar a análise

Pré-requisito: Python 3.12.

```bash
# 1. criar o ambiente e instalar dependências
python -m venv .venv
.venv/Scripts/python.exe -m pip install pandas numpy matplotlib

# 2. executar o pipeline (ordem importa)
.venv/Scripts/python.exe scripts/01_prep.py    # prepara e cruza as bases
.venv/Scripts/python.exe scripts/02_revenue.py # modelo de receita (preço/demanda/sazonalidade)
.venv/Scripts/python.exe scripts/03_yield.py   # lado da compra (VivaReal) + yield líquido
```

Saídas em `output/`:
- `output/clean/` — bases consolidadas (listings com preço, preço por imóvel, VivaReal normalizado).
- `output/revenue/` — preço por perfil, demanda/competição por bairro, cenários de receita.
- `output/yield/` — yield líquido por perfil e cenário de ocupação.

- **`relatorio.md`** — recomendação final e posição sobre a tese dos compactos no Centro.
- **`roteiro-video.md`** — roteiro do vídeo de 3 minutos.
- **`ai-log/`** — sessão de trabalho com a IA exportada em texto (parte da avaliação).

