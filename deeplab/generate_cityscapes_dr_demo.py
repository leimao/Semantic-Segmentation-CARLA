'''
Generate labels for Cityscapes demo testsets using CARLA trained models.
'''
import os
from model import DeepLab
from utils import save_load_means
from carla_utils import labels_to_cityscapes_palette, generate_labels, generate_labels_visualization, blend_image_labels

def generate_CARLA_test_demos():

    models_dir = './models/deeplab/resnet_101_carla'
    model_filename = 'resnet_101_0.6427.ckpt'
    dataset_directory = '/workspace/CARLA_Semantic_Segmentation/cityscapes/leftImg8bit/demoVideo/'
    demo_direcotry = '/workspace/CARLA_Semantic_Segmentation/cityscapes_demo/'
    test_scales = [1]
    num_classes = 13
    ignore_label = 255

    test_episodes = ['stuttgart_00', 'stuttgart_01', 'stuttgart_02']

    channel_means = save_load_means(means_filename='channel_means.npz', image_filenames=None)

    model = DeepLab('resnet_101', training=False, num_classes=num_classes, ignore_label=ignore_label)
    model.load(os.path.join(models_dir, model_filename))

    for test_episode in test_episodes:
        print('Generating semantic segmentation labels for {}'.format(test_episode))
        image_dir = os.path.join(dataset_directory, test_episode)
        predicted_labels_dir = os.path.join(demo_direcotry, test_episode, 'PredictedSemanticSegmentation')
        predicted_visualization_dir = os.path.join(demo_direcotry, test_episode, 'PredictedVisualizedSemanticSegmentation')
        predicted_blend_dir = os.path.join(demo_direcotry, test_episode, 'PredictedBlend')
        print('Generating predicted labels ...')
        generate_labels(image_dir=image_dir, labels_dir=predicted_labels_dir, model=model, channel_means=channel_means, test_scales=test_scales, image_format='png')
        print('Generating predicted labels visualizations ...')
        generate_labels_visualization(labels_dir=predicted_labels_dir, visualization_dir=predicted_visualization_dir)
        print('Generating image predicted labels visualizations blends ...')
        blend_image_labels(image_dir=image_dir, visualization_dir=predicted_visualization_dir, blend_dir=predicted_blend_dir, image_format='png', mask=None)

    model.close()


if __name__ == '__main__':
    
    generate_CARLA_test_demos()