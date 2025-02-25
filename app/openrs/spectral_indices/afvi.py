from pathlib import Path

from matplotlib import pyplot as plt

from app.openrs.base import Base
from app.openrs.exceptions.OException import OException
from app.openrs.export import PlotExport
from app.openrs.file_handler import OpenFiles


class AFVICalculator(Base):
    """A class to calculate the Normalized Difference Vegetation Index (NDVI)."""

    def __init__(self, files: OpenFiles):
        if files.swir1_band is None or files.nir_band is None:
            raise Exception("Both NIR and Swir1 bands are required")
        super().__init__(files)
        self.normalized_bands = self.files.get_normalize_bands()
        self.afvi = None

    def calculate(self, extra_params: dict):
        normalized_swir1 = self.normalized_bands["swir1"]
        normalized_nir = self.normalized_bands["nir"]
        self.afvi = (normalized_nir - 0.66) * (
            normalized_swir1 / (normalized_nir + (0.66 * normalized_swir1))
        )
        return self.afvi

    def export(self, file_path: Path, title: str):
        if self.afvi is None:
            raise OException("NDWI has not been calculated. Call 'calculate' first.")

        plt.figure(figsize=(15, 10))
        plt.imshow(self.afvi, cmap="gray")
        plt.title(title)
        plt.colorbar()
        plt.axis("off")
        plt.savefig(file_path)
        plt.close()


if __name__ == "__main__":
    nir_path = Path.cwd() / "app/openrs/data/NIR(1).tif"
    swir1_path = Path.cwd() / "app/openrs/data/SWIR1.tif"

    calculator = AFVICalculator(OpenFiles(swir1_path=swir1_path, nir_path=nir_path))
    ndvi = calculator.calculate()
    plot_export = PlotExport()
    calculator.export("hello", "world")
