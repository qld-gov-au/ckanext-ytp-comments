#!/usr/bin/env sh
##
# Create some example content for extension BDD tests.
#
set -e

export CKAN_ACTION_URL=http://ckan:3000/api/action
export CKAN_INI_FILE=/app/ckan/default/production.ini

. /app/ckan/default/bin/activate \
    && cd /app/ckan/default/src/ckan

# We know the "admin" sysadmin account exists, so we'll use her API KEY to create further data
export API_KEY=$(paster --plugin=ckan user admin -c ${CKAN_INI_FILE} | tr -d '\n' | sed -r 's/^(.*)apikey=(\S*)(.*)/\2/')

##
# BEGIN: Create a Salsa Digital organisation with test users for admin, editor and member
#
SALSA_ORG_NAME=salsa-digital
SALSA_ORG_TITLE="Salsa Digital"

echo "Creating test users for ${SALSA_ORG_TITLE} Organisation:"

paster --plugin=ckan user add ckan_user email=ckan_user@localhost password=password -c ${CKAN_INI_FILE}
paster --plugin=ckan user add salsa_admin email=salsa_admin@localhost password=password -c ${CKAN_INI_FILE}
paster --plugin=ckan user add salsa_editor email=salsa_editor@localhost password=password -c ${CKAN_INI_FILE}
paster --plugin=ckan user add salsa_member email=salsa_member@localhost password=password -c ${CKAN_INI_FILE}

echo "Creating ${SALSA_ORG_TITLE} Organisation:"

SALSA_ORG=$( \
    wget -O- --header="Authorization: ${API_KEY}" \
    --post-data "name=${SALSA_ORG_NAME}&title=${SALSA_ORG_TITLE}" \
    ${CKAN_ACTION_URL}/organization_create
)

SALSA_ORG_ID=$(echo $SALSA_ORG | sed -r 's/^(.*)"id": "(.*)",(.*)/\2/')

echo "Assigning test users to ${SALSA_ORG_TITLE} Organisation:"

wget -O- --header="Authorization: ${API_KEY}" \
    --post-data "id=${SALSA_ORG_ID}&object=salsa_admin&object_type=user&capacity=admin" \
    ${CKAN_ACTION_URL}/member_create

wget -O- --header="Authorization: ${API_KEY}" \
    --post-data "id=${SALSA_ORG_ID}&object=salsa_editor&object_type=user&capacity=editor" \
    ${CKAN_ACTION_URL}/member_create

wget -O- --header="Authorization: ${API_KEY}" \
    --post-data "id=${SALSA_ORG_ID}&object=salsa_member&object_type=user&capacity=member" \
    ${CKAN_ACTION_URL}/member_create

# Use CKAN's built-in paster command for creating some test datasets...
paster create-test-data -c ${CKAN_INI_FILE}

# Datasets need to be assigned to an organisation

echo "Assigning test Datasets to Organisation..."

wget -q -O- --header="Authorization: ${API_KEY}" \
    --post-data "id=annakarenina&owner_org=${SALSA_ORG_ID}" \
    ${CKAN_ACTION_URL}/package_patch >> /dev/null

wget -q -O- --header="Authorization: ${API_KEY}" \
    --post-data "id=warandpeace&owner_org=${SALSA_ORG_ID}" \
    ${CKAN_ACTION_URL}/package_patch >> /dev/null
##
# END.
#

# Data Requests requires a specific organisation to exist in order to create DRs for Data.Qld
TEST_ORG_NAME=open-data-administration-data-requests
TEST_ORG_TITLE="Open Data Administration (data requests)"

echo "Creating Data Request Organisation:"

TEST_ORG=$( \
    wget -O- \
    --header="Authorization: ${API_KEY}" \
    --post-data "name=${TEST_ORG_NAME}&title=${TEST_ORG_TITLE}" \
    ${CKAN_ACTION_URL}/organization_create
)

echo $TEST_ORG

# Get the ID of that newly created Organisation
TEST_ORG_ID=$(echo $TEST_ORG | sed -r 's/^(.*)"id": "(.*)",(.*)/\2/')

echo "Creating test Data Request:"

wget -O- --header="Authorization: ${API_KEY}" \
    --post-data "title=Test Request&description=This is an example&organization_id=${TEST_ORG_ID}" \
    ${CKAN_ACTION_URL}/create_datarequest

deactivate
