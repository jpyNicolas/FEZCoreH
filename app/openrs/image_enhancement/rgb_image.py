from pathlib import Path

import numpy as np
from fastapi import HTTPException, status
from matplotlib import pyplot as plt

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class RGBIMAGECalculator(Base):
    def __init__(self, files: OpenFiles) -> None:
        if (
            files.blue_band is None
            or files.red_band is None
            or files.green_band is None
        ):
            raise HTTPException(
                detail="BLUE/RED/GREEN bands are require to calculate Image enhancement (rgb orginal image)",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )

        super().__init__(files)
        self.red_band = self.files.red_metadata["skimage"]
        self.blue_band = self.files.blue_metadata["skimage"]
        self.green_band = self.files.green_metadata["skimage"]

    def calculate(self, extra_params):
        red_band = np.array(self.red_band).astype(float)
        blue_band = np.array(self.blue_band).astype(float)
        green_band = np.array(self.green_band).astype(float)

        blue_band_normalize = (blue_band - np.min(blue_band)) / (
            np.max(blue_band) - np.min(blue_band)
        )
        green_band_normalize = (green_band - np.min(green_band)) / (
            np.max(green_band) - np.min(green_band)
        )
        red_band_normalize = (red_band - np.min(red_band)) / (
            np.max(red_band) - np.min(red_band)
        )

        rgb_nstack = np.stack(
            [red_band_normalize, green_band_normalize, blue_band_normalize], axis=2
        )

        self.rgb_nstack = rgb_nstack

    def export(self, file_path, title):
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
        ax[0].imshow(self.rgb_nstack, cmap="gray")
        ax[0].set_title(f"Equalize RGB {title}")
        ax[0].axis("off")
        ax[1].hist(
            self.rgb_nstack.ravel(),
            bins=256,
            density=True,
            histtype="bar",
            color="black",
        )
        ax[1].ticklabel_format(style="plain")
        ax[1].set_title(f"Histogram of Equalize RGB {title}")
        # plt.show()
        plt.savefig(file_path)
        plt.close()


# This condition is for test output of operation calculator class
if __name__ == "__main__":
    red = Path.cwd() / "app/openrs/data/Red.tif"
    green = Path.cwd() / "app/openrs/data/Green.tif"
    blue = Path.cwd() / "app/openrs/data/Blue.tif"

    calculator = RGBIMAGECalculator(
        OpenFiles(
            red_path=red,
            green_path=green,
            blue_path=blue,
        )
    )
    imageenhancement = calculator.calculate(None)
    calculator.export("imageenhancement", "export")
