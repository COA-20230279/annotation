# Annotation System

This repository holds the source code of the annotation system for the manuscript of COA-20230279.

## Dependencies

- Python >= 3.9
- Gradio >= 4.11
- Numpy >= 1.26.2
- Matplotlib >= 3.8.2

## How to Deploy

1. Create a virtual environment and install the dependencies:

    ```bash
    conda create -n annotation python=3.9
    conda activate annotation
    pip install -r requirements.txt
    ```

2. Run the application:

    ```bash
    conda activate annotation
    python app.py
    ```

3. Open the browser and go to the address: [http://127.0.0.1:7860](http://127.0.0.1:7860)

This demo only includes a sample of 100 patient records to illustrate the annotation process. The complete dataset is not included in this demo.
