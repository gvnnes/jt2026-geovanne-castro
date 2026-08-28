# ai-log — Sessão de trabalho com IA (OpenCode)

Hackathon Jovens Talentos AI Builder 2026 · Geovanne Castro · Itapema (SC)
Modelo: `deepseek-v4-flash` (hub.seazone) · Ferramenta: OpenCode CLI

> Sessão completa com a IA, exportada em texto, conforme o critério de avaliação.
> Mostra o processo: planejamento, exploração, obstáculos, iteração e senso crítico.

---

## 1. Missão

Entregar recomendação de investimento imobiliário para a Seazone em Itapema (SC),
respondendo: (1) melhor perfil de imóvel, (2) melhor localização, (3) características
que explicam receita, (4) o que comprar hoje com estimativa de retorno — e tomar
posição sobre a tese interna de "compactos (studio/1q) no Centro".

## 2. Exploração dos dados (primeiros achados)

Bases (data/): `Details_Itapema.csv` (4.441 anúncios Airbnb), `Hosts_ids_Itapema.csv`
(hosts), `Mesh_Ids_Data_Itapema.csv` (bairro/lat/long), `Price_AV_Itapema.csv`
(118.839 linhas de preço, 1.005 imóveis, jan–abr/2025), `VivaReal_Itapema.csv`
(8.329 anúncios de venda).

- Preço/noite cresce com nº de quartos: studio R$441 → 1q R$446 → 2q R$571 → 3q R$737 → 4+ R$1.321.
- Preço/noite por bairro: Meia Praia R$723, Morretes R$665, Centro R$630.
- **Compra:** Centro é o mais caro por m² (R$17.450) — mais caro que Meia Praia (R$15.972).
  Isso apontou desde cedo que a tese dos compactos no Centro seria fraca em yield.
- Demanda: Meia Praia tem oferta gigante (2.860) com mediana de só 2 reviews — saturação.

## 3. Planejamento

Definido em conjunto: critério **yield líquido** (retorno sobre preço de compra),
ferramenta **Python + pandas** (instalei Python 3.12, que não existia no Windows),
relatório em **relatorio.md** com tabelas, e entrega de README + ai-log + roteiro de vídeo.

## 4. Construção (scripts)

- `scripts/common.py` — loader + normalização de bairros (case/acentos/variantes).
- `scripts/01_prep.py` — cruza bases, checa viés da amostra, corrige duplicação de hosts.
- `scripts/02_revenue.py` — preço por perfil, sazonalidade anual (fator ×0,92), índice de
  demanda (reviews/ano por anos do host) e cenários de ocupação (25/35/45%).
- `scripts/03_yield.py` — lado da compra (VivaReal) × receita → yield líquido por perfil.

## 5. Obstáculos e como resolvi

- **Sem Python/pandas no Windows** → instalei Python 3.12 via winget e criei venv do projeto.
- **Bug de duplicação no merge de hosts** (1 owner com vários snapshots) → dedupe pelo snapshot mais recente (4.441 → 3.057 hosts reais).
- **Sem dado de ocupação real** → usei cenários de ocupação e validei o *rank* por reviews/ano + % de imóveis sem review (proxy robusto de demanda/vacância).
- **`aquisition_date` não é idade do imóvel** (mediana 0,26 ano) → troquei o denominador de demanda por **anos do host** (mediana 5 anos), proxy mais honesto.

## 6. Resultados-chave

- **Yield líquido (cenário base, 35% ocupação):** Morretes 2q 8,2% · Morretes 3q 8,1% ·
  Meia Praia 1q 6,5% · Tabuleiro 2q 6,4% · **Centro 1q 4,9%** (pior).
- **Centro:** maior custo/m² (R$19.905), menor demanda (2,8 rev/ano), maior ociosidade (7,8% sem review).
- **Recomendação:** apto 2–3q em **Morretes** (~R$845 mil), yield 8,1%, payback 12,3 anos.
- **Tese interna (compactos no Centro): NÃO sustentada pelos dados.**

## 7. Senso crítico sobre a IA

A IA sugeriu índices e critérios que validei contra a realidade dos dados: rejeitei o uso
do `aquisition_date` como idade do imóvel, corrigi o viés de duplicação de hosts e
verifiquei que "preço/aluguel alto ≠ bom investimento" — o yield é quem manda.
A decisão final (Morretes vs tese do Centro) foi tomada a partir dos números, não da sugestão inicial.
