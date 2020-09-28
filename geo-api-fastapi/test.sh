#! /usr/bin/env sh

# Exit in case of error
set -e

docker-compose -f docker-test-stack.yml build
docker-compose -f docker-test-stack.yml down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker-compose -f docker-test-stack.yml up -d
docker-compose -f docker-test-stack.yml exec -T backend bash /app/scripts/lint.sh
docker-compose -f docker-test-stack.yml exec -T backend bash /app/tests-start.sh
docker-compose -f docker-test-stack.yml down -v --remove-orphans
