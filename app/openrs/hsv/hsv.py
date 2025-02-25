from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from skimage.color import rgb2hsv

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class HSVCalculator(Base):
    """
    HSV calculator class
    To Whoman (please refactor and complete the export method, you can test the calculator method with below IF condition
    And remeber to remove the 'return' from calculate method)
    """

    def __init__(self, files: OpenFiles):
        # Check requirment bands
        if (
            files.nir_band is None
            or files.green_band is None
            or files.blue_band is None
        ):
            raise Exception("NIR G B bands are require for HSV")
        super().__init__(files)
        # Normalize the bands
        self.normalized_bands = self.files.get_normalize_bands()
        self.hsv = None

    def calculate(self, extra_params: dict):
        ### is this require you define property class instance of simple variable?
        self.normalized_nir = self.normalized_bands["nir"]
        self.normalized_green = self.normalized_bands["green"]
        self.normalized_blue = self.normalized_bands["blue"]

        image_hsv = np.dstack(
            (self.normalized_nir, self.normalized_green, self.normalized_blue)
        )

        hsv = rgb2hsv(image_hsv)
        self.hsv = hsv
        # Remove this return when you complete the export
        return hsv

    def export(self, file_path: Path, title: str):
        # complete this section
        plt.figure(figsize=(20, 10))
        plt.title(title)
        plt.imshow(self.hsv)
        plt.grid(True)
        plt.colorbar()
        plt.savefig(file_path)
        plt.close()


# Export (on test mode)
if __name__ == "__main__":
    nir_path = Path.cwd() / "app/openrs/data/NIR.tif"
    green_path = Path.cwd() / "app/openrs/data/Green.tif"
    blue_path = Path.cwd() / "app/openrs/data/Blue.tif"

    calculator = HSVCalculator(
        OpenFiles(nir_path=nir_path, green_path=green_path, blue_path=blue_path)
    )
    hsv = calculator.calculate()
    plt.figure(figsize=(20, 10))
    plt.imshow(hsv)
    plt.colorbar()
    plt.show()
