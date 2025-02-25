from pathlib import Path

from matplotlib import pyplot as plt

from app.openrs.base import Base
from app.openrs.exceptions.OException import OException
from app.openrs.export import PlotExport
from app.openrs.file_handler import OpenFiles


class NDWICalculator(Base):
    """A class to calculate the Normalized Difference Vegetation Index (NDVI)."""

    def __init__(self, files: OpenFiles):
        if files.green_band is None or files.nir_band is None:
            raise Exception("Both NIR and Green bands are required")
        super().__init__(files)
        self.normalized_bands = self.files.get_normalize_bands()
        self.ndwi = None

    def calculate(self, extra_params: dict):
        normalized_green = self.normalized_bands["green"]
        normalized_nir = self.normalized_bands["nir"]
        self.ndwi = (normalized_green - normalized_nir) / (
            normalized_nir + normalized_green
        )
        return self.ndwi

    def export(self, file_path: Path, title: str):
        if self.ndwi is None:
            raise OException("NDWI has not been calculated. Call 'calculate' first.")

        plt.figure(figsize=(15, 10))
        plt.imshow(self.ndwi, cmap="gray")
        plt.title(title)
        plt.colorbar()
        plt.axis("off")
        plt.savefig(file_path)
        plt.close()


if __name__ == "__main__":
    nir_path = Path.cwd() / "app/openrs/data/NIR(1).tif"
    green_path = Path.cwd() / "app/openrs/data/Green.tif"

    calculator = NDWICalculator(OpenFiles(green_path=green_path, nir_path=nir_path))
    ndvi = calculator.calculate()
    plot_export = PlotExport()
    calculator.export("hello", "world")
