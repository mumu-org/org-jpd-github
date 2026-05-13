slash-npm-virtual
slash-npm-stage-local
slash-npm-curation-remote

rm -rf node_modules package-lock.json

npm cache clean --force

npm install


docker build --platform linux/amd64 --build-arg JPD_URL=jfrog.local:32012 --build-arg NPM_AUTH_TOKEN=<token> -t app-npm:1.0.5 .

docker tag app-npm:1.0.5 jfrog.local:32012/slash-docker-virtual/app-npm:1.0.5
docker tag app-npm:1.0.5 demo.jfrogchina.com/slash-docker-virtual/app-npm:1.0.5

docker push jfrog.local:32012/slash-docker-virtual/app-npm:1.0.5


