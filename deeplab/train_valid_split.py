"""
Prepare the trainset and validation set for CARLA dataset.
"""

import os
import random

def rotate_list(lst, k):
    """
    Rotate lst by k positions to the right.
    For example,
    >>> rotate([1, 2, 3], 1)
    [3, 1, 2]
    >>> rotate([0, 1, 2, 3, 4], -2)
    [2, 3, 4, 0, 1]
    """
    r = k % len(lst)
    return lst[-r:] + lst[:-r]


def train_valid_split(directory, episode_foldernames, trainset_filename, validset_filename, train_valid_ratio=0.9, random_seed=0):
    """
    Split dataset into training subset and validation subset.
    """
    random.seed(random_seed)

    trainset_images = list()
    trainset_labels = list()
    validset_images = list()
    validset_labels = list()

    for episode_foldername in episode_foldernames:
        episode_dir = os.path.join(directory, episode_foldername, 'CameraRGB')
        episode_filenames = list()
        for filename in os.listdir(episode_dir):
            filename_raw = os.path.splitext(filename)[0]
            episode_filenames.append(filename_raw)
        episode_filenames.sort()

        # Randomly rotate the sorted list
        num_samples = len(episode_filenames)
        k = random.randint(0, num_samples-1)
        episode_filenames = rotate_list(lst=episode_filenames, k=k)
        split_point = int(num_samples * train_valid_ratio)
        trainset = episode_filenames[:split_point]
        validset = episode_filenames[split_point:]

        trainset_images += [os.path.join(episode_foldername, 'CameraRGB', filename + '.png') for filename in trainset]
        trainset_labels += [os.path.join(episode_foldername, 'CameraSemanticSegmentation', filename + '.png') for filename in trainset]

        validset_images += [os.path.join(episode_foldername, 'CameraRGB', filename + '.png') for filename in validset]
        validset_labels += [os.path.join(episode_foldername, 'CameraSemanticSegmentation', filename + '.png') for filename in validset]


    with open(trainset_filename, 'w+') as fhand:
        for image_path, label_path in zip(trainset_images, trainset_labels):
            fhand.write('{},{}\n'.format(image_path, label_path))

    with open(validset_filename, 'w+') as fhand:
        for image_path, label_path in zip(validset_images, validset_labels):
            fhand.write('{},{}\n'.format(image_path, label_path))


def main():

    # https://carla.readthedocs.io/en/stable/carla_settings/
    num_weathers = 15
    num_episodes = 50
    start_episode = num_weathers
    carla_dataset_directory = '/home/marine/Workspace/CARLA_dataset'
    dataset_index_directory = './dataset'
    trainset_filename = 'carla_trainset.txt'
    validset_filename='carla_validset.txt'
    if not os.path.exists(dataset_index_directory):
        os.makedirs(dataset_index_directory)
    # episode_0000 to episode_0014 were reserved for test
    trainvalid_episodes = ['episode_{:0>4d}'.format(i) for i in range(start_episode, num_episodes)]
    test_episodes = ['episode_{:0>4d}'.format(i) for i in range(start_episode)]

    train_valid_split(directory=carla_dataset_directory, episode_foldernames=trainvalid_episodes, trainset_filename=os.path.join(dataset_index_directory, trainset_filename), validset_filename=os.path.join(dataset_index_directory, validset_filename), train_valid_ratio=0.9, random_seed=0)

if __name__ == '__main__':
    
    main()