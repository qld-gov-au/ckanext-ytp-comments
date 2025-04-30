#!/usr/bin/env sh
set -e

. "${APP_DIR}"/bin/activate
if (which ckan > /dev/null); then
    ckan -c ${CKAN_INI} run --threaded
else
    paster serve ${CKAN_INI}
fi
