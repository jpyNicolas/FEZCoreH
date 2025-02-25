from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skimage import exposure

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class SpectralProfile(Base):
    def __init__(self, files: OpenFiles):
        """
        Initialize the SpectralProfile with image files.

        :param files: An instance of OpenFiles containing image data.
        """
        super().__init__(files)
        self.files = files
        self.img = None
        self.xaxis = []
        self.yaxis = []

    def calculate(self, extra_params: dict):
        """
        Calculate the spectral profile by adjusting the logarithmic scale
        of a specific image band and preparing data for plotting.
        """
        # # Extract image collections from the files
        imgcol = self.files.__dict__
        imgcol_filtered = []

        for key, value in imgcol.items():  # Iterate over both keys and values
            if "band" in key:  # Check if "band" is in the attribute name (key)
                imgcol_filtered.append(value)  # Append the actual value

        # Ensure imgcol[4] is within bounds and valid
        if len(imgcol_filtered) > 4 and isinstance(imgcol_filtered[4], np.ndarray):
            self.img = exposure.adjust_log(imgcol_filtered[4])
        else:
            raise ValueError("Invalid image data at index 4.")

        # Prepare x and y axis data for plotting
        for i, img in enumerate(imgcol_filtered):
            self.xaxis.append(f"Band{i + 1}")
            self.yaxis.append(np.mean(img))

    def export(self, file_path: Path, title: str):
        """
        Export the calculated spectral profile as a plot.
        """
        plt.figure(figsize=(15, 10))
        plt.plot(self.xaxis, self.yaxis)
        plt.title(title)
        plt.xlabel("Bands")
        plt.ylabel("Intensity")
        plt.grid(True)
        plt.savefig(file_path)
        plt.close()


if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"
    red = Path.cwd() / "app/openrs/data/Red.tif"
    green = Path.cwd() / "app/openrs/data/Green.tif"
    blue = Path.cwd() / "app/openrs/data/Blue.tif"
    swir1 = Path.cwd() / "app/openrs/data/SWIR1.tif"
    swir2 = Path.cwd() / "app/openrs/data/SWIR2.tif"

    calculator = SpectralProfile(
        OpenFiles(
            nir_path=nir,
            red_path=red,
            blue_path=blue,
            green_path=green,
            swir1_path=swir1,
            swir2_path=swir2,
        )
    )
    ndvi = calculator.calculate()
    calculator.export("spectral_profile", "export")
