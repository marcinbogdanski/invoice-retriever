#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
profile_dir="${repo_root}/data/chrome-profile"

mkdir -p "${profile_dir}"

exec google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="${profile_dir}"
