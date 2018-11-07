#!/usr/bin/env python3

# Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""Basic CARLA client example."""

from __future__ import print_function

import argparse
import logging
import random
import time

from carla.client import make_carla_client
from carla.sensor import Camera, Lidar
from carla.settings import CarlaSettings
from carla.tcp import TCPConnectionError
from carla.util import print_over_same_line


def random_weather(num_weathers=14):
    # https://carla.readthedocs.io/en/stable/carla_settings/#weather-presets
    # Totally 14 weathers
    random_id = random.randint(0,num_weathers)
    return random_id



def run_carla_client(args, episode, weather_id):

    frames_per_episode = args.frames_per_episode

    number_of_vehicles = args.number_of_vehicles
    number_of_pedestrians = args.number_of_pedestrians

    quality_level = args.quality_level

    # We assume the CARLA server is already waiting for a client to connect at
    # host:port. To create a connection we can use the `make_carla_client`
    # context manager, it creates a CARLA client object and starts the
    # connection. It will throw an exception if something goes wrong. The
    # context manager makes sure the connection is always cleaned up on exit.
    with make_carla_client(args.host, args.port) as client:
        print('CarlaClient connected')

        if args.settings_filepath is None:

            # Create a CarlaSettings object. This object is a wrapper around
            # the CarlaSettings.ini file. Here we set the configuration we
            # want for the new episode.
            settings = CarlaSettings()
            settings.set(
                SynchronousMode=True,
                SendNonPlayerAgentsInfo=True,
                NumberOfVehicles=number_of_vehicles,
                NumberOfPedestrians=number_of_pedestrians,
                WeatherId=weather_id,
                QualityLevel=quality_level)
            settings.randomize_seeds()

            # Now we want to add a couple of cameras to the player vehicle.
            # We will collect the images produced by these cameras every
            # frame.

            # The default camera captures RGB images of the scene.
            camera0 = Camera('CameraRGB')
            # Set image resolution in pixels.
            camera0.set_image_size(800, 600)
            #camera0.set_image_size(513, 513)
            # Set its position relative to the car in meters.
            #camera0.set_position(0.30, 0, 1.30)
            camera0.set_position(1.60, 0, 1.30)
            settings.add_sensor(camera0)

            # Let's add another camera producing ground-truth depth.
            camera1 = Camera('CameraSemanticSegmentation', PostProcessing='SemanticSegmentation')
            camera1.set_image_size(800, 600)
            #camera1.set_image_size(513, 513)
            #camera1.set_position(0.30, 0, 1.30)
            camera1.set_position(1.60, 0, 1.30)
            settings.add_sensor(camera1)

        else:

            # Alternatively, we can load these settings from a file.
            with open(args.settings_filepath, 'r') as fp:
                settings = fp.read()

        # Now we load these settings into the server. The server replies
        # with a scene description containing the available start spots for
        # the player. Here we can provide a CarlaSettings object or a
        # CarlaSettings.ini file as string.
        scene = client.load_settings(settings)

        # Choose one player start at random.
        number_of_player_starts = len(scene.player_start_spots)
        player_start = random.randint(0, max(0, number_of_player_starts - 1))

        # Notify the server that we want to start the episode at the
        # player_start index. This function blocks until the server is ready
        # to start the episode.
        print('Starting new episode...')
        client.start_episode(player_start)

        # Iterate every frame in the episode.
        for frame in range(0, frames_per_episode):

            # Read the data produced by the server this frame.
            measurements, sensor_data = client.read_data()

            # Print some of the measurements.
            print('number of frames: {}'.format(frame))
            print_measurements(measurements)

            # Save the images to disk if requested.
            if args.save_images_to_disk:
                if frame % args.save_images_to_disk_frequency == 0:
                    for name, measurement in sensor_data.items():
                        filename = args.out_filename_format.format(episode, name, frame)

                        measurement.save_to_disk(filename)

            # We can access the encoded data of a given image as numpy
            # array using its "data" property. For instance, to get the
            # depth value (normalized) at pixel X, Y
            #
            #     depth_array = sensor_data['CameraDepth'].data
            #     value_at_pixel = depth_array[Y, X]
            #

            # Now we have to send the instructions to control the vehicle.
            # If we are in synchronous mode the server will pause the
            # simulation until we send this control.

            if not args.autopilot:

                client.send_control(
                    steer=random.uniform(-1.0, 1.0),
                    throttle=0.5,
                    brake=0.0,
                    hand_brake=False,
                    reverse=False)

            else:

                # Together with the measurements, the server has sent the
                # control that the in-game autopilot would do this frame. We
                # can enable autopilot by sending back this control to the
                # server. We can modify it if wanted, here for instance we
                # will add some noise to the steer.

                control = measurements.player_measurements.autopilot_control
                control.steer += random.uniform(-0.1, 0.1)
                client.send_control(control)

        return


