#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/home/odin/device-connect}"
cd "${PROJECT_ROOT}"

source "${VENV_DIR:-.venv}/bin/activate"

export DEVICE_CONNECT_ALLOW_INSECURE="${DEVICE_CONNECT_ALLOW_INSECURE:-false}"
export MESSAGING_BACKEND="${MESSAGING_BACKEND:-nats}"
export MESSAGING_CREDENTIALS_FILE="${MESSAGING_CREDENTIALS_FILE:-${PROJECT_ROOT}/beta-puppypi.creds.json}"
export DEVICE_TYPE="${DEVICE_TYPE:-quadruped}"

exec python "${PROJECT_ROOT}/puppy-device-connect/puppypi_readonly_device.py"
