from carla_utils import labels_to_cityscapes_palette, generate_labels, generate_labels_visualization

def generate_CARLA_test_demos():

    models_dir = './models/deeplab/resnet_101_carla'
    model_filename = 'resnet_101_0.6427.ckpt'
    dataset_directory = '/workspace/CARLA_Semantic_Segmentation/CARLA_dataset'
    test_scales = [1]
    num_classes = 13
    ignore_label = 255

    test_episodes = ['episode_{:0>4d}'.format(i) for i in range(15)]

    channel_means = save_load_means(means_filename='channel_means.npz', image_filenames=None)

    model = DeepLab('resnet_101', training=False, num_classes=num_classes, ignore_label=ignore_label)
    model.load(os.path.join(models_dir, model_filename))

    for test_episode in test_episodes:
        print('Generating semantic segmentation labels for {}'.format(test_episode))
        image_dir = os.path.join(dataset_directory, test_episode, 'CameraRGB')
        labels_dir = os.path.join(dataset_directory, test_episode, 'PredictedSemanticSegmentation')
        visualization_dir = os.path.join(dataset_directory, test_episode, 'VisualizedSemanticSegmentation')
        print('Generating labels ...')
        generate_labels(image_dir=image_dir, labels_dir=labels_dir, model=model, channel_means=channel_means, test_scales=test_scales, image_format='png')
        print('Generating label visualizations ...')
        generate_labels_visualization(labels_dir=labels_dir, visualization_dir=visualization_dir)

    model.close()


if __name__ == '__main__':
    
    generate_CARLA_test_demos()