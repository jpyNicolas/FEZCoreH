from pathlib import Path

from matplotlib import pyplot as plt

from app.openrs.base import Base
from app.openrs.exceptions.OException import OException
from app.openrs.export import PlotExport
from app.openrs.file_handler import OpenFiles


class NDVICalculator(Base):
    """A class to calculate the Normalized Difference Vegetation Index (NDVI)."""

    def __init__(self, files: OpenFiles):
        if files.red_band is None or files.nir_band is None:
            raise Exception("Both NIR and Red bands are required")
        super().__init__(files)
        self.normalized_bands = self.files.get_normalize_bands()
        self.ndvi = None

    def calculate(self, extra_params: dict):
        self.normalized_red = self.normalized_bands["red"]
        self.normalized_nir = self.normalized_bands["nir"]
        self.ndvi = (self.normalized_nir - self.normalized_red) / (
            self.normalized_nir + self.normalized_red
        )
        return self.ndvi

    def export(self, file_path: Path, title: str):
        if self.ndvi is None:
            raise OException("NDVI has not been calculated. Call 'calculate' first.")

        plt.figure(figsize=(15, 10))
        plt.imshow(self.ndvi, cmap="gray")
        plt.title(title)
        plt.colorbar()
        plt.axis("off")
        plt.savefig(file_path)
        plt.show()
        plt.close()


if __name__ == "__main__":
    nir_path = Path.cwd() / "app/openrs/data/NIR.tif"
    red_path = Path.cwd() / "app/openrs/data/Red.tif"

    calculator = NDVICalculator(OpenFiles(red_path=red_path, nir_path=nir_path))
    ndvi = calculator.calculate()
    plot_export = PlotExport()
    calculator.export(file_path="./", title="NDVI Image")
