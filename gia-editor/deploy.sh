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

npm install -g serverless
npm install
npm run build
serverless client deploy --stage $stage --profile $profile --no-confirm
