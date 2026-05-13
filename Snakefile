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
# Utility rules
# ---------------------------------------------------------------------------

rule dag:
    input:
        "Snakefile"
    output:
        "dag.png"
    shell:
        "uv run snakemake --dag 2>/dev/null | dot -Tpng > {output}"

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
    shell:
        "bash pipeline/convert_to_nb_and_run.sh {input.script} {output.notebook}"

rule analyse_country_portfolios:
    input:
        script = "pipeline/05_analyse_country_portfolios.py",
        data   = "data/processed/ken_french/countries_synth_prices.csv",
    output:
        notebook = "book/notebooks/05_analyse_country_portfolios.ipynb",
    shell:
        "bash pipeline/convert_to_nb_and_run.sh {input.script} {output.notebook}"

rule industry_trend_following:
    input:
        script = "pipeline/06_industry_trend_following.py",
        data   = "data/processed/ken_french/industries_synth_prices.csv",
    output:
        notebook = "book/notebooks/06_industry_trend_following.ipynb",
    shell:
        "bash pipeline/convert_to_nb_and_run.sh {input.script} {output.notebook}"

rule country_trend_following:
    input:
        script = "pipeline/07_country_trend_following.py",
        data   = "data/processed/ken_french/countries_synth_prices.csv",
    output:
        notebook  = "book/notebooks/07_country_trend_following.ipynb",
    shell:
        "bash pipeline/convert_to_nb_and_run.sh {input.script} {output.notebook}"

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
