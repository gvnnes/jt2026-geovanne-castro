"""run_all.py — executa todo o pipeline de uma vez.

Roda, em ordem: 01_prep → 02_revenue → 03_yield → 04_dashboard_charts
e, ao final, monta o index.html da raiz a partir do dashboard.

Execução: python scripts/run_all.py
"""
import sys, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable

STEPS = [
    ("01_prep.py",            "Preparação e cruzamento das bases"),
    ("02_revenue.py",         "Modelo de receita (preço/demanda/sazonalidade)"),
    ("03_yield.py",           "Lado da compra (VivaReal) + yield líquido"),
    ("04_dashboard_charts.py","Geração dos gráficos do dashboard"),
]


def build_landing():
    """Gera o index.html da raiz a partir do dashboard/index.html,
    ajustando os caminhos relativos das imagens (graficos/ -> dashboard/graficos/)."""
    src = os.path.join(ROOT, "dashboard", "index.html")
    dst = os.path.join(ROOT, "index.html")
    print("\n--- [Landing page] (index.html a partir do dashboard) ---")
    with open(src, encoding="utf-8") as f:
        html = f.read()
    html = html.replace('src="graficos/', 'src="dashboard/graficos/')
    with open(dst, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Gerado {dst}")


def main():
    print("=" * 70)
    print("PIPELINE ITAPEMA — SEAZONE")
    print("=" * 70)
    for script, desc in STEPS:
        path = os.path.join(HERE, script)
        print(f"\n--- [{desc}] ({script}) ---")
        rc = subprocess.call([PY, path])
        if rc != 0:
            print(f"\nERRO ao executar {script} (código {rc}). Encerrando.")
            sys.exit(rc)
    build_landing()
    print("\n" + "=" * 70)
    print("Pipeline concluído com sucesso.")
    print("Resultados em output/ e gráficos em dashboard/graficos/.")
    print("Dashboard: abra index.html (raiz) no navegador.")
    print("=" * 70)


if __name__ == "__main__":
    main()
