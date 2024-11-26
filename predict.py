from PIL import Image, ImageDraw

# Input JSON-like detection results
detections = [
    [
        {
            "box": [69.94551086425781, 75.28325653076172, 371.8227844238281, 372.56585693359375],
            "confidence": 0.9537157416343689,
            "class_id": 0.0,
            "class_name": "circle"
        },
        {
            "box": [216.2585906982422, 161.34420776367188, 320.2163391113281, 226.0605010986328],
            "confidence": 0.943381130695343,
            "class_id": 2.0,
            "class_name": "minutes"
        },
        {
            "box": [151.2060089111328, 175.1717987060547, 222.4562530517578, 226.87026977539062],
            "confidence": 0.938014805316925,
            "class_id": 1.0,
            "class_name": "hours"
        },
        {
            "box": [210.75967407226562, 211.9117889404297, 227.33993530273438, 229.33236694335938],
            "confidence": 0.7478576898574829,
            "class_id": 4.0,
            "class_name": "center"
        },
        {
            "box": [197.8579864501953, 92.28866577148438, 239.21743774414062, 145.15280151367188],
            "confidence": 0.6843570470809937,
            "class_id": 5.0,
            "class_name": "12"
        },
        {
            "box": [198.45245361328125, 188.22543334960938, 235.86289978027344, 309.3158874511719],
            "confidence": 0.5428741574287415,
            "class_id": 3.0,
            "class_name": "seconds"
        },
        {
            "box": [199.9100341796875, 183.76858520507812, 222.2774658203125, 308.64501953125],
            "confidence": 0.3318377435207367,
            "class_id": 3.0,
            "class_name": "seconds"
        }
    ]
]

# Path to the source image
image_path = "examples/watch_test.jpg"  # Replace with the actual image path

def draw_seconds_boxes(image_path, detections):
    # Open the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Flatten detections list if it's nested
    detections = [item for sublist in detections for item in sublist]

    # Filter for "seconds" class (class_id == 3.0)
    seconds_boxes = [d for d in detections if d['class_id'] == 3.0]

    # Draw bounding boxes
    for det in seconds_boxes:
        box = det["box"]
        confidence = det["confidence"]
        class_name = det["class_name"]
        
        # Draw the box (x_min, y_min, x_max, y_max)
        draw.rectangle(box, outline="blue", width=3)
        # Add a label with confidence score
        draw.text((box[0], box[1] - 10), f"{class_name} ({confidence:.2f})", fill="blue")

    # Show the image
    image.show()

# Run the function
draw_seconds_boxes(image_path, detections)
