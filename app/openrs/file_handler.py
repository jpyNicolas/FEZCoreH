import os

import matplotlib.pyplot as plt
import numpy as np
from skimage import io


def _load_image(path: str) -> np.ndarray | None:
    if not path:
        return None
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} not found")
    return io.imread(path).astype(float)


def _data_image(path: str | None) -> dict | None:
    if path:
        image = plt.imread(path)
        image_skimage = io.imread(path)
        return {
            "image": image,
            "skimage": image_skimage,
            "height": image.shape[0],
            "width": image.shape[1],
            # "channels": image.shape[2] | None,
        }
    else:
        return {}


def _normalize(image: np.ndarray) -> np.ndarray | None:
    if image is None:
        return None
    return (image - np.min(image)) / (np.max(image) - np.min(image))


class OpenFiles:
    def __init__(
        self,
        red_path: str | None = None,
        green_path: str | None = None,
        blue_path: str | None = None,
        nir_path: str | None = None,
        swir1_path: str | None = None,
        swir2_path: str | None = None,
        tif_file: str | None = None,
    ):
        self.blue_band = _load_image(blue_path)
        self.green_band = _load_image(green_path)
        self.nir_band = _load_image(nir_path)
        self.red_band = _load_image(red_path)
        self.swir1_band = _load_image(swir1_path)
        self.swir2_band = _load_image(swir2_path)
        self.tif_file = _load_image(tif_file)

        self.blue_metadata = _data_image(blue_path)
        self.green_metadata = _data_image(green_path)
        self.nir_metadata = _data_image(nir_path)
        self.red_metadata = _data_image(red_path)
        self.swir1_metadata = _data_image(swir1_path)
        self.swir2_metadata = _data_image(swir2_path)
        self.tif_file_metadata = _data_image(tif_file)

        self.files_path = [
            blue_path,
            green_path,
            nir_path,
            red_path,
            swir1_path,
            swir2_path,
        ]

    def get_normalize_bands(self) -> dict[str, np.ndarray]:
        return {
            "red": _normalize(self.red_band),
            "green": _normalize(self.green_band),
            "blue": _normalize(self.blue_band),
            "nir": _normalize(self.nir_band),
            "swir1": _normalize(self.swir1_band),
            "swir2": _normalize(self.swir2_band),
            "tif_file": _normalize(self.tif_file),
        }

    def get_images_metadata(self) -> dict:
        return {
            "blue": self.blue_metadata,
            "green": self.green_metadata,
            "nir": self.nir_metadata,
            "red": self.red_metadata,
            "swir1": self.swir1_metadata,
            "swir2": self.swir2_metadata,
            "tif_file": self.tif_file_metadata,
        }

    def get_collection(self) -> any:
        return io.imread_collection(self.files_path)
