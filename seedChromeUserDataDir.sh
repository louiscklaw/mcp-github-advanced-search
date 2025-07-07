#!/usr/bin/env bash

set -ex

~/.cache/ms-playwright/chromium-1179/chrome-linux/chrome \
  --user-data-dir=~/mcp/mcp-git-gas/_user_data_dir

echo "seed done"
