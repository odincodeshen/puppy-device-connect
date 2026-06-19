#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/home/odin/device-connect}"
cd "${PROJECT_ROOT}"

source "${VENV_DIR:-.venv}/bin/activate"

export DEVICE_CONNECT_ALLOW_INSECURE="${DEVICE_CONNECT_ALLOW_INSECURE:-true}"
export DEVICE_CONNECT_DISCOVERY_MODE="${DEVICE_CONNECT_DISCOVERY_MODE:-d2d}"
export MESSAGING_BACKEND="${MESSAGING_BACKEND:-zenoh}"
export ZENOH_LISTEN="${ZENOH_LISTEN:-tcp/0.0.0.0:7447}"
export DEVICE_TYPE="${DEVICE_TYPE:-quadruped}"

exec python "${PROJECT_ROOT}/puppypi-connect/puppypi_readonly_device.py"
