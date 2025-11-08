"""Gradio interface for the Analogic Watch Detector model.

This module exposes a lightweight Gradio demo that can be used on
Hugging Face Spaces. It loads the YOLO model once, runs inference on the
uploaded image and renders the predicted time alongside the annotated
image.
"""

from __future__ import annotations

import os
from typing import Optional, Tuple

import cv2
import gradio as gr
import numpy as np
from ultralytics import YOLO

from utils.clock_utils import process_clock_time
from utils.detections_utils import get_latest_train_dir, run_detection


_MODEL: Optional[YOLO] = None


def _resolve_model_path() -> str:
    """Return the best available model path."""
    env_path = os.environ.get("MODEL_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    default_weight = "yolov8s.pt"
    if os.path.exists(default_weight):
        return default_weight

    try:
        return os.path.join(get_latest_train_dir(), "weights", "best.pt")
    except FileNotFoundError as exc:  # pragma: no cover - defensive path
        raise RuntimeError(
            "Model weights were not found. Provide them via the MODEL_PATH "
            "environment variable or include 'yolov8s.pt' in the repository."
        ) from exc


def _load_model() -> YOLO:
    """Lazy-load the YOLO model to keep the interface responsive."""
    global _MODEL
    if _MODEL is None:
        model_path = _resolve_model_path()
        _MODEL = YOLO(model_path)
    return _MODEL


def _format_time(prediction: Optional[dict]) -> str:
    """Generate a human readable string for the detected time."""
    if not prediction:
        return "Unable to determine the time from the detected clock."

    hours = prediction.get("hours")
    minutes = prediction.get("minutes")
    seconds = prediction.get("seconds")

    if hours is None:
        return "Unable to determine the time from the detected clock."

    if minutes is None:
        return f"Detected hour hand at {hours:02d}."

    if seconds is None:
        return f"Detected time: {hours:02d}:{minutes:02d}."

    return f"Detected time: {hours:02d}:{minutes:02d}:{seconds:02d}."


def _ensure_uint8_rgb(image: np.ndarray) -> np.ndarray:
    """Convert the provided image into an RGB uint8 array.

    Gradio can return float arrays in the range [0, 1] or [0, 255] depending on
    the installed version. Ultralytics expects uint8 arrays, so we normalise the
    input accordingly while preserving the original RGB channel order.
    """

    if image.dtype == np.uint8:
        return image

    image_float = image.astype(np.float32)
    max_value = image_float.max() if image_float.size else 0.0
    if max_value <= 1.0:
        image_float *= 255.0

    return np.clip(image_float, 0, 255).astype(np.uint8)


def predict(image: np.ndarray, confidence: float) -> Tuple[np.ndarray, str]:
    """Run detection on the uploaded image and return the annotated preview."""
    if image is None:
        raise gr.Error("Please upload an image of an analog clock.")

    model = _load_model()
    image_rgb_uint8 = _ensure_uint8_rgb(image)
    image_bgr = image_rgb_uint8[..., ::-1]

    detections, results = run_detection(
        image=image_bgr,
        image_path=None,
        model=model,
        confidence=confidence,
        save_path=None,
        save_visualization=False,
        return_prediction_results=True,
    )

    if not detections or not detections[0]:
        return image, "No clock components detected in the provided image."

    prediction = process_clock_time(detections, "uploaded_image")
    annotated = image_rgb_uint8
    if results:
        annotated_bgr = results[0].plot()
        annotated = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)

    return annotated, _format_time(prediction)


def build_interface() -> gr.Blocks:
    """Create the Gradio Blocks interface."""
    with gr.Blocks(title="Analog Clock Time Detector") as demo:
        gr.Markdown(
            """
            # Analog Clock Time Detector
            Upload a picture of an analog clock to detect the time displayed on it.
            The model is based on YOLOv8 and predicts the hour, minute and second
            hands when available.
            """
        )

        with gr.Row():
            with gr.Column():
                image_input = gr.Image(
                    type="numpy",
                    label="Clock image",
                    image_mode="RGB",
                )
                confidence_slider = gr.Slider(
                    minimum=0.01,
                    maximum=0.5,
                    step=0.01,
                    value=0.1,
                    label="Detection confidence threshold",
                )
                submit_btn = gr.Button("Detect time")

            with gr.Column():
                annotated_image = gr.Image(
                    type="numpy",
                    label="Detections",
                )
                time_output = gr.Textbox(
                    label="Predicted time",
                    placeholder="The predicted time will appear here.",
                )

        submit_btn.click(
            fn=predict,
            inputs=[image_input, confidence_slider],
            outputs=[annotated_image, time_output],
        )

        gr.Examples(
            examples=[
                os.path.join("img", "1.png"),
                os.path.join("img", "2.png"),
            ],
            inputs=image_input,
        )

    return demo


if __name__ == "__main__":
    build_interface().launch()
