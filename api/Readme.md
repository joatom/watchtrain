Following https://fastapi.tiangolo.com/deployment/docker/

Setting up the container.
```bash
docker build -t joatom/apiserver .

docker run --name apiserver -p 8555:80 -v ~/git_repos/training-observer/api/app:/app joatom/apiserver

```
