from pathlib import Path

import matplotlib.pyplot as plt

# from skimage import io
from fastapi import HTTPException, status

# Libraries and dependencies
from sklearn.cluster import KMeans

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class KMEANSCalculator(Base):
    """
    KMEANS calculator class
    K-means clustering provide unsupervised division of samples into different groups reflecting relative contents of detrital (siliciclastic-volcaniclastic),
    biogenic and hydrothermal components in the marble protoliths.
    """

    def __init__(self, files: OpenFiles):
        # Check requirment bands
        if files.nir_band is None:
            raise Exception("NIR band is require for Kmeans")
        super().__init__(files)
        # Normalize the bands
        self.normalized_bands = self.files.get_normalize_bands()
        self.nir_band_metadata = self.files.nir_metadata
        self.nir = self.files.nir_band
        self.kmeans = None

    def calculate(self, extra_params: dict) -> any:
        # Validation extra parameters
        if extra_params is None and type(extra_params) is not dict:
            raise HTTPException(
                detail="you should send value of (n_clusters and random_state), these params are required",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )
        if (
            extra_params.get("n_clusters") is None
            or extra_params.get("random_state") is None
        ):
            raise HTTPException(
                detail="The n_clusters and random_state value cant be empty",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )

        if type(extra_params["n_clusters"]) is not int:
            raise HTTPException(
                detail="The n_clusters value should be number",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )

        if extra_params["n_clusters"] <= 0:
            raise HTTPException(
                detail="The n_clusters value should be number greater that 0",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )

        if extra_params["random_state"] < 0 or extra_params["random_state"] > 42:
            raise HTTPException(
                detail="The random_state value should be between 0 - 42",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )
        # End validation extra parameters

        image_reshape = self.nir.reshape(
            self.nir_band_metadata["width"] * self.nir_band_metadata["height"], 1
        )

        # Define the number of clusters (you can change this number depending on your needs)
        # These variables are extra parameters
        n_clusters = extra_params["n_clusters"]
        random_state = extra_params["random_state"]

        # Initialize and fit the KMeans model
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
        kmeans.fit(image_reshape)

        # Get cluster centers and labels
        cluster_centers = kmeans.cluster_centers_
        cluster_labels = kmeans.labels_

        # Reshape the clustered labels back into the image dimensions
        clusterd_image = cluster_centers[cluster_labels].reshape(
            self.nir_band_metadata["height"], self.nir_band_metadata["width"]
        )

        self.kmeans = clusterd_image

        return self.kmeans

    def export(self, file_path, title) -> any:
        plt.figure(figsize=(15, 15))
        plt.title(title)
        plt.imshow(self.kmeans)
        plt.axis("off")
        plt.savefig(file_path)
        # plt.show()
        plt.close()


if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"
    red = Path.cwd() / "app/openrs/data/Red.tif"
    green = Path.cwd() / "app/openrs/data/Green.tif"
    blue = Path.cwd() / "app/openrs/data/Blue.tif"
    swir1 = Path.cwd() / "app/openrs/data/SWIR1.tif"
    swir2 = Path.cwd() / "app/openrs/data/SWIR2.tif"

    calculator = KMEANSCalculator(
        OpenFiles(
            nir_path=nir,
            red_path=red,
            blue_path=blue,
            green_path=green,
            swir1_path=swir1,
            swir2_path=swir2,
        )
    )
    kmeans = calculator.calculate(4, 0)

    plt.figure(figsize=(15, 15))
    plt.imshow(kmeans)
    plt.axis("off")
    plt.show()
