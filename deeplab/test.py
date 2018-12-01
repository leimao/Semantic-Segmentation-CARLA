import os
import numpy as np

from model import DeepLab
from tqdm import trange
from utils import (Dataset, Iterator, save_load_means, subtract_channel_means, multiscale_single_validate, count_label_prediction_matches, 
                   mean_intersection_over_union, validation_single_demo)

if __name__ == '__main__':

    models_dir = './models/deeplab/resnet_101_carla'
    model_filename = 'resnet_101_0.6427.ckpt'
    testset_filename = './dataset/carla_testset.txt'
    dataset_directory = '/workspace/CARLA_Semantic_Segmentation/CARLA_dataset'
    minibatch_size = 16
    test_scales = [1]
    num_classes = 13
    ignore_label = 255

    channel_means = save_load_means(means_filename='channel_means.npz', image_filenames=None)

    test_dataset = Dataset(dataset_filename=testset_filename, dataset_directory=dataset_directory, image_extension='.png', label_extension='.png')
    test_iterator = Iterator(dataset=test_dataset, minibatch_size=minibatch_size, process_func=None, random_seed=None, scramble=False, num_jobs=1)

    model = DeepLab('resnet_101', training=True, num_classes=num_classes, ignore_label=ignore_label)
    model.load(os.path.join(models_dir, model_filename))

    test_loss_total = 0
    num_pixels_union_total = np.zeros(num_classes)
    num_pixels_intersection_total = np.zeros(num_classes)

    for i in trange(test_iterator.dataset_size):
        image, label = test_iterator.next_raw_data()
        image = subtract_channel_means(image=image, channel_means=channel_means)

        output, test_loss = multiscale_single_validate(image=image, label=label, input_scales=test_scales, validator=model.validate)
        test_loss_total += test_loss

        prediction = np.argmax(output, axis=-1)
        num_pixels_union, num_pixels_intersection = count_label_prediction_matches(labels=[np.squeeze(label, axis=-1)], predictions=[prediction], num_classes=num_classes, ignore_label=ignore_label)

        num_pixels_union_total += num_pixels_union
        num_pixels_intersection_total += num_pixels_intersection

    mean_IOU = mean_intersection_over_union(num_pixels_union=num_pixels_union_total, num_pixels_intersection=num_pixels_intersection_total)
    test_loss_ave = test_loss_total / test_iterator.dataset_size

    print('Test loss: {:.4f} | mIOU: {:.4f}'.format(test_loss_ave, mean_IOU))

    model.close()
