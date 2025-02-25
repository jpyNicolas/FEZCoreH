from pathlib import Path

import matplotlib.pyplot as plt
from skimage import img_as_float

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class FLOATIMAGECaculator(Base):
    def __init__(self, files: OpenFiles):
        if files.nir_band is None:
            raise Exception("NIR band are require to calculate Image enhancement")

        super().__init__(files)
        self.nir_band = self.files.nir_metadata["skimage"]

    def calculate(self, extra_params):
        self.float_image = img_as_float(self.nir_band)

    def export(self, file_path, title):
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
        ax[0].imshow(self.float_image, cmap="gray")
        ax[0].set_title(f"Float Image {title}")
        ax[0].axis("off")
        ax[1].hist(
            self.float_image.ravel(),
            bins=256,
            density=True,
            histtype="bar",
            color="black",
        )
        ax[1].ticklabel_format(style="plain")
        ax[1].set_title(f"Histogram of Float Image {title}")
        # plt.show()
        plt.savefig(file_path)
        plt.close()


if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"

    calculator = FLOATIMAGECaculator(
        OpenFiles(
            nir_path=nir,
        )
    )
    imageenhancement = calculator.calculate(None)
    calculator.export("imageenhancement", "export")
