from os import listdir, makedirs
from pathlib import Path

import streamlit as st

from commons import open_image
from dicom import DicomMetadata, create_dicom, read_dicom


def run_app():
    try:
        makedirs("dicom")
    except FileExistsError:
        pass

    saved_results_path = Path().absolute().joinpath("results")
    saved_dicom_path = Path().absolute().joinpath("dicom")

    read_dicom_opt, save_dicom_opt = "Load DICOM file", "Save CT scan result to DICOM"
    opt = st.radio("", [read_dicom_opt, save_dicom_opt])
    if opt is read_dicom_opt:
        dc_name = st.selectbox("Choose a DICOM file to load", listdir(saved_dicom_path))
        if dc_name:
            load_dc = st.button("Load file")
            if load_dc:
                dc = read_dicom(saved_dicom_path.joinpath(dc_name))
                st.markdown("### DICOM metadata")
                st.dataframe(dc.Metadata)
                st.markdown("### CT scan image stored in the DICOM file")
                st.image(dc.Image)
    elif opt is save_dicom_opt:
        file_picker, image_preview = st.beta_columns(2)
        img_name = file_picker.selectbox("Choose a scan to save in DICOM file", listdir(saved_results_path))
        if img_name:
            img = open_image(saved_results_path.joinpath(img_name).__str__())
            image_preview.image(img)

            metadata = DicomMetadata()

            date_input, time_input = st.beta_columns(2)
            metadata.Date = date_input.date_input("Scan date")
            metadata.Time = time_input.time_input("Scan time")

            patient_name_input, patient_id_input = st.beta_columns(2)
            metadata.Patient.Name = patient_name_input.text_input("Patient name")
            metadata.Patient.ID = patient_id_input.text_input("Patient ID")

            patient_age_input, patient_sex_input = st.beta_columns(2)
            metadata.Patient.Age = patient_age_input.number_input("Patient age", step=1, min_value=0, max_value=120,
                                                                  value=20)
            metadata.Patient.Sex = patient_sex_input.selectbox("Patient sex", ["Male", "Female"])

            metadata.Patient.Comments = st.text_input("Patient related comments")

            save_file = st.button("Save DICOM file")

            if save_file:
                if metadata.is_valid():
                    fn = create_dicom(saved_results_path.joinpath(img_name), saved_dicom_path, metadata)
                    st.success(f"{fn} was saved successfully!")
                else:
                    st.error("provided metadata was not valid, all fields except Comments are required")


if __name__ == "__main__":
    run_app()
