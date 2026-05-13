# Snakefile — project pipeline
#
# Download rules  — rules with no input files are skipped automatically when
#                   their outputs exist. Delete the sentinel or use
#                   `snakemake --cores 1 -R <rule>` to force a re-run.
#
# rule all        — builds all final processed outputs when you run
#                   `snakemake --cores 1` with no target argument.
#
# Common commands:
#   snakemake --cores 1 -n          dry-run: show what would be executed
#   snakemake --cores 4             run everything (up to 4 parallel jobs)
#   snakemake --cores 1 <target>    build one specific output
#   snakemake --cores 1 -R <rule>   force-re-run a specific rule
#   snakemake --forceall --cores 4  re-run everything unconditionally

INDUSTRIES_30 = [
    "Food", "Beer", "Smoke", "Games", "Books", "Hshld", "Clths", "Hlth",
    "Chems", "Txtls", "Cnstr", "Steel", "FabPr", "ElcEq", "Autos", "Carry",
    "Mines", "Coal", "Oil", "Util", "Telcm", "Servs", "BusEq", "Paper",
    "Trans", "Whlsl", "Rtail", "Meals", "Fin", "Other",
]

COUNTRIES_FULL_PERIOD = [
    "AUS", "BEL", "CHE", "DEU", "ESP", "FRA", "GBR",
    "HKG", "ITA", "JPN", "NLD", "NOR", "SGP", "SWE",
]

# ---------------------------------------------------------------------------
# Default target — all final processed outputs
# ---------------------------------------------------------------------------

rule all:
    input:
        "data/processed/ken_french/countries_synth_prices.csv",
        "data/processed/ken_french/industries_synth_prices.csv",
        "book/notebooks/04_analyse_industry_portfolios.ipynb",
        "book/notebooks/05_analyse_country_portfolios.ipynb",
        "book/notebooks/06_industry_trend_following.ipynb",
        "book/notebooks/07_country_trend_following.ipynb",

# ---------------------------------------------------------------------------
# Download rules
# ---------------------------------------------------------------------------

rule download_country_data:
    output:
        directory("data/downloads/ken_french/international_countries"),
    shell:
        "uv run python pipeline/01_download_country_data.py"

rule download_industry_portfolios_30:
    output:
        directory("data/downloads/ken_french/industry_portfolios_30"),
    shell:
        "uv run python pipeline/01_download_industry_portfolios_30.py"

# ---------------------------------------------------------------------------
# Processing rules
# ---------------------------------------------------------------------------

rule process_country_returns:
    input:
        downloads = "data/downloads/ken_french/international_countries",
        script    = "pipeline/02_process_country_returns.py",
    output:
        directory("data/processed/ken_french/international_countries/monthly_returns"),
    shell:
        "uv run python {input.script}"

rule process_industry_portfolios_30:
    input:
        downloads = "data/downloads/ken_french/industry_portfolios_30",
        script    = "pipeline/02_process_industry_portfolios_30.py",
    output:
        "data/processed/ken_french/industry_portfolios_30/daily_returns.csv",
    shell:
        "uv run python {input.script}"

rule analyse_industry_portfolios:
    input:
        script = "pipeline/04_analyse_industry_portfolios.py",
        data   = "data/processed/ken_french/industries_synth_prices.csv",
    output:
        notebook = "book/notebooks/04_analyse_industry_portfolios.ipynb",
        img1     = "output/images/04_industry_prices.png",
        img2     = "output/images/04_industry_log_prices.png",
        img3     = "output/images/04_industry_yearly_heatmap.png",
        img4     = "output/images/04_industry_risk_return.png",
        img5     = "output/images/04_industry_drawdowns.png",
        img6     = "output/images/04_industry_vol_return.png",
        img7     = "output/images/04_industry_dd_return.png",
        img8     = "output/images/04_industry_drawdown_bar.png",
        img9     = "output/images/04_industry_dd_duration_bar.png",
        img10    = "output/images/04_industry_yearly_dd_heatmap.png",
    shell:
        """
        MPLBACKEND=Agg uv run jupytext --to notebook --execute \
            --set-kernel python3 \
            --output {output.notebook} {input.script} && \
        uv run python -c "
import nbformat
nb = nbformat.read('{output.notebook}', as_version=4)
nb.cells = [c for c in nb.cells
            if not (c.cell_type == 'raw' and 'jupytext' in c.source)]
nb.metadata.pop('jupytext', None)
nbformat.write(nb, '{output.notebook}')
"
        """

