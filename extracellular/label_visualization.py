
import os
import cv2
from utils import labels_to_cityscapes_palette

def visualize_labels_from_directory(episode_dir):

    semantic_segmentation_labels_dir = os.path.join(episode_dir, 'CameraSemanticSegmentation')
    semantic_segmentation_visualization_dir = os.path.join(episode_dir, 'CameraSemanticSegmentationVisualization')
    if not os.path.exists(semantic_segmentation_visualization_dir):
        os.makedirs(semantic_segmentation_visualization_dir)
    input_filepaths = [os.path.join(semantic_segmentation_labels_dir, file) for file in os.listdir(semantic_segmentation_labels_dir) if os.path.isfile(os.path.join(semantic_segmentation_labels_dir, file)) and os.path.splitext(file)[1] == '.png']
    for input_filepath in input_filepaths:
        labels = cv2.imread(input_filepath)[:,:,2]
        labels_visualization = labels_to_cityscapes_palette(labels=labels)
        output_filename = os.path.basename(input_filepath)
        output_filepath = os.path.join(semantic_segmentation_visualization_dir, output_filename)
        cv2.imwrite(output_filepath, labels_visualization)

def main():

    visualize_labels_from_directory('./episode_0013')

if __name__ == '__main__':
    
    main()
