#!/bin/sh
set -eu

shutdown() {
    lms server stop || true
    lms daemon down || true
}

trap shutdown EXIT
trap 'exit 0' TERM INT

lms daemon up
lms server start --bind 0.0.0.0 --port 1234

while curl --fail --silent --max-time 3 --output /dev/null http://127.0.0.1:1234/api/v1/models; do
    sleep 5 &
    wait "$!"
done

exit 1