rule analyse_country_portfolios:
    input:
        script = "pipeline/05_analyse_country_portfolios.py",
        data   = "data/processed/ken_french/countries_synth_prices.csv",
    output:
        notebook = "book/notebooks/05_analyse_country_portfolios.ipynb",
        img1     = "output/images/05_country_prices.png",
        img2     = "output/images/05_country_log_prices.png",
        img3     = "output/images/05_country_drawdowns.png",
        img4     = "output/images/05_country_yearly_heatmap.png",
        img5     = "output/images/05_country_yearly_dd_heatmap.png",
        img6     = "output/images/05_country_risk_return.png",
        img7     = "output/images/05_country_vol_return.png",
        img8     = "output/images/05_country_dd_return.png",
        img9     = "output/images/05_country_drawdown_bar.png",
        img10    = "output/images/05_country_dd_duration_bar.png",
        img11    = "output/images/05_country_date_ranges.png",
    shell:
        """
        MPLBACKEND=Agg uv run jupytext --to notebook --execute \
            --set-kernel python3 \
            --output {output.notebook} {input.script} && \
        uv run python -c "
import nbformat
nb = nbformat.read('{output.notebook}', as_version=4)
nb.cells = [c for c in nb.cells
            if not (c.cell_type == 'raw' and 'jupytext' in c.source)]
nb.metadata.pop('jupytext', None)
nbformat.write(nb, '{output.notebook}')
"
        """

rule industry_trend_following:
    input:
        script = "pipeline/06_industry_trend_following.py",
        data   = "data/processed/ken_french/industries_synth_prices.csv",
    output:
        notebook = "book/notebooks/06_industry_trend_following.ipynb",
        img1     = "output/images/06_industry_tf_risk_return.png",
        img2     = "output/images/06_industry_tf_dd_return.png",
        img3     = "output/images/06_industry_tf_ret_scatter.png",
        img4     = "output/images/06_industry_tf_dd_scatter.png",
        img8     = "output/images/06_industry_tf_cw_risk_return.png",
        img9     = "output/images/06_industry_tf_cw_dd_return.png",
        img5     = "output/images/06_industry_tf_frac_invested_bar.png",
        img6     = "output/images/06_industry_tf_invested_heatmap.png",
        img7     = "output/images/06_industry_tf_turnover_bar.png",
        per_asset = expand("output/images/06_industry_tf_{industry}.png", industry=INDUSTRIES_30),
    shell:
        """
        MPLBACKEND=Agg uv run jupytext --to notebook --execute \
            --set-kernel python3 \
            --output {output.notebook} {input.script} && \
        uv run python -c "
import nbformat
nb = nbformat.read('{output.notebook}', as_version=4)
nb.cells = [c for c in nb.cells
            if not (c.cell_type == 'raw' and 'jupytext' in c.source)]
nb.metadata.pop('jupytext', None)
nbformat.write(nb, '{output.notebook}')
"
        """

rule country_trend_following:
    input:
        script = "pipeline/07_country_trend_following.py",
        data   = "data/processed/ken_french/countries_synth_prices.csv",
    output:
        notebook  = "book/notebooks/07_country_trend_following.ipynb",
        img1      = "output/images/07_country_tf_risk_return.png",
        img2      = "output/images/07_country_tf_dd_return.png",
        img3      = "output/images/07_country_tf_ret_scatter.png",
        img4      = "output/images/07_country_tf_dd_scatter.png",
        img8      = "output/images/07_country_tf_cw_risk_return.png",
        img9      = "output/images/07_country_tf_cw_dd_return.png",
        img5      = "output/images/07_country_tf_frac_invested_bar.png",
        img6      = "output/images/07_country_tf_invested_heatmap.png",
        img7      = "output/images/07_country_tf_turnover_bar.png",
        per_asset = expand("output/images/07_country_tf_{country}.png", country=COUNTRIES_FULL_PERIOD),
    shell:
        """
        MPLBACKEND=Agg uv run jupytext --to notebook --execute \
            --set-kernel python3 \
            --output {output.notebook} {input.script} && \
        uv run python -c "
import nbformat
nb = nbformat.read('{output.notebook}', as_version=4)
nb.cells = [c for c in nb.cells
            if not (c.cell_type == 'raw' and 'jupytext' in c.source)]
nb.metadata.pop('jupytext', None)
nbformat.write(nb, '{output.notebook}')
"
        """

rule create_synth_prices:
    input:
        countries  = "data/processed/ken_french/international_countries/monthly_returns",
        industries = "data/processed/ken_french/industry_portfolios_30/daily_returns.csv",
        script     = "pipeline/03_create_synth_prices.py",
    output:
        "data/processed/ken_french/countries_synth_prices.csv",
        "data/processed/ken_french/industries_synth_prices.csv",
    shell:
        "uv run python {input.script}"
