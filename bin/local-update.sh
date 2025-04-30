#!/usr/bin/env bash

export CKAN_VERSION="2.11"
export PYTHON_VERSION=py3
export PYTHON=python3
export SOLR_VERSION=9

function cli {
  CKAN_CONTAINER=$(sh bin/docker-compose.sh ps -q ckan)
      if [ "${#}" -ne 0 ]; then
        docker exec $CKAN_CONTAINER sh -c '. "${APP_DIR}"/bin/activate; cd $APP_DIR;'" $*"
      else
        docker exec $CKAN_CONTAINER sh -c '. "${APP_DIR}"/bin/activate && cd $APP_DIR && sh'
      fi
}

function copy {
  CKAN_CONTAINER=$(sh bin/docker-compose.sh ps -q ckan)
  docker cp . $CKAN_CONTAINER:/srv/app

}


copy
echo "copy done"
cli "pip install -e ."

#cli "/srv/app/bin/serve.sh"