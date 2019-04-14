docker build -t naccs_image .
docker stop naccs || true
docker rm naccs || true
docker run --env-file ./env.list -d --name naccs -p 80:80 -p 443:443 naccs_image
