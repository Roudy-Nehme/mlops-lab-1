quest 1:

My model was registered as version 1. A logged model belongs to one run, while a registered model gives it a name and version so it’s easier to manage.

quest 2:

MLflow now uses aliases instead of stages like Staging and Production. An alias such as champion can easily be moved from one model version to another.

quest 3:

Using models:/food11@champion means the code always loads the model marked as champion. To use a newer model, I only need to move the champion alias to the new version.

quest 4:

Docker installs the dependencies before copying the source code so it can reuse the cached dependency layer. If I only change serve.py, Docker does not need to reinstall everything.

quest 5:

The multi-stage image was about 1.99 GB, while the single-stage image was about 3.59 GB. The multi-stage image is smaller because build tools and the larger base image are not kept in the final image.

quest 6:

Without .dockerignore, Docker sends unnecessary files like data/, .venv/, and mlruns/, which makes builds slower and possibly larger. The Windows .venv could also cause compatibility problems inside the Linux container.

quest 7:

Inside the container, 127.0.0.1 refers to the container itself, not my PC. On Windows, host.docker.internal lets the container connect to the MLflow server running on the host.

In my setup, the MLflow model artifacts were stored locally in the host mlruns folder, so I also had to mount that folder into the container so the registered model files could be accessed at runtime.

quest 8:

Yes, the model still loaded when I started a new container without rebuilding the image. The code and dependencies are inside the image, while the model is loaded from MLflow at runtime.

quest 9:

The image currently only exists on my PC. To use it on another machine, I would need to push it to a container registry and use a specific version tag or image digest.
