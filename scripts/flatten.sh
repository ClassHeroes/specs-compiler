#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

readonly LOG_FILE="/tmp/$(basename "$0").log"
info()    { echo "[INFO]    $*" | tee -a "$LOG_FILE" >&2 ; }
warning() { echo "[WARNING] $*" | tee -a "$LOG_FILE" >&2 ; }
error()   { echo "[ERROR]   $*" | tee -a "$LOG_FILE" >&2 ; }
fatal()   { echo "[FATAL]   $*" | tee -a "$LOG_FILE" >&2 ; exit 1 ; }

flatten() {
    local input=$1
    local full_filename=$(basename "$1")
    local filename=${full_filename%%.*}
    local output_folder=$2
    local output_file="$output_folder/$filename.yml"

    info "Flattening $input to $output_file"
    python3 -m swag.flattener "$input" > "$output_file"
}

main() {
    local output=$1
    local input=$2
    local pattern=${3:-}
    local files=$(find "$input" -regex "^[^.]*$pattern\.yml" -maxdepth 1 | sort)

    mkdir -p "$output"
    for f in $files
    do
        flatten "$f" "$output"
    done
}

if [[ "${BASH_SOURCE[0]}" = "$0" ]]; then
    main "$@"
fi
