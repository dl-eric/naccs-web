docker build -t naccs_image .
docker stop naccs
docker rm naccs
docker run --env-file ./env.list -d --name naccs -p 80:80 naccs_image