def print_measurements(measurements):
    number_of_agents = len(measurements.non_player_agents)
    player_measurements = measurements.player_measurements
    message = 'Vehicle at ({pos_x:.1f}, {pos_y:.1f}), '
    message += '{speed:.0f} km/h, '
    message += 'Collision: {{vehicles={col_cars:.0f}, pedestrians={col_ped:.0f}, other={col_other:.0f}}}, '
    message += '{other_lane:.0f}% other lane, {offroad:.0f}% off-road, '
    message += '({agents_num:d} non-player agents in the scene)'
    message = message.format(
        pos_x=player_measurements.transform.location.x,
        pos_y=player_measurements.transform.location.y,
        speed=player_measurements.forward_speed * 3.6, # m/s -> km/h
        col_cars=player_measurements.collision_vehicles,
        col_ped=player_measurements.collision_pedestrians,
        col_other=player_measurements.collision_other,
        other_lane=100 * player_measurements.intersection_otherlane,
        offroad=100 * player_measurements.intersection_offroad,
        agents_num=number_of_agents)
    print_over_same_line(message)


def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='localhost',
        help='IP of the host server (default: localhost)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-a', '--autopilot',
        action='store_true',
        help='enable autopilot')
    argparser.add_argument(
        '-q', '--quality-level', # Low, Medium, High, or Epic
        choices=['Low', 'Epic'],
        type=lambda s: s.title(),
        default='Epic',
        help='graphics quality level, a lower level makes the simulation run considerably faster.')
    argparser.add_argument(
        '-i', '--images-to-disk',
        action='store_true',
        dest='save_images_to_disk',
        help='save images (and Lidar data if active) to disk')
    argparser.add_argument(
        '-c', '--carla-settings',
        metavar='PATH',
        dest='settings_filepath',
        default=None,
        help='Path to a "CarlaSettings.ini" file')


    argparser.add_argument(
        '--number-of-episodes',
        default=50,
        type=int,
        dest='number_of_episodes',
        help='Number of simulation episode')

    argparser.add_argument(
        '--frames-per-episode',
        default=50,
        type=int,
        dest='frames_per_episode',
        help='Number of frames per episode')

    argparser.add_argument(
        '--images-to-disk-frequency',
        default=1,
        type=int,
        dest='save_images_to_disk_frequency',
        help='Image saving frequency')


    argparser.add_argument(
        '--number-of-vehicles',
        default=200,
        type=int,
        dest='number_of_vehicles',
        help='Number of vehicles in map')

    argparser.add_argument(
        '--number-of-pedestrians',
        default=500,
        type=int,
        dest='number_of_pedestrians',
        help='Number of pedestrians in map')
    '''
    argparser.add_argument(
        '--weather-id',
        default=0,
        type=int,
        dest='weather_id',
        help='Weather Id from 0 to 14')
    '''

    args = argparser.parse_args()

    print(args)

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    args.out_filename_format = '_out/episode_{:0>4d}/{:s}/{:0>6d}'

    episode = 0
    while episode < args.number_of_episodes:
        print('episode: {}'.format(episode))
        try:
            time.sleep(1)
            weather_id = episode % 15
            run_carla_client(args, episode, weather_id)
            episode += 1

        except TCPConnectionError as error:
            print('==========================================')
            print('Time-out!')
            print('==========================================')
            logging.error(error)
            time.sleep(1)


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
