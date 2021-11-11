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

echo "Creating comment tables..."
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli comments initdb
echo "Adding deletion metadata fields..."
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli comments updatedb
echo "Adding comment notification tables..."
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli comments init_notifications_db

# Create some base test data
. $APP_DIR/scripts/create-test-data.sh
