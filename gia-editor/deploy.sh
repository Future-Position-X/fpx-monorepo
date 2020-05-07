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
profile=${profile:-default}

npm install -g serverless
npm install
npm run build
sudo -E sls config credentials --provider aws --key $AWS_ACCESS_KEY_ID --secret $AWS_SECRET_ACCESS_KEY --stage $stage --profile $profile
serverless client deploy --stage $stage --profile $profile --no-confirm
