from math import ceil
from pathlib import Path
from os import listdir, makedirs
from time import sleep

import streamlit as st

from scanner import Scanner
from converter import Converter
from components import Scan
from commons import to_image, open_image


def run_app():
    try:
        makedirs("results")
    except FileExistsError:
        pass

    saved_results_path = Path().absolute().joinpath("results")
    predefined_images_path = Path().absolute().joinpath("images")

    run_sim_was_pressed = st.button("Run simulation")

    step_input, detectors_count_input, span_input = st.beta_columns(3)
    step = step_input.number_input("∆α emitter/detector step [int]", value=2, min_value=1)
    detectors_count = detectors_count_input.number_input("detectors count [int]", value=500, step=1, min_value=1)
    span = span_input.number_input("emitter/detector span [angle °]", value=180, min_value=1)

    img, img_name = None, None
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
    elif image_opt is file_picker_opt:
        file_picker, image_preview = st.beta_columns(2)
        img_name = file_picker.selectbox("Choose an image", listdir(predefined_images_path))
        if img_name:
            img = open_image(predefined_images_path.joinpath(img_name).__str__())
            image_preview.image(img)
        else:
            img = None

    if run_sim_was_pressed:
        if img is not None:
            scan_img, res_img = st.beta_columns(2)
            n_steps = int(ceil(360 / step) + 1)
            with st.spinner("Running the simulation..."):
                scan = Scan(detectors_count)

                scanner = Scanner(img, span, step, n_steps, scan)
                scan_result = scanner.run(0)
                scan_img = scan_img.image(to_image(scan_result), caption="Simulated CT scan")
                for i in range(1, n_steps):
                    sleep(0.01)
                    scan_result = scanner.run(i)
                    scan_img.image(to_image(scan_result), caption="Simulated CT scan")

                converter = Converter(step, span, scanner.radius, scan, scan_result)
                result_img = converter.run(0)
                res_img = res_img.image(to_image(result_img), caption="Output image result")
                for i in range(1, n_steps):
                    sleep(0.01)
                    result_img = converter.run(i)
                    res_img.image(to_image(result_img), caption="Output image result")

                to_image(result_img) \
                    .save(saved_results_path.joinpath(img_name))

            st.success("Done! Result was saved to 'results' folder")

        else:
            st.error("please upload or select an image to run the simulation on")


if __name__ == "__main__":
    run_app()
