from pathlib import Path

from matplotlib import pyplot as plt

from app.openrs.base import Base
from app.openrs.exceptions.OException import OException
from app.openrs.export import PlotExport
from app.openrs.file_handler import OpenFiles


class UICalculator(Base):
    """A class to calculate the Normalized Difference Vegetation Index (NDVI)."""

    def __init__(self, files: OpenFiles):
        if files.swir2_band is None or files.nir_band is None:
            raise Exception("Both NIR and Swir2 bands are required")
        super().__init__(files)
        self.normalized_bands = self.files.get_normalize_bands()
        self.ui = None

    def calculate(self, extra_params: dict):
        normalized_swir2 = self.normalized_bands["swir2"]
        normalized_nir = self.normalized_bands["nir"]
        self.ui = (normalized_swir2 - normalized_nir) / (
            normalized_nir + normalized_swir2
        )
        return self.ui

    def export(self, file_path: Path, title: str):
        if self.ui is None:
            raise OException("UI has not been calculated. Call 'calculate' first.")

        plt.figure(figsize=(15, 10))
        plt.imshow(self.ui, cmap="gray")
        plt.title(title)
        plt.colorbar()
        plt.axis("off")
        plt.savefig(file_path)
        plt.close()


if __name__ == "__main__":
    nir_path = Path.cwd() / "app/openrs/data/NIR(1).tif"
    swir2 = Path.cwd() / "app/openrs/data/SWIR2.tif"

    calculator = UICalculator(OpenFiles(swir2_path=swir2, nir_path=nir_path))
    ndvi = calculator.calculate()
    plot_export = PlotExport()
    calculator.export("hello", "world")
