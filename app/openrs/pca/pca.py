from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from skimage import io
from sklearn.decomposition import PCA as skpc

from app.openrs.base import Base
from app.openrs.exceptions.OException import OException
from app.openrs.file_handler import OpenFiles


class PCACalculator(Base):
    def __init__(self, files: OpenFiles):
        super().__init__(files)
        self.pcas = None  # Initialize as None until calculated
        self.image_shape = (files.red_metadata["width"], files.red_metadata["height"])

    def calculate(self, extra_params: dict):
        imgcol_filtered = self.files.get_collection()
        images = []
        for i in range(len(imgcol_filtered)):
            images.append(imgcol_filtered[i].flatten())
        images = np.array(images)
        pca = skpc(n_components=6)  # Specify the number of components
        pca.fit(images)
        self.pcas = pca.components_[:6]  # Store the first 6 components
        return self.pcas

    def export(self, file_path: Path, title: str):
        if self.pcas is None:
            raise OException("PCA has not been calculated. Call 'calculate' first.")

        fig, ax = plt.subplots(nrows=6, ncols=2, figsize=(20, 30))
        plt.title(title)
        for i, pca_component in enumerate(self.pcas):
            reshaped_component = pca_component.reshape(self.image_shape)
            ax[i, 0].imshow(reshaped_component, cmap="gray")
            ax[i, 0].set_title(f"PCA Band {i + 1}")
            ax[i, 0].axis("off")
            ax[i, 1].hist(
                pca_component.ravel(),
                bins=256,
                density=True,
                histtype="bar",
                color="black",
            )
            ax[i, 1].set_title(f"Histogram of PCA Band {i + 1}")
        plt.savefig(file_path)
        plt.close()

        # labels = ['point {0}'.format(i + 1) for i in range(10)]
        # tooltip = mpld3.plugins.PointLabelTooltip(ax[0], labels=labels)
        # mpld3.plugins.connect(fig, tooltip)
        # t1 = time.perf_counter()
        # t2 = time.perf_counter()
        # print(t2 - t1)
        # yield mpld3.fig_to_html(fig)


if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"
    red = Path.cwd() / "app/openrs/data/Red.tif"
    green = Path.cwd() / "app/openrs/data/Green.tif"
    blue = Path.cwd() / "app/openrs/data/Blue.tif"
    swir1 = Path.cwd() / "app/openrs/data/SWIR1.tif"
    swir2 = Path.cwd() / "app/openrs/data/SWIR2.tif"

    example_image = io.imread(red)
    image_shape = example_image.shape
    calculator = PCACalculator(
        OpenFiles(
            nir_path=nir,
            red_path=red,
            blue_path=blue,
            green_path=green,
            swir1_path=swir1,
            swir2_path=swir2,
        ),
    )
    ndvi = calculator.calculate(None)

    # plot_export = PlotExport()
    # calculator.export(export_func=plot_export.show, title="NDVI Image")
    # calculator.show_pca_components()
    calculator.export("hello.png", "hello")
