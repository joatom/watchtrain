Following https://fastapi.tiangolo.com/deployment/docker/

Setting up the container.

```bash
docker build -t joatom/apiserver .

docker run --name apiserver -p 8555:80 -v /<local_git_repos>/watchtrain/api/app:/app joatom/apiserver
```
