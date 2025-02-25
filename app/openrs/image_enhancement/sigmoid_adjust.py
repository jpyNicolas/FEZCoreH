from pathlib import Path

from fastapi import HTTPException, status
from matplotlib import pyplot as plt
from skimage import exposure, img_as_float

from app.openrs.base import Base
from app.openrs.file_handler import OpenFiles


class SIGMODIDADJUSTCalculator(Base):
    def __init__(self, files: OpenFiles) -> None:
        if files.nir_band is None:
            raise HTTPException(
                detail="NIR band are require to calculate Image enhancement (log adjust)",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )

        super().__init__(files)
        self.nir_band = self.files.nir_metadata["skimage"]

    def calculate(self, extra_params):
        # Validation extra parameters
        if extra_params is None and type(extra_params) is not dict:
            raise HTTPException(
                detail="you should send value of (gain and inv and cutoff), these params are required",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )
        if (
            extra_params.get("gain") is None
            or extra_params.get("inv") is None
            or extra_params.get("cutoff") is None
        ):
            raise HTTPException(
                detail="The (gain and inv) values can not be empty",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )

        if (
            type(extra_params["gain"]) is not int
            and type(extra_params["inv"]) is not bool
            and type(extra_params["cutoff"]) is not float
        ):
            raise HTTPException(
                detail="The gain value should be number, and inv value should be true or false (boolean)",
                status_code=status.HTTP_412_PRECONDITION_FAILED,
            )
        # End validation extra parameters

        gain = extra_params["gain"]
        inv = extra_params["inv"]
        cutoff = extra_params["cutoff"]

        float_image = img_as_float(self.nir_band)
        sigmoid_adjust = exposure.adjust_sigmoid(
            float_image, cutoff=cutoff, gain=gain, inv=inv
        )
        self.sigmoid_adjust = sigmoid_adjust

        return sigmoid_adjust

    def export(self, file_path, title):
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
        ax[0].imshow(self.sigmoid_adjust, cmap="gray")
        ax[0].set_title(f"Log Adjust {title}")
        ax[0].axis("off")
        ax[1].hist(
            self.sigmoid_adjust.ravel(),
            bins=256,
            density=True,
            histtype="bar",
            color="black",
        )
        ax[1].ticklabel_format(style="plain")
        ax[1].set_title(f"Histogram of Log Adjust {title}")
        # plt.show()
        plt.savefig(file_path)
        plt.close()


# This condition is for test output of operation calculator class
if __name__ == "__main__":
    nir = Path.cwd() / "app/openrs/data/NIR.tif"

    calculator = SIGMODIDADJUSTCalculator(
        OpenFiles(
            nir_path=nir,
        )
    )
    imageenhancement = calculator.calculate({"inv": True, "gain": 5, "cutoff": 0.1})
    calculator.export("imageenhancement", "export")
