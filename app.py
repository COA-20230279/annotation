#! /usr/bin/env python
# -*- coding: utf-8 -*-

import shutil

import gradio as gr

from audiogram import Audiogram

audiogram = Audiogram("anonymized-data.pkl.xz")


def get_audiogram_info(index: int) -> tuple[dict, str, str]:
    """Get the audiogram info and plot for a given index.

    Args:
        index (int): The index of the patient.

    Returns:
        tuple[dict, str, str]: patient infomation, filepath of the left plot,  filepath of the right plot
    """
    patient_info = audiogram.patient_info(index)
    figures = audiogram.plots(index)
    left_plot = figures["left"]
    right_plot = figures["right"]

    return patient_info, left_plot, right_plot


def flag_func(*args) -> str:
    """Flag the annotation.

    Returns:
        str: result of the flagging in HTML format.
    """
    args = list(args)
    if not args[0]:  # username
        return '<b>❌Faild!</b><br>Please select the <b><span style="color:Red;">"Audiologist Name"</span></b> first'
    callback.flag(args)
    return '<span style="color:Green;"><b>🟢Successful!<b></span>'


CHOICES = {
    "Degree": ["Normal", "Mild", "Moderate", "Moderately Severe", "Severe", "Profound", "Complete Deafness"],
    "Type": ["Normal", "Conductive", "Sensorineural", "Mixed"],
    "Configuration": ["Normal", "Flat", "Rising", "Sloping", "Total deafness", "Irregular"],
    "USERS": ["Audiologist-A", "Audiologist-B", "Audiologist-C"],
}

PATIENT_INFO_MARKDOWN = """
Explanations of the Patient Info:
- AC: Air-conducted thresholds at 250, 500, 1k, 2k, 4k, 8k Hz
- BC: Bone-conducted thresholds at 250, 500, 1k, 2k, 4k Hz
- PTA (Pure Tone Average): Air-conducted average value at 500, 1k, 2k, 4k Hz
- (R) / (L): Right ear/ Left ear
"""

DEMO_HTML = """
<h4>How to use this demo?</h4>
1. Choose your name in the <b><span style="color:Red;">"Audiologist Name"</span></b>.<br>
2. Slide the <b><span style="color:Red;">"Patient ID"</span></b> slider, you will see the patient info and audiogram plots.<br>
3. Annotate the degree, type and configuration of this patient in the right <b><span style="color:Red;">"Dropdown Boxes"</span></b>.<br>
4. Click the <b><span style="color:Red;">"Submit"</span></b> button to save the annotation.<br><br>

This demo only includes a sample of 100 patient records to illustrate the annotation process. The complete dataset is not included in this demo.<br>
To deploy the demo yourself, please refer to the source code on GitHub at <a href="https://github.com/COA-20230279/annotation">this link</a>.
"""

# Build the GUI
with gr.Blocks(title="Annotation") as demo:
    with gr.Row(variant="compact"):
        with gr.Column(variant="compact"):
            patient_info = gr.JSON(label="PatientInfo")
            patient_info_notes = gr.Markdown(value=PATIENT_INFO_MARKDOWN, label="PatientInfoNotes")

        right_plot = gr.Image(label="right", interactive=False)
        left_plot = gr.Image(label="left", interactive=False)

    with gr.Row(variant="compact"):
        with gr.Column(scale=1, variant="compact"):
            with gr.Row(variant="compact"):
                slider = gr.Slider(value=0, label="Patient ID", minimum=0, maximum=audiogram.n_sample - 1, step=1)
            with gr.Row(variant="compact"):
                username = gr.Dropdown(choices=CHOICES["USERS"], interactive=True, label="Audiologist Name")
                submit_btn = gr.Button("Submit", variant="primary")
            flag_status = gr.HTML(value="", label="Annotation")
            demo_html = gr.HTML(value=DEMO_HTML, label="Annotation")

        with gr.Column(scale=2, variant="compact"):
            with gr.Row(variant="compact"):
                flagged_degree_r = gr.Dropdown(choices=CHOICES["Degree"], interactive=True, label="Degree (R)")
                flagged_degree_l = gr.Dropdown(choices=CHOICES["Degree"], interactive=True, label="Degree (L)")
            with gr.Row(variant="compact"):
                flagged_type_r = gr.Dropdown(choices=CHOICES["Type"], interactive=True, label="Type (R)")
                flagged_type_l = gr.Dropdown(choices=CHOICES["Type"], interactive=True, label="Type (L)")
            with gr.Row(variant="compact"):
                flagged_configuration_r = gr.Dropdown(choices=CHOICES["Configuration"], interactive=True, label="Configuration (R)")
                flagged_configuration_l = gr.Dropdown(choices=CHOICES["Configuration"], interactive=True, label="Configuration (L)")


    shutil.rmtree("cache", ignore_errors=True)
    shutil.rmtree("annotation", ignore_errors=True)

    # We need annotate the following information:
    need_flag = [
        username,
        patient_info,
        flagged_degree_l,
        flagged_degree_r,
        flagged_type_l,
        flagged_type_r,
        flagged_configuration_l,
        flagged_configuration_r,
    ]
    callback = gr.CSVLogger()
    callback.setup(need_flag, flagging_dir="annotation")

    # Actions when the user slides the slider
    output = [patient_info, left_plot, right_plot]
    slider.change(get_audiogram_info, slider, output)
    submit_btn.click(flag_func, need_flag, flag_status, preprocess=False)

# Launch the GUI
demo.queue()
demo.launch()
