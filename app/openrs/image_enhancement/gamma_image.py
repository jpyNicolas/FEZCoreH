from pathlib import Path

import matplotlib.pyplot as plt
from skimage import exposure, img_as_float

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class GAMMAIMAGECalculator(Base):
    def __init__(self, files: OpenFiles):
        if files.nir_band is None:
            raise Exception("NIR band are require to calculate Image enhancement")

        super().__init__(files)
        self.nir_band = self.files.nir_metadata["skimage"]
        self.nir_band_float = img_as_float(self.nir_band)

    def calculate(self, extra_params):
        gamma = extra_params["gamma"]
        gain = extra_params["gain"]
        gamma_image = exposure.adjust_gamma(self.nir_band_float, gamma=gamma, gain=gain)
        while self.nir_band_float.mean() < gamma_image.mean():
            gamma = gamma + 0.2
            gamma_image = exposure.adjust_gamma(
                self.nir_band_float, gamma=gamma, gain=gain
            )

        self.gamma_image = gamma_image
        return gamma_image

    def export(self, file_path, title):
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
        ax[0].imshow(self.gamma_image, cmap="gray")
        ax[0].set_title(f"Gamma Image {title}")
        ax[0].axis("off")
        ax[1].hist(
            self.gamma_image.ravel(),
            density=True,
            bins=256,
            histtype="bar",
            color="black",
        )
        ax[1].ticklabel_format(style="plain")
        ax[1].set_title(f"Histogram of Gamma Image {title}")
        # plt.show()
        plt.savefig(file_path)
        plt.close()


if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"

    calculator = GAMMAIMAGECalculator(
        OpenFiles(
            nir_path=nir,
        )
    )
    imageenhancement = calculator.calculate({"gamma": 0.2, "gain": 1})
    calculator.export("imageenhancement", "export")
