'''
Generate labeling for any images in the directory.
'''
import os
import cv2
import numpy as np

from tqdm import trange
from utils import (Dataset, Iterator, save_load_means, subtract_channel_means, multiscale_single_test)

def labels_to_cityscapes_palette(labels):
    """
    Convert an image containing CARLA semantic segmentation labels to
    Cityscapes palette.
    """
    assert labels.ndim == 2, 'Semantic segmentation label has to be two dimensional!'
    classes = {
        0: [0, 0, 0],        # None
        1: [70, 70, 70],     # Buildings
        2: [190, 153, 153],  # Fences
        3: [72, 0, 90],      # Other
        4: [220, 20, 60],    # Pedestrians
        5: [153, 153, 153],  # Poles
        6: [157, 234, 50],   # RoadLines
        7: [128, 64, 128],   # Roads
        8: [244, 35, 232],   # Sidewalks
        9: [107, 142, 35],   # Vegetation
        10: [0, 0, 255],     # Vehicles
        11: [102, 102, 156], # Walls
        12: [220, 220, 0]    # TrafficSigns
    }
    result = np.zeros((labels.shape[0], labels.shape[1], 3))
    for key, value in classes.items():
        result[np.where(labels == key)] = value

    return result


def generate_labels(image_dir, labels_dir, model, channel_means, test_scales=[1], image_format='png'):

    if not os.path.exists(labels_dir):
        os.makedirs(labels_dir)

    filenames = [filename for filename in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, filename)) and os.path.splitext(filename)[1] == '.{}'.format(image_format)]

    for i in trange(len(filenames)):
        filename = filenames[i]
        filepath = os.path.join(image_dir, filename)
        filename_raw = os.path.splitext(filename)[0]
        filename_extension = os.path.splitext(filename)[1]
        '''
        if (not os.path.isfile(filepath)) or (filename_extension != '.{}'.format(image_format)):
            continue
        '''
        image_filepath = filepath
        labels_filepath = os.path.join(labels_dir, filename_raw + '.png')
        image = cv2.imread(image_filepath)
        image_input = subtract_channel_means(image=image, channel_means=channel_means)
        output = multiscale_single_test(image=image_input, input_scales=test_scales, predictor=model.test)
        labels = np.argmax(output, axis=-1)
        labels_png = np.array([np.zeros(labels.shape), np.zeros(labels.shape), labels]).transpose(1,2,0).astype(np.int8)
        cv2.imwrite(labels_filepath, labels_png)


def generate_labels_visualization(labels_dir, visualization_dir):

    if not os.path.exists(visualization_dir):
        os.makedirs(visualization_dir)

    filenames = [filename for filename in os.listdir(labels_dir) if os.path.isfile(os.path.join(labels_dir, filename)) and os.path.splitext(filename)[1] == '.png']

    for i in trange(len(filenames)):
        filename = filenames[i]
        filepath = os.path.join(labels_dir, filename)
        filename_raw = os.path.splitext(filename)[0]
        filename_extension = os.path.splitext(filename)[1]
        '''
        if (not os.path.isfile(filepath)) or (filename_extension != '.png'):
            continue
        '''
        labels_visualization_filepath = os.path.join(visualization_dir, filename_raw + '.png')
        labels = cv2.imread(filepath)[:,:,2]
        labels_visualization = labels_to_cityscapes_palette(labels=labels)
        cv2.imwrite(labels_visualization_filepath, labels_visualization)


def blend_images(image_1, image_2, mask, ratio):
    
    blend = mask * (image_1 * ratio + image_2 * (1 - ratio)) + (1 - mask) * image_2

    return blend

def blend_image_labels(image_dir, visualization_dir, blend_dir, image_format='png', mask=None):

    if not os.path.exists(blend_dir):
        os.makedirs(blend_dir)
    if mask is None:
        mask = 1

    image_filenames = [filename for filename in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, filename)) and os.path.splitext(filename)[1] == '.{}'.format(image_format)]
    labels_png_filenames = [filename for filename in os.listdir(visualization_dir) if os.path.isfile(os.path.join(visualization_dir, filename)) and os.path.splitext(filename)[1] == '.png']

    for i in trange(len(image_filenames)):
        image_filename = image_filenames[i]
        image_filepath = os.path.join(image_dir, image_filename)
        image_filename_raw = os.path.splitext(image_filename)[0]
        image_filename_extension = os.path.splitext(image_filename)[1]
        labels_png_filename = '{}.png'.format(image_filename_raw)
        assert labels_png_filename in labels_png_filenames, 'Image labels was not found!'
        labels_png_filepath = os.path.join(visualization_dir, labels_png_filename)
        blend_filename = '{}.png'.format(image_filename_raw)
        blend_filepath = os.path.join(blend_dir, blend_filename)

        image = cv2.imread(image_filepath)
        labels_visualization = cv2.imread(labels_png_filepath)
        blend = blend_images(image_1=labels_visualization, image_2=image, mask=1, ratio=0.7)
        cv2.imwrite(blend_filepath, blend)


if __name__ == '__main__':
    
    image_dir = '/home/marine/Workspace/cityscapes/leftImg8bit_demoVideo/leftImg8bit/demoVideo/stuttgart_00'
    visualization_dir = '/home/marine/Workspace/stuttgart_00/VisualizedSemanticSegmentation'
    blend_dir = '/home/marine/Workspace/stuttgart_00/Blend'

    blend_image_labels(image_dir=image_dir, visualization_dir=visualization_dir, blend_dir=blend_dir)
