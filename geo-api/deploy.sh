#!/bin/bash -e

ARGUMENT_LIST=(
    "stage"
    "profile"
)


# read arguments
opts=$(getopt \
    --longoptions "$(printf "%s:," "${ARGUMENT_LIST[@]}")" \
    --name "$(basename "$0")" \
    --options "" \
    -- "$@"
)

eval set --$opts

while [[ $# -gt 0 ]]; do
    case "$1" in
        --stage)
            stage=$2
            shift 2
            ;;

        --profile)
            profile=$2
            shift 2
            ;;

        *)
            break
            ;;
    esac
done
stage=${stage:-dev}
profile=${profile:-geo-api-deploy-dev}

serverless deploy --stage $stage --profile $profile
serverless downloadDocumentation  --stage $stage --profile $profile --outputFileName=static/swagger/oas.json

python3 <<EOF
print("Fixing openapi spec")
import json
with open('static/swagger/oas.json') as json_file:
    data = json.load(json_file)

# Fix title, aws ignores what's been set by serverless
data['info']['title'] = "geo-api-$stage"

# Remove all options request as they fail to validate due to pathParams
for path in data['paths'].keys():
    if "options" in data['paths'][path]:
        del data['paths'][path]['options']

with open('static/swagger/oas.json', 'w') as outfile:
    json.dump(data, outfile)

print("Fixed openapi spec")
EOF

serverless client deploy --stage $stage --profile $profile --no-confirm
rm static/swagger/oas.json
