#!/usr/bin/env sh
##
# Initialise CKAN instance.
#
set -e


if [ "$VENV_DIR" != "" ]; then
  . ${VENV_DIR}/bin/activate
fi
CLICK_ARGS="--yes" ckan_cli db clean
ckan_cli db init

# Initialise the Comments database tables
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli comments initdb
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli comments updatedb
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli comments init_notifications_db

# Create some base test data
. $APP_DIR/scripts/create-test-data.sh
