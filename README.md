# Semantic Segmentation CARLA

Lei Mao

University of Chicago

## CARLA Instructions

The experience are gained from using [CARLA 0.8.2](https://github.com/carla-simulator/carla/releases/tag/0.8.2).

### Dependencies

* Python 3.5/3.5 (CARLA 0.8.2 does not support Python 3.8)


### Start CARLA

To start CARLA in a window with customized resolution.


```bash
$ ./CarlaUE4.sh -windowed -ResX=512 -ResY=512
```
The resolution settings and window settings only affects the display on the screen. It does not affect the internal resolution in the game environment.


* ``ALT+F4`` terminates environment.
* ``C`` change the illumination or environment?

Check keyboard input [table](https://carla.readthedocs.io/en/stable/simulator_keyboard_input/)



To change the environment variable initializations

We need to prepare a ``ini`` format file:

```
NumberOfVehicles=60
NumberOfPedestrians=60
WeatherId=3
```

To initialize the environment with customized variable values:

```bash
$ ./CarlaUE4.sh -carla-settings=Example.CarlaSettings.ini
```


### Collect Data


First start the Carla Python control script. Need ``autopilot`` to make sure the car runs well.

```bash
python client_semantic_segmentation.py --autopilot --images-to-disk
```

Then start the Carla environment and make sure that it is in the ``carla-server`` mode.


```bash
./CarlaUE4.sh -windowed -ResX=513 -ResY=513 -carla-server
```


#### Examples


```bash
python client_semantic_segmentation.py --autopilot --images-to-disk --images-to-disk-frequency 1 --quality-level Epic --number-of-episodes 50 --frames-per-episode 1000
```

```bash
./CarlaUE4.sh -windowed -ResX=513 -ResY=513 -carla-server -carla-settings=SemanticSegmentation.CarlaSettings.ini
```


