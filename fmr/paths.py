"""Project paths configuration.

All paths are resolved relative to the project root, making scripts runnable
from any working directory. Add a @property for each new data file introduced
in the pipeline.
"""

from pathlib import Path


class ProjPaths:
    """Centralized project paths.

    The root is inferred from the location of this file (pkg/), so scripts
    run correctly regardless of the working directory they are invoked from.
    """

    def __init__(self):
        self._pkg_path = Path(__file__).resolve().parent  # pkg/
        self._project_path = self._pkg_path.parent        # project root

    # ------------------------------------------------------------------ #
    # Top-level directories                                                #
    # ------------------------------------------------------------------ #

    @property
    def project_path(self) -> Path:
        """Root project directory."""
        return self._project_path

    @property
    def pkg_path(self) -> Path:
        """Source package directory (pkg/)."""
        return self._pkg_path

    @property
    def pipeline_path(self) -> Path:
        """Pipeline scripts directory."""
        return self._project_path / "pipeline"

    # ------------------------------------------------------------------ #
    # Data directories                                                     #
    # ------------------------------------------------------------------ #

    @property
    def data_path(self) -> Path:
        """Main data directory."""
        return self._project_path / "data"

    @property
    def downloads_path(self) -> Path:
        """Raw downloaded data."""
        return self.data_path / "downloads"

    @property
    def processed_data_path(self) -> Path:
        """Processed/transformed data."""
        return self.data_path / "processed"

    # ------------------------------------------------------------------ #
    # Output directories                                                   #
    # ------------------------------------------------------------------ #

    @property
    def output_path(self) -> Path:
        """Generated outputs root."""
        return self._project_path / "output"

    @property
    def images_path(self) -> Path:
        """Chart/figure images saved by pipeline scripts."""
        return self.output_path / "images"

    @property
    def reports_path(self) -> Path:
        """Report files."""
        return self.output_path / "reports"

    # ------------------------------------------------------------------ #
    # Ken French data library                                             #
    # ------------------------------------------------------------------ #

    @property
    def ken_french_path(self) -> Path:
        """Root directory for all Ken French data library downloads."""
        return self.downloads_path / "ken_french"

    @property
    def international_countries_path(self) -> Path:
        """Extracted Ken French international country returns."""
        return self.ken_french_path / "international_countries"

    @property
    def international_countries_monthly_returns_path(self) -> Path:
        """Processed monthly market returns per country (CSV files)."""
        return self.processed_data_path / "ken_french" / "international_countries" / "monthly_returns"

    @property
    def industry_portfolios_30_path(self) -> Path:
        """Raw extracted Ken French 30 Industry Portfolios daily file."""
        return self.downloads_path / "ken_french" / "industry_portfolios_30"

    @property
    def industry_portfolios_30_daily_returns_path(self) -> Path:
        """Processed daily VW returns for 30 industry portfolios (CSV)."""
        return self.processed_data_path / "ken_french" / "industry_portfolios_30" / "daily_returns.csv"

    @property
    def ken_french_processed_path(self) -> Path:
        """Root directory for all processed Ken French outputs."""
        return self.processed_data_path / "ken_french"

    @property
    def countries_synth_prices_path(self) -> Path:
        """Synthetic prices for international countries (wide CSV, one column per ISO3)."""
        return self.ken_french_processed_path / "countries_synth_prices.csv"

    @property
    def industries_synth_prices_path(self) -> Path:
        """Synthetic prices for 30 industry portfolios (wide CSV, one column per industry)."""
        return self.ken_french_processed_path / "industries_synth_prices.csv"

    # ------------------------------------------------------------------ #
    # Example data files — replace with project-specific paths            #
    # ------------------------------------------------------------------ #

    @property
    def example_raw_file(self) -> Path:
        """Raw example dataset (parquet)."""
        return self.downloads_path / "example_data.parquet"

    @property
    def example_processed_file(self) -> Path:
        """Processed example dataset (parquet)."""
        return self.processed_data_path / "example_processed.parquet"

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def ensure_directories(self) -> None:
        """Create all standard directories if they do not yet exist."""
        dirs = [
            self.downloads_path,
            self.processed_data_path,
            self.images_path,
            self.reports_path,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
