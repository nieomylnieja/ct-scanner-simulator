from dataclasses import dataclass
from datetime import date, time
from pathlib import Path

import numpy as np
import pandas as pd
from pydicom import dcmread, DataElement
from pydicom.uid import ExplicitVRLittleEndian
from pydicom.dataset import FileDataset, FileMetaDataset
from PIL import Image


@dataclass(init=False)
class PatientData:

    def is_valid(self):
        return self.Age >= 0 and self.Sex and self.Name and self.ID

    Age: int
    Sex: str
    Name: str
    ID: str
    Comments: str


@dataclass(init=False)
class DicomMetadata:

    def __init__(self):
        self.Patient = PatientData()

    def is_valid(self) -> bool:
        return self.Patient.is_valid() and self.Date and self.Time

    Date: date
    Time: time
    Patient: PatientData


def create_dicom(img_path: Path, dicom_dir_path: Path, metadata: DicomMetadata) -> str:
    img = np.array(Image.open(img_path)).astype(np.uint8)
    filename = img_path.name.replace(".jpg", ".dcm", 1)

    # Populate required values for file meta information
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
    file_meta.MediaStorageSOPInstanceUID = "1.2.3"
    file_meta.ImplementationClassUID = "1.2.3.4"
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(filename, {}, file_meta=file_meta, preamble=b"\0" * 128)

    # fill patient metadata
    ds.PatientName = metadata.Patient.Name
    ds.PatientID = metadata.Patient.ID
    ds.PatientAge = str(metadata.Patient.Age)
    ds.PatientSex = metadata.Patient.Sex
    if metadata.Patient.Comments:
        ds.PatientComments = metadata.Patient.Comments

    # image metadata
    ds.SamplesPerPixel = 1
    ds.BitsAllocated = 8
    ds.PixelRepresentation = 0
    ds.PhotometricInterpretation = "MONOCHROME1"
    ds.Rows, ds.Columns = img.shape
    ds.PixelData = img.tobytes()
    ds['PixelData'].is_undefined_length = True

    ds.is_little_endian = True
    ds.is_implicit_VR = False

    ds.ContentDate = metadata.Date
    ds.ContentTime = metadata.Time

    ds.save_as(dicom_dir_path.joinpath(filename), write_like_original=False)
    return filename


@dataclass
class DicomFile:
    Metadata: pd.DataFrame
    Image: np.ndarray


def read_dicom(dicom_path: Path) -> DicomFile:
    ds = dcmread(dicom_path)

    data = [v for v in ds if isinstance(v, DataElement) and v.keyword != "PixelData"]

    metadata = {
        "Tag": [e.tag.__str__() for e in data],
        "Name": [e.name for e in data],
        "VR": [e.VR for e in data],
        "Value": [e.value for e in data]
    }

    df = pd.DataFrame(metadata, columns=["Tag", "Name", "VR", "Value"])

    return DicomFile(df, ds.pixel_array)
