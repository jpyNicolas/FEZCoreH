from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from skimage.color import rgb2hsv

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class IRVALUEHSVCalculator(Base):
    """
    IRVALUEHSV calculator class
    """

    def __init__(self, files: OpenFiles):
        # Check requirment bands
        if (
            files.swir2_band is None
            or files.swir1_band is None
            or files.red_band is None
        ):
            raise Exception("NIR G B bands are require for HSV")
        super().__init__(files)
        # Normalize the bands
        self.normalized_bands = self.files.get_normalize_bands()
        self.irvaluehsv = None

    def calculate(self, extra_params: dict):
        ### is this require you define property class instance of simple variable?
        self.normalized_swir2 = self.normalized_bands["swir2"]
        self.normalized_swir1 = self.normalized_bands["swir1"]
        self.normalized_red = self.normalized_bands["red"]

        image_irimg = np.dstack(
            (self.normalized_swir2, self.normalized_swir1, self.normalized_red)
        )

        irhsv = rgb2hsv(image_irimg)
        self.irvaluehsv = irhsv[:, :, 2]
        # Remove this return when you complete the export
        return self.irvaluehsv

    def export(self, file_path: Path, title: str):
        # complete this section
        plt.figure(figsize=(20, 10))
        plt.title(title)
        plt.imshow(self.irvaluehsv)
        plt.grid(True)
        plt.colorbar()
        plt.savefig(file_path)
        plt.close()


# Export (on test mode)
if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"
    red = Path.cwd() / "app/openrs/data/Red.tif"
    green = Path.cwd() / "app/openrs/data/Green.tif"
    blue = Path.cwd() / "app/openrs/data/Blue.tif"
    swir1 = Path.cwd() / "app/openrs/data/SWIR1.tif"
    swir2 = Path.cwd() / "app/openrs/data/SWIR2.tif"

    calculator = IRVALUEHSVCalculator(
        OpenFiles(swir1_path=swir1, swir2_path=swir2, red_path=red)
    )
    irvaluehsv = calculator.calculate()
    plt.figure(figsize=(20, 10))
    plt.imshow(irvaluehsv)
    plt.colorbar()
    plt.show()
