# Semantic Segmentation CARLA

Lei Mao

University of Chicago

## CARLA Instructions

The experience are gained from using CARLA 0.8.2.

### Start CARLA

To start CARLA in a window with customized resolution.


```bash
$ ./CarlaUE4.sh -windowed -ResX=512 -ResY=512
```



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