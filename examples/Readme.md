Following https://fastapi.tiangolo.com/deployment/docker/

Setting up the container.
```bash
docker build -t joatom/apiserver .

docker run --name apiserver -p 8555:80 -v ~/git_repos/training-observer/api/app:/app joatom/apiserver

```
docker run --name examples -it --network=host --shm-size=2gb -p 8809:8889 -p 8808:8888 -v ~/.gitconfig:/etc/gitconfig -v ~/git_repos:/home/git_repos --gpus all joatom/ml