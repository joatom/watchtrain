# ML watchtrain

## About
This repository contains code to stream ML training progress (currently only fastai) to a Fitbit Versa 3. 

<p align="left">
  <img src="docs/assets/img/logo_watchtrain1.png?raw=true" width="400" title="ML watchtrain">
</p>

The project consists of three components, which can be found in the respective folders:
- */api*: An API server that coordinates the communication between ML training and the watch.
- */fitbit*: Code that runs on the Fitbit Versa 3 to display the training progress received from the API server.
- */training*: A websocket logger that uses fastai's callback architecture to fetch training progress and metrics to send to the API server. The WebsocketLogger was heavily influenced by the original fastai [CSVLogger and Progress Callback](https://docs.fast.ai/callback.progress.html).

## How to run it

The */api* folder contains a Dockerfile that launches the API server. */fitbit* contains the code for the watch that can be deployed via [Fitbit Studio](https://studio.fitbit.com/). The API server address can be adjusted in the */fitbit/companion/index.js*. A running example on how to use the fastai Callback from */training* can be found in the *example_fastai_training.ipynb* notebooks.


> The watch, the API server and the training scripts should run in the same network, if run locally. On a local net the subnet mask needs to be 192.168.0.*. Alternatively the API server needs to run on a trusted HTTPS host. (see [blog post](https://joatom.github.io/ai_curious/api/websockets/ml%20logging/fastai%20callbacks/2021/06/19/watchtrain.html))

# References
- [Blog post](https://joatom.github.io/ai_curious/api/websockets/ml%20logging/fastai%20callbacks/2021/06/19/watchtrain.html) about this project
- Fastapi Docker setup: https://fastapi.tiangolo.com/deployment/docker/
- Fitbit IDE: https://studio.fitbit.com/
- Fastai CSVLogger and Progress Callback: https://docs.fast.ai/callback.progress.html