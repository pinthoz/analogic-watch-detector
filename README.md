# AnalogTimeDetector

## Introduction

This project focuses on detecting the time shown on analog clocks from images using computer vision techniques. It is designed to handle images of analog clock faces, extracting key components like the clock circle, hour hand, minute hand, second hand (if present), and the position of the number 12. 

### Datasets Used
The following datasets contributed to training and validation (not all images were used):
- [Watche Image Dataset](https://www.kaggle.com/datasets/ahedjneed/fancy-watche-images)
- [A Dataset of Watches](https://www.kaggle.com/datasets/mathewkouch/a-dataset-of-watches)
- [Simple Analog Clock (Monochrome)](https://www.kaggle.com/datasets/kopfgeldjaeger/simple-analog-clock-monochrome/data)
- Additional images from screenshots of watch stores and Google searches.

### Technology Stack
- **Language**: Python
- **Libraries**: Specified in `requirements.txt`
- **Model**: YOLOv8/YOLOv11n for object detection

---

## How to Use

### 1. Preparing the Dataset
If you want to add new images to the training or validation datasets:
1. Add the new images to the following folders:
   - Training dataset: `dataset/images/train`
   - Validation dataset: `dataset/images/val`
2. Generate annotations for these images:
   - Use [labelImg](https://github.com/heartexlabs/labelImg) to create annotations. 
   - Draw bounding boxes for the following:
     - The **circle** of the clock
     - The **hour hand**
     - The **minute hand**
     - The **second hand** (if present)
     - The **label for the number 12** or any marker representing 12.

3. Convert the annotations from XML to TXT format using the following script:
```bash
   python annotations_utils/xml_to_txt.py
```
Save the converted annotations in:
  - `dataset/labels/train` for training
  - `dataset/labels/val` for validation


### 2. Training the Model
To train the model with the updated dataset:

1. Ensure the dataset configuration is defined in `dataset.yaml`.
2. Run the training script:
```bash
python utils/train_model.py
```
We used Ultralytics 8.3.40 🚀 Python-3.8.9 torch-2.2.2+cu118 CUDA:0 (NVIDIA GeForce RTX 2060, 6144MiB) for the train.
If you don't have GPU, you can change the `device` variable in the `train_model.py` file to 1.
You can adjust parameters as needed.


### 3. Running the Application
To use the model for time detection:

1. Launch the app by running:
```bash
python main.py
```
The app provides a user-friendly GUI where you can:

- Select a single image or a folder containing multiple images for detection.
- Specify the name of the output CSV file where the detected times will be saved.
- View the detected time, and if available, compare it with the ground truth values.
- View the final image with the hands highlighted.
- View the detected components of the clock (circle, hour hand, minute hand, second hand, and 12 marker).

This app will always select the last model trained. If you want to use a specific model, you can change the `model_path` variable in the `utils\detections_utils` file in the `run_detection` function.

### 4. Running the Gradio Demo / Deploying to Hugging Face Spaces

The repository includes a lightweight Gradio interface that is ready for a Hugging Face Space. To start the demo locally run:

```bash
python gradio_app.py
```

By default the script loads `yolov8s.pt` from the project root. If you want to use a different checkpoint, set the `MODEL_PATH` environment variable before launching the app:

```bash
export MODEL_PATH=/path/to/your/weights.pt
python gradio_app.py
```

On Hugging Face Spaces create a new **Gradio** Space, upload the repository contents (including the weights file) and set the `gradio_app.py` file as the entry point. The dependencies listed in `requirements.txt` already include `gradio`, so installing them in the Space is enough to run the demo.

#### Deploying to Hugging Face Spaces

You can host the exact same interface on Hugging Face by following these steps:

1. **Install the Hugging Face CLI and log in** (the CLI stores a token that lets you push to Spaces):

   ```bash
   pip install -U "huggingface_hub[cli]"
   huggingface-cli login
   ```

2. **Create a new Space** on <https://huggingface.co/spaces> choosing the **Gradio** SDK. Give it a name such as `username/analogic-watch-detector`.

3. **Clone the empty Space locally** and copy the project files into it:

   ```bash
   git clone https://huggingface.co/spaces/username/analogic-watch-detector
   cd analogic-watch-detector
   rsync -av --exclude '.git' /path/to/this/repository/ ./
   ```

   Make sure the model weights you want to serve (e.g. `yolov8s.pt`) are also copied into the repository root or uploaded to the Space's "Files" tab.

4. **Tell the Space which file to run** by setting `gradio_app.py` as the entry point in the Space settings (`Files and versions` → `Settings` → `App file`). The provided `requirements.txt` already contains `gradio`, `ultralytics`, and `torch` so no extra dependency configuration is required.

5. **Push the code to Hugging Face** using regular Git commands:

   ```bash
   git lfs install  # enables large file support for the weight file
   git add .
   git commit -m "Deploy analog clock detector"
   git push
   ```

   After the push finishes, the Space will automatically build the environment and launch the Gradio application. You can monitor the deployment logs on the Space page.

If you later update the project, repeat steps 3 and 5 to sync your changes with the Space. Hugging Face will redeploy the app each time you push a new commit.

### 5. Test Set

We have provided a test set in the `test_set` folder. You can use this set to evaluate the model's performance. The images in this folder are not part of the training or validation datasets and they are retired from X, Reddit and the last ones are photos taken by us.

### 6. Handling Ground Truths
If you have a file containing the actual times for the images:

1. Place the file in the ground_truths folder.
2. The app will display:
    - The detected time
    - The original time (ground truth)
    - The difference between the two times in seconds

## Important Notes
### Dependencies
Install all required dependencies by running:

```bash
pip install -r requirements.txt
```

### Detection Limitations
- The detection process may fail if the model cannot identify critical components, such as:
    - The hour hand
    - The label for 12

### Annotations
- Ensure that the annotations are precise and well-labeled to achieve optimal model performance.

### App Limitations
- For the images to appear correctly in the app, the names of the images must be in the format `watch_test<number>.jpg`. For example, `watch_test1.jpg`.

## Results
#### Outputs Generated by the App
1. Visual Outputs:
    - Processed images with detected hands and clock visualizations are saved in results/images.
2. CSV Report:
Predicted times are saved in results/files/<output_csv_name>.csv.

## Example

### Before Detection

![image](img/1.png)

### After Detection

![image](img/2.png)

## Other Notes

We have also provided a script to detect the time from a camera feed. You can run the script by executing the following command:

```bash
python real_time.py
```

This project was developed by Ana Pinto and Pedro Leitão as part of a Computer Vision course.