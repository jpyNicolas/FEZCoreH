from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from skimage import img_as_float

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class ORGINALIMAGECalculator(Base):
    def __init__(self, files: OpenFiles):
        if files.nir_band is None:
            raise Exception("NIR band are require to calculate Image enhancement")

        super().__init__(files)

        self.nir_band = self.files.nir_metadata["skimage"]

    def calculate(self, extra_params):
        self.image_float = img_as_float(self.nir_band)
        return self.image_float

    def export(self, file_path, title):
        fig = plt.figure(figsize=(10, 5))
        gs = GridSpec(
            1, 2, width_ratios=[1, 1], height_ratios=[2]
        )  # Adjust height ratios if needed

        # Display the original image
        ax0 = fig.add_subplot(gs[0, 0])
        ax0.imshow(self.nir_band, cmap="gray")
        ax0.set_title("Original Image")
        ax0.axis("off")

        # Histogram of the original image with reduced height
        ax1 = fig.add_subplot(gs[0, 1])
        ax1.hist(
            self.nir_band.ravel(), bins=256, density=True, histtype="bar", color="black"
        )
        ax1.ticklabel_format(style="plain")
        ax1.set_title("Histogram of Original Image")

        # plt.show()
        plt.savefig(file_path)
        plt.close()


if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"

    calculator = ORGINALIMAGECalculator(
        OpenFiles(
            nir_path=nir,
        )
    )
    imageenhancement = calculator.calculate(None)
    calculator.export("imageenhancement", "export")
