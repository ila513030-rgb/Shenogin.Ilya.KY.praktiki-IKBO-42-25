#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
printf 'exit\n' | python3 -m src.main --script tests/startup_basic.txt
