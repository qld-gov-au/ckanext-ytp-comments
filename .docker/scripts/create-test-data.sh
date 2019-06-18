#!/usr/bin/env sh
##
# Create some example content for extension BDD tests.
#
set -e

CKAN_ACTION_URL=http://ckan:3000/api/action
CKAN_INI_FILE=/app/ckan/default/production.ini

. /app/ckan/default/bin/activate \
    && cd /app/ckan/default/src/ckan

# Use CKAN's built-in paster command for creating some test datasets...
paster create-test-data -c $CKAN_INI_FILE

# We know the "admin" sysadmin account exists, so we'll use her API KEY to create further data
API_KEY=$(paster --plugin=ckan user admin -c ${CKAN_INI_FILE} | tr -d '\n' | sed -r 's/^(.*)apikey=(\S*)(.*)/\2/')

# Data Requests requires a specific organisation to exist in order to create DRs for Data.Qld
TEST_ORG_NAME=open-data-administration-data-requests
TEST_ORG_TITLE="Open Data Administration (data requests)"

echo "Creating Data Request Organisation:"

TEST_ORG=$( \
    wget -O- \
    --header="Authorization: ${API_KEY}" \
    --post-data "name=${TEST_ORG_NAME}&title=${TEST_ORG_TITLE}" \
    ${CKAN_ACTION_URL}/organization_create \
)

echo $TEST_ORG

# Get the ID of that newly created Organisation
TEST_ORG_ID=$(echo $TEST_ORG | sed -r 's/^(.*)"id": "(.*)",(.*)/\2/')

echo "Creating test Data Request:"

wget -O- --header="Authorization: ${API_KEY}" \
    --post-data "title=Test Request&description=This is an example&organization_id=${TEST_ORG_ID}" \
    ${CKAN_ACTION_URL}/create_datarequest

deactivate
