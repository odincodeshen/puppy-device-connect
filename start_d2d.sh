#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVICE_PROFILE="${DEVICE_PROFILE:-puppypi}"
PROFILE_FILE="${PROFILE_FILE:-${SCRIPT_DIR}/profiles/${DEVICE_PROFILE}.env}"

if [[ ! -r "${PROFILE_FILE}" ]]; then
  echo "Profile file not found or unreadable: ${PROFILE_FILE}" >&2
  echo "Set DEVICE_PROFILE=puppypi, DEVICE_PROFILE=rpi5, or PROFILE_FILE=/path/to/profile.env." >&2
  exit 2
fi

set -a
source "${PROFILE_FILE}"
set +a

: "${PROJECT_ROOT:?profile must set PROJECT_ROOT}"

cd "${PROJECT_ROOT}"

source "${VENV_DIR:-venv}/bin/activate"

export DEVICE_CONNECT_ALLOW_INSECURE="${DEVICE_CONNECT_ALLOW_INSECURE:-true}"
export DEVICE_CONNECT_DISCOVERY_MODE="${DEVICE_CONNECT_DISCOVERY_MODE:-d2d}"
export MESSAGING_BACKEND="${MESSAGING_BACKEND:-zenoh}"
export ZENOH_LISTEN="${ZENOH_LISTEN:-tcp/0.0.0.0:7447}"
export DEVICE_ID="${DEVICE_ID:-${DEVICE_PROFILE}-d2d}"

exec python "${PROJECT_ROOT}/puppy-device-connect/puppypi_readonly_device.py"
