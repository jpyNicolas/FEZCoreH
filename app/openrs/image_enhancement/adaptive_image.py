from pathlib import Path

from fastapi import HTTPException, status
from matplotlib import pyplot as plt
from pydantic import BaseModel, ValidationError, confloat
from skimage import exposure, img_as_float

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class AdaptiveImageType(BaseModel):
    clip_limit: confloat(gt=0.0, le=1.0) = 0.9  # Ensure clip_limit is between 0 and 1

    class Config:
        schema_extra = {
            "example": {
                "clip_limit": 0.9,
            }
        }


class ADAPTIVEIMAGECalculator(Base):
    def __init__(self, files: OpenFiles) -> None:
        if files.nir_band is None:
            raise HTTPException(
                detail="NIR band are require to calculate Image enhancement (adaptive image)",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )

        super().__init__(files)
        self.nir_band = self.files.nir_metadata["skimage"]

    def calculate(self, extra_params):
        # Validation extra parameters
        try:
            validated_params = AdaptiveImageType(**extra_params)
        except ValidationError as e:
            raise HTTPException(
                detail=f"Invalid parameters: {e}",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )
        # End validation extra parameters

        clip_limit = validated_params.clip_limit
        nbins = 256
        float_image = img_as_float(self.nir_band)
        adaptive_image = exposure.equalize_adapthist(
            float_image, clip_limit=clip_limit, nbins=nbins
        )
        self.adaptive_image = adaptive_image

        return adaptive_image

    def export(self, file_path, title):
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
        ax[0].imshow(self.adaptive_image, cmap="gray")
        ax[0].set_title(f"Adaptive Image {title}")
        ax[0].axis("off")
        ax[1].hist(
            self.adaptive_image.ravel(),
            bins=256,
            density=True,
            histtype="bar",
            color="black",
        )
        ax[1].ticklabel_format(style="plain")
        ax[1].set_title(f"Histogram of Adaptive Image {title}")

        # plt.show()
        plt.savefig(file_path)
        plt.close()


# This condition is for test output of operation calculator class
if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"

    calculator = ADAPTIVEIMAGECalculator(
        OpenFiles(
            nir_path=nir,
        )
    )
    imageenhancement = calculator.calculate({"clip_limit": 0.9})
    calculator.export("imageenhancement", "export")
