### Support Vector Machine

# Import libraries


import itertools
from pathlib import Path

import pandas as pd
from skimage import io

# Import modules
from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


# SVM class
class SVMCalculator(Base):
    def __init__(self, files: OpenFiles):
        if (
            files.red_band is None
            or files.green_band is None
            or files.blue_band is None
        ):
            raise Exception("RGB band are require to calculate SVM")
        super().__init__(files)
        self.normalized_bands = self.files.get_normalize_bands()
        self.svm = None
        self.blue_metadata = self.files.get_images_metadata()["blue"]

        self.class_num = 4
        self.sample_num = 10

        self.collection_data = self.files.get_collection()

    def calculate(self, extra_params: dict):

        # # Extract image collections from the files
        imgcol = self.files.__dict__
        imgcol_filtered = []

        for key, value in imgcol.items():  # Iterate over both keys and values
            if "band" in key:  # Check if "band" is in the attribute name (key)
                imgcol_filtered.append(value)  # Append the actual value

        all_images = io.concatenate_images(self.collection_data).transpose()
        all_image_reshape = all_images.reshape(
            (
                self.blue_metadata["height"] * self.blue_metadata["width"],
                len(self.collection_data),
            )
        )

        columns = ["Band{}".format(i + 1) for i in range(len(self.collection_data))]
        classes_df = pd.DataFrame(columns=columns)

        targets = [[i + 1] * self.sample_num for i in range(self.class_num)]
        merged = list(itertools.chain(*targets))
        classes_df["Target"] = merged

    def export(self, export_func, **kwargs):
        pass


if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"
    red = Path.cwd() / "app/openrs/data/Red.tif"
    green = Path.cwd() / "app/openrs/data/Green.tif"
    blue = Path.cwd() / "app/openrs/data/Blue.tif"
    swir1 = Path.cwd() / "app/openrs/data/SWIR1.tif"
    swir2 = Path.cwd() / "app/openrs/data/SWIR2.tif"

    svm_instance = SVMCalculator(
        OpenFiles(
            red_path=red,
            green_path=green,
            blue_path=blue,
            nir_path=nir,
            swir1_path=swir1,
            swir2_path=swir2,
        )
    )
    svm_instance.calculate()
