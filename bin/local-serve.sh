#!/usr/bin/env bash


function cli {
  CKAN_CONTAINER=$(sh bin/docker-compose.sh ps -q ckan)
      if [ "${#}" -ne 0 ]; then
        docker exec $CKAN_CONTAINER sh -c '. "${APP_DIR}"/bin/activate; cd $APP_DIR;'" $*"
      else
        docker exec $CKAN_CONTAINER sh -c '. "${APP_DIR}"/bin/activate && cd $APP_DIR && sh'
      fi
}

# Process Docker Compose configuration. This is used to avoid multiple
# docker-compose.yml files.
# Remove lines containing '###'.
sed -i -e "/###/d" docker-compose.yml
# Uncomment lines containing '##'.
sed -i -e "s/##//" docker-compose.yml

export CKAN_VERSION="2.11"
export PYTHON_VERSION=py3
export PYTHON=python3
export SOLR_VERSION=9

if [ "$CKAN_VERSION" = "2.9" ]; then
    SOLR_VERSION=8
fi

sed "s|{CKAN_VERSION}|$CKAN_VERSION|g" .docker/Dockerfile-template.ckan \
    | sed "s|{PYTHON_VERSION}|$PYTHON_VERSION|g" \
    | sed "s|{PYTHON}|$PYTHON|g" \
    > .docker/Dockerfile.ckan

#build-network
docker network prune -f > /dev/null
docker network inspect amazeeio-network > /dev/null || docker network create amazeeio-network

docker compose up -d --build
echo "Initialising database schema"
cli "/srv/app/bin/init.sh"
cli "/srv/app/bin/init-ext.sh"
#cli "ckan -c ${CKAN_INI} run --disable-reloader --threaded"
