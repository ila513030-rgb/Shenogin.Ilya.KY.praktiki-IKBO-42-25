#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
printf 'exit\n' | python3 -m src.main --vfs tests/vfs/invalid.json
printf 'exit\n' | python3 -m src.main --vfs tests/vfs/missing.json
printf 'exit\n' | python3 -m src.main --script tests/missing.txt
