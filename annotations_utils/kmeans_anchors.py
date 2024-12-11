import yaml
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def debug_bounding_boxes(bboxes):
    """
    Perform detailed analysis of bounding box dimensions
    
    Args:
        bboxes (np.array): Array of bounding box dimensions
    """
    # Convert to numpy array if not already
    bboxes = np.array(bboxes)
    
    # Comprehensive statistics
    print("\n--- Bounding Box Dimension Analysis ---")
    print(f"Total bounding boxes: {len(bboxes)}")
    print("\nWidth Statistics:")
    print(f"  Min:    {bboxes[:, 0].min()}")
    print(f"  Max:    {bboxes[:, 0].max()}")
    print(f"  Mean:   {bboxes[:, 0].mean()}")
    print(f"  Median: {np.median(bboxes[:, 0])}")
    print(f"  Std:    {bboxes[:, 0].std()}")
    
    print("\nHeight Statistics:")
    print(f"  Min:    {bboxes[:, 1].min()}")
    print(f"  Max:    {bboxes[:, 1].max()}")
    print(f"  Mean:   {bboxes[:, 1].mean()}")
    print(f"  Median: {np.median(bboxes[:, 1])}")
    print(f"  Std:    {bboxes[:, 1].std()}")
    
    # Visualize distribution
    plt.figure(figsize=(12, 5))
    
    # Width distribution
    plt.subplot(1, 2, 1)
    plt.hist(bboxes[:, 0], bins=50, edgecolor='black')
    plt.title('Width Distribution')
    plt.xlabel('Width')
    plt.ylabel('Frequency')
    
    # Height distribution
    plt.subplot(1, 2, 2)
    plt.hist(bboxes[:, 1], bins=50, edgecolor='black')
    plt.title('Height Distribution')
    plt.xlabel('Height')
    plt.ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('bounding_box_distribution.png')
    plt.close()

def generate_anchors(bboxes, num_anchors=9):
    """
    Generate anchors using K-means clustering on bounding box dimensions.
    
    Args:
        bboxes (np.array): Array of bounding box dimensions (width, height)
        num_anchors (int): Number of anchors to generate
    
    Returns:
        np.array: Generated anchor dimensions
    """
    # Validate input
    if len(bboxes) == 0:
        raise ValueError("No valid bounding boxes found")
    
    # Debug bounding boxes before processing
    debug_bounding_boxes(bboxes)
    
    # Ensure enough unique bounding boxes for clustering
    num_anchors = min(num_anchors, len(set(tuple(box) for box in bboxes)))
    
    # Perform K-means on original scale (not normalized)
    kmeans = KMeans(
        n_clusters=num_anchors, 
        random_state=42, 
        n_init=10,  # Multiple initializations
        max_iter=300
    )
    
    # Fit K-means
    kmeans.fit(bboxes)
    
    # Get cluster centers
    anchors = kmeans.cluster_centers_
    
    # Print detailed anchor information
    print("\n--- Generated Anchors ---")
    for i, anchor in enumerate(anchors, 1):
        print(f"Anchor {i}: Width = {anchor[0]:.4f}, Height = {anchor[1]:.4f}")
    
    return anchors

def custom_anchor_generation(dataset_path):
    """
    Generate custom anchors from a YOLO dataset configuration.
    
    Args:
        dataset_path (str): Path to the dataset YAML file
    
    Returns:
        np.array or None: Generated anchors
    """
    # Load dataset configuration
    with open(dataset_path, 'r') as file:
        dataset_config = yaml.safe_load(file)
    
    # Extract training images path
    train_path = dataset_config['train']
    
    # Find corresponding labels directory
    labels_path = train_path.replace('images', 'labels')
    
    # List all annotation files
    label_files = []
    for root, _, files in os.walk(labels_path):
        label_files.extend([os.path.join(root, f) for f in files if f.endswith('.txt')])
    
    # Extract bounding box dimensions
    bboxes = []
    
    # Read YOLO annotation files
    for label_file in label_files:
        try:
            with open(label_file, 'r') as f:
                for line in f:
                    # Clean and split the line
                    parts = line.strip().split()
                    
                    try:
                        # YOLO format: class x_center y_center width height
                        # Extract width and height
                        width = float(parts[3])
                        height = float(parts[4])
                        
                        # Sanity check for valid dimensions
                        if 0 < width < 1 and 0 < height < 1:
                            bboxes.append([width, height])
                    
                    except (ValueError, IndexError) as e:
                        print(f"Error processing line in {label_file}: {line}")
        
        except Exception as e:
            print(f"Error processing file {label_file}: {e}")
    
    # Generate anchors
    try:
        # Convert to numpy array
        bboxes_array = np.array(bboxes)
        
        # Generate anchors
        anchors = generate_anchors(bboxes_array)
        
        # Format for YOLO configuration
        anchor_str = ', '.join([f'[{w:.2f},{h:.2f}]' for w, h in anchors])
        print("\nYOLO Anchor Configuration:")
        print(anchor_str)
        
        return anchors
    
    except Exception as e:
        print(f"Error generating anchors: {e}")
        return None


dataset_yaml_path = 'dataset.yaml'
custom_anchor_generation(dataset_yaml_path)