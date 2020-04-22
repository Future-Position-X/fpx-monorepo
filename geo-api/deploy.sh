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
sed -i "s/\"title\" : \"$stage-geo-api\",/\"title\" : \"geo-api-$stage\",/g" static/swagger/oas.json
serverless client deploy --stage $stage --profile $profile --no-confirm
