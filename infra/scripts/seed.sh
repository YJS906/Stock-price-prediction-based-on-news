#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://localhost:8000/api/v1/admin/seed/reset

