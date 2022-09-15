#!/usr/bin/env sh
##
# Initialise CKAN data for testing.
#
set -e

. ${APP_DIR}/bin/activate
CLICK_ARGS="--yes" ckan_cli db clean
ckan_cli db init
ckan_cli db upgrade

echo "Creating comment tables..."
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli comments initdb
echo "Adding deletion metadata fields..."
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli comments updatedb
echo "Adding comment notification tables..."
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli comments init_notifications_db

# Create some base test data
. $APP_DIR/bin/create-test-data.sh
