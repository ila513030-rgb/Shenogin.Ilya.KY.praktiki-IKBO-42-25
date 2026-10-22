#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
for name in minimal multiple nested; do
  printf 'exit\n' | python3 -m src.main \
    --vfs "tests/vfs/$name.json" \
    --script tests/startup_all.txt
done
