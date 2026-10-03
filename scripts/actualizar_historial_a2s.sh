#!/usr/bin/env bash

# Actualiza la copia recuperable del historial de a2s-transformer.
set -euo pipefail

raiz="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
repositorio_a2s="$raiz/a2s-transformer"
directorio_control="$raiz/control_version"
bundle="$directorio_control/a2s-transformer.bundle"

if ! git -C "$repositorio_a2s" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: no se encontró un repositorio Git en $repositorio_a2s." >&2
    exit 1
fi

mkdir -p "$directorio_control"
temporal="$(mktemp "$directorio_control/.a2s-transformer.XXXXXX.bundle")"
trap 'rm -f "$temporal"' EXIT

git -C "$repositorio_a2s" bundle create "$temporal" --all
git bundle verify "$temporal" >/dev/null
mv -f "$temporal" "$bundle"
trap - EXIT

echo "Instantánea actualizada: $bundle"
echo "Commit principal: $(git -C "$repositorio_a2s" rev-parse HEAD)"
