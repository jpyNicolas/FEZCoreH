import uuid
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.operation import OperationCrud
from app.models import Project
from app.openrs.base import Base as OpenrsBase
from app.openrs.file_handler import OpenFiles
from app.openrs.filters.gaussian import GAUSSIANCalculator
from app.openrs.filters.laplacian import LAPLACIANCalculator
from app.openrs.filters.mean import MEANCalculator
from app.openrs.filters.median import MEDIANCalculator
from app.openrs.filters.sobel import SOBELCalculator
from app.openrs.hsv.hsv import HSVCalculator
from app.openrs.hsv.hue import HUECalculator
from app.openrs.hsv.irhsv import IRHSVCalculator
from app.openrs.hsv.irhue import IRHUECalculator
from app.openrs.hsv.irsaturation import IRSATURATIONCalculator
from app.openrs.hsv.irvaluehsv import IRVALUEHSVCalculator
from app.openrs.hsv.saturation import SATURATIONCalculator
from app.openrs.hsv.valuehsv import VALUEHSVCalculator
from app.openrs.image_enhancement.adaptive_image import ADAPTIVEIMAGECalculator
from app.openrs.image_enhancement.equalize_image import EQUALIZEIMAGECalculator
from app.openrs.image_enhancement.float_image import FLOATIMAGECaculator
from app.openrs.image_enhancement.gamma_image import GAMMAIMAGECalculator
from app.openrs.image_enhancement.log_adjust import LOGADJUSTCalculator
from app.openrs.image_enhancement.original_image import ORGINALIMAGECalculator
from app.openrs.image_enhancement.rgb_adaptive_image import RGBADAPTIVEIMAGECalculator
from app.openrs.image_enhancement.rgb_equalize_image import RGBEQUALIZEIMAGECalculator
from app.openrs.image_enhancement.rgb_gamma_image import RGBGAMMAIMAGECalculator
from app.openrs.image_enhancement.rgb_image import RGBIMAGECalculator
from app.openrs.image_enhancement.sigmoid_adjust import SIGMODIDADJUSTCalculator
from app.openrs.kmeans.kmeans import KMEANSCalculator
from app.openrs.pca.pca import PCACalculator
from app.openrs.spectral_indices.afvi import AFVICalculator
from app.openrs.spectral_indices.bi import BICalculator
from app.openrs.spectral_indices.ndvi import NDVICalculator
from app.openrs.spectral_indices.ndwi import NDWICalculator
from app.openrs.spectral_indices.savi import SAVICalculator
from app.openrs.spectral_indices.ui import UICalculator
from app.openrs.spectral_profile.spectral_profile import SpectralProfile
from app.schemas import Bands
from app.services.file import FileService

allowed_operation_types = {
    # SI
    "ndvi": NDVICalculator,
    "ndwi": NDWICalculator,
    "afvi": AFVICalculator,
    "bi": BICalculator,
    "savi": SAVICalculator,
    "ui": UICalculator,
    # PCA
    "pca": PCACalculator,
    # SP
    "spectral_profile": SpectralProfile,
    # HSV
    "hsv": HSVCalculator,
    "irhsv": IRHSVCalculator,
    "hue": HUECalculator,
    "irhue": IRHUECalculator,
    "saturation": SATURATIONCalculator,
    "valuehsv": VALUEHSVCalculator,
    "valueirhsv": IRVALUEHSVCalculator,
    "irsaturation": IRSATURATIONCalculator,
    # Kmeans
    "clustering": KMEANSCalculator,
    "mean": MEANCalculator,
    # Filters
    "gaussian": GAUSSIANCalculator,
    "laplacian": LAPLACIANCalculator,
    "median": MEDIANCalculator,
    "sobel": SOBELCalculator,
    # Image Enhancement
    "adaptive_image": ADAPTIVEIMAGECalculator,
    "float_image": FLOATIMAGECaculator,
    "gamma_image": GAMMAIMAGECalculator,
    "log_adjust": LOGADJUSTCalculator,
    "orginal_image": ORGINALIMAGECalculator,
    "sigmodid": SIGMODIDADJUSTCalculator,
    "equalize_image": EQUALIZEIMAGECalculator,
    "rgb_adaptive_image": RGBADAPTIVEIMAGECalculator,
    "rgb_image": RGBIMAGECalculator,
    "rgb_equalize_image": RGBEQUALIZEIMAGECalculator,
    "rgb_gamma_image": RGBGAMMAIMAGECalculator,
}


class Operation:
    def __init__(self, db: Session):
        self.db = db

    def operate(
        self,
        bands: Bands,
        tif_file: int | None,
        operation_type: str,
        title: str,
        project: Project,
        extra_params: dict | None,
    ):

        if operation_type not in allowed_operation_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation type {operation_type} not allowed",
            )

        project_files_id = {file.id for file in project.files}
        if res := set(bands.model_dump(exclude_unset=True).values()) - project_files_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Files with id's {res} not found",
            )

        file_service = FileService(self.db)

        files_dict = {
            "red_path": (
                file_service.get(bands.red_band, project) if bands.red_band else None
            ),
            "blue_path": (
                file_service.get(bands.blue_band, project) if bands.blue_band else None
            ),
            "green_path": (
                file_service.get(bands.green_band, project)
                if bands.green_band
                else None
            ),
            "nir_path": (
                file_service.get(bands.nir_band, project) if bands.nir_band else None
            ),
            "swir1_path": (
                file_service.get(bands.swir1_band, project)
                if bands.swir1_band
                else None
            ),
            "swir2_path": (
                file_service.get(bands.swir2_band, project)
                if bands.swir2_band
                else None
            ),
            "tif_file": (file_service.get(tif_file, project) if tif_file else None),
        }

        openrs_base_class = allowed_operation_types[operation_type]
        openrs_instance: OpenrsBase = openrs_base_class(OpenFiles(**files_dict))
        openrs_instance.calculate(extra_params)

        export_unique_filename = uuid.uuid4()

        save_path = (
            Path(settings.local_save_files) / f"images/{export_unique_filename}.png"
        )
        openrs_instance.export(save_path, title=title)

        file_model = file_service.create_operation_output(
            file_path=save_path,
            extension="png",
            unique_name=export_unique_filename,
            title=title,
            project=project,
        )

        return file_model

    def delete_operation_output(self, _id: int):
        operation_output = OperationCrud.get(db=self.db, _id=_id)

        if operation_output is None:
            raise HTTPException(
                detail=f"Operation file does not exist with {_id} id",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        operation_output.deleted_at = datetime.now()

        operation_output = OperationCrud.update(db=self.db, file=operation_output)

        return operation_output
