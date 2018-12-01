
import os
import cv2
import numpy as np

from model import DeepLab
from tqdm import trange
from utils import (Dataset, Iterator, save_load_means, subtract_channel_means)



def labels_to_cityscapes_palette(labels):
    """
    Convert an image containing CARLA semantic segmentation labels to
    Cityscapes palette.
    """
    assert labels.ndim == 2, "Semantic segmentation label has to be two dimensional!"
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


if __name__ == '__main__':


    models_dir = './models/deeplab/resnet_101_carla'
    model_filename = 'resnet_101_0.6427.ckpt'
    testset_filename = './dataset/carla_testset.txt'
    dataset_directory = '/workspace/CARLA_Semantic_Segmentation/CARLA_dataset'
    minibatch_size = 16
    test_scales = [1]
    num_classes = 13
    ignore_label = 255

    test_episodes = ['episode_{:0>4d}'.format(i) for i in range(1)]

    channel_means = save_load_means(means_filename='channel_means.npz', image_filenames=None)

    model = DeepLab('resnet_101', training=False, num_classes=num_classes, ignore_label=ignore_label)
    model.load(os.path.join(models_dir, model_filename))

    for test_episode in test_episodes:
        print('Generating semantic segmentation predictions for {}'.format(test_episode))
        episode_dir = os.path.join(dataset_directory, test_episode, 'CameraRGB')
        episode_filenames = list()
        for filename in os.listdir(episode_dir):
            filename_raw = os.path.splitext(filename)[0]
            episode_filenames.append(filename_raw)
        episode_filenames.sort()

        predictions_dir = os.path.join(dataset_directory, test_episode, 'PredictSemanticSegmentation')
        if not os.path.exists(predictions_dir):
            os.makedirs(predictions_dir)

        for i in trange(len(episode_filenames)):
            image_path = os.path.join(dataset_directory, test_episode, 'CameraRGB', episode_filenames[i] + '.png')
            predictions_path = os.path.join(predictions_dir, episode_filenames[i] + '.png')
            image = cv2.imread(image_path)
            image_input = subtract_channel_means(image=image, channel_means=channel_means)
            output = model.test(inputs=[image_input], target_height=image.shape[0], target_width=image.shape[1])[0]
            predictions = labels_to_cityscapes_palette(labels=np.argmax(output, axis=-1))
            cv2.imwrite(predictions_path, predictions)

    model.close()



