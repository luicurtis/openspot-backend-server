# openspot-backend-server

Repo for the backend server

When working on the project, you will need to activate the virtual environment:
```
source venv/bin/activate
```

To start the server:
``` 
cd backend/server && python manage.py runserver <IP>:port
```
- IP is found from by running: ``` ipconfig getifaddr en0 ```

## Library Versions:
Note: Install libraries in the order given

### opencv-python:
- opencv-python          4.2.0.34

### mrcnn
- mrcnn                  0.2

### Keras:
- Keras                   2.4.3
- Keras-Applications      1.0.8
- keras-nightly           2.5.0.dev2021032900
- Keras-Preprocessing     1.1.2

### tensorflow
- tensorflow             2.5.0
- tensorflow-estimator   2.5.0

### Shapely
``` pip install Shapely ```

## Common Errors
AttributeError: module 'tensorflow' has no attribute 'log': https://github.com/matterport/Mask_RCNN/issues/1797

