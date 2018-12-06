'''
Generate labels for CARLA testsets
'''
import os
from model import DeepLab
from utils import save_load_means
from carla_utils import labels_to_cityscapes_palette, generate_labels, generate_labels_visualization, blend_image_labels

def generate_CARLA_test_demos():

    models_dir = './models/deeplab/resnet_101_carla'
    model_filename = 'resnet_101_0.6427.ckpt'
    dataset_directory = '/workspace/CARLA_Semantic_Segmentation/CARLA_dataset'
    demo_directory = '/workspace/CARLA_Semantic_Segmentation/CARLA_demos'
    test_scales = [1]
    num_classes = 13
    ignore_label = 255

    test_episodes = ['episode_{:0>4d}'.format(i) for i in range(15)]

    if not os.path.exists(demo_directory):
        os.makedirs(demo_directory)

    channel_means = save_load_means(means_filename='channel_means.npz', image_filenames=None)

    model = DeepLab('resnet_101', training=False, num_classes=num_classes, ignore_label=ignore_label)
    model.load(os.path.join(models_dir, model_filename))

    for test_episode in test_episodes:
        print('Generating semantic segmentation labels for {}'.format(test_episode))
        image_dir = os.path.join(dataset_directory, test_episode, 'CameraRGB')
        gt_labels_dir = os.path.join(dataset_directory, test_episode, 'CameraSemanticSegmentation')
        predicted_labels_dir = os.path.join(demo_directory, test_episode, 'PredictedSemanticSegmentation')
        gt_visualization_dir = os.path.join(demo_directory, test_episode, 'GtVisualizedSemanticSegmentation')
        predicted_visualization_dir = os.path.join(demo_directory, test_episode, 'PredictedVisualizedSemanticSegmentation')
        gt_blend_dir = os.path.join(demo_directory, test_episode, 'GtBlend')
        predicted_blend_dir = os.path.join(demo_directory, test_episode, 'PredictedBlend')
        print('Generating predicted labels ...')
        generate_labels(image_dir=image_dir, labels_dir=predicted_labels_dir, model=model, channel_means=channel_means, test_scales=test_scales, image_format='png')
        print('Generating predicted labels visualizations ...')
        generate_labels_visualization(labels_dir=predicted_labels_dir, visualization_dir=predicted_visualization_dir)
        print('Generating image predicted labels visualizations blends ...')
        blend_image_labels(image_dir=image_dir, visualization_dir=predicted_visualization_dir, blend_dir=predicted_blend_dir, image_format='png', mask=None)
        print('Generating ground-truth labels visualizations ...')
        generate_labels_visualization(labels_dir=gt_labels_dir, visualization_dir=gt_visualization_dir)
        print('Generating image ground-truth labels visualizations blends ...')
        blend_image_labels(image_dir=image_dir, visualization_dir=gt_visualization_dir, blend_dir=gt_blend_dir, image_format='png', mask=None)

    model.close()


if __name__ == '__main__':
    
    generate_CARLA_test_demos()