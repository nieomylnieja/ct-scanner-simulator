from pathlib import Path
from os import listdir

import numpy as np
import streamlit as st

from scanner import Scanner
from converter import Converter
from components import Scan
from commons import SimulationResults, to_image, open_image


def run_app():
    run_sim_was_pressed = st.button("Run simulation")

    step_input, detectors_count_input, span_input = st.beta_columns(3)
    step = step_input.number_input("∆α emitter/detector step [int]", value=2, min_value=1)
    detectors_count = detectors_count_input.number_input("detectors count [int]", value=500, step=1, min_value=1)
    span = span_input.number_input("emitter/detector span [angle °]", value=180, min_value=1)

    img = None
    file_picker_opt, file_upload_opt = "Choose one of the predefined images", "Upload image"
    image_opt = st.radio("", [file_upload_opt, file_picker_opt])
    if image_opt is file_upload_opt:
        file_uploader, image_preview = st.beta_columns(2)
        file_upload = file_uploader.file_uploader("Upload image", type=["png", "jpg"])
        if file_upload:
            img = open_image(file_upload)
            image_preview.image(img)
        else:
            img = None
    else:
        predefined_images_path = Path().absolute().joinpath("images")
        file_picker, image_preview = st.beta_columns(2)
        img_name = file_picker.selectbox("Choose an image", listdir(predefined_images_path))
        if img_name:
            img = open_image(predefined_images_path.joinpath(img_name).__str__())
            image_preview.image(img)
        else:
            img = None

    if run_sim_was_pressed:
        if img is not None:
            with st.spinner('Running the simulation...'):
                result = run_sim(img, span, step, detectors_count)
            st.success('Done!')
            scan_img, res_img = st.beta_columns(2)
            scan_img.image(to_image(result.Scan), caption="Simulated CT scan")
            res_img.image(to_image(result.Result), caption="Output image result")
        else:
            st.error("please upload or select an image to run the simulation on")


def run_sim(img: np.ndarray, span: int, step: int, detectors_count: int) -> SimulationResults:
    scan = Scan(detectors_count)
    scanner = Scanner(img, span, step)
    sinogram = scanner.run(scan)
    converter = Converter(step, span, scanner.radius)
    res = converter.run(sinogram, scan)
    return SimulationResults(sinogram, res)


if __name__ == "__main__":
    run_app()
