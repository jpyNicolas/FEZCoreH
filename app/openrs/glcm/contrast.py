from pathlib import Path

import matplotlib.pyplot as plt

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class CONSTRASTCalculator(Base):
    def __init__(self, files: OpenFiles):
        if files.nir_band is None:
            raise Exception("The nir band is require for GLCM")
        super().__init__(files)

    def calculate(self, extra_params):
        pass

    def export(self, file_path, title):
        pass


if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"

    calculator = CONSTRASTCalculator(
        OpenFiles(
            nir_path=nir,
        )
    )
    contrast = calculator.calculate(None)
    plt.figure(figsize=(15, 15))
    plt.imshow(contrast)
    plt.show()
