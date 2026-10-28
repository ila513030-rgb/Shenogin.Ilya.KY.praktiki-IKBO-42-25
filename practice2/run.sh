#!/bin/sh
cd "$(dirname "$0")/.."
exec python3 -m practice2.src.main "$@"
