#!/bin/bash
set -euo pipefail

# TODO: Output to log file
# TODO: Add debug flag

USAGE="USAGE: flow.sh AUDIO_FILE OUTPUT_FILE"
GOOGLE_CLOUD_TMP_FILE_NAME="integration-test-input-file.wav"

# HELPER FUNCS
error() {
	local p_lineno="$1"
	local msg="$2"
	local code="${3:-1}"
	if [[ -n "$msg" ]] ; then
		echo "Error on or near line ${p_lineno}: ${msg}; exiting with status ${code}"
	else
		echo "Error on or near line ${p_lineno}; exiting with status ${code}"
	fi
	exit "${code}"
}

# CHECK PARAMS
[[ "$#" != "1" ]] && error ${LINENO} "$USAGE"

[[ ! -f "$1" ]] && error ${LINENO} "File does not exist: $1"
audio_file=$(realpath "$1")

outfile="$(basename -- "$1" ".${1##*.}").out"
if [[ -f "$outfile" ]] ; then
	read -p "File \"$outfile\" already exists. Overwrite? [yN] " overwrite
else
	overwrite="y"
fi
output=""

tmpdir=$(mktemp -d)
trap "rm -rf $tmpdir" EXIT

. "../memo-journal/bin/activate"

# 1. Convert audio file to .wav
echo "Converting $audio_file to WAV.."
ffmpeg -y -hide_banner -loglevel error -i "$audio_file" -ac 1 "${tmpdir}/converted-wav.wav"
mv "${tmpdir}/converted-wav.wav" "${tmpdir}/converted-wav"

# 2. Upload to GS
echo "Uploading file to Google Cloud Storage Bucket.."
python3 ../speech2text/gs-upload.test.py "${tmpdir}/converted-wav" "$GOOGLE_CLOUD_TMP_FILE_NAME" >/dev/null

# 3. Perform S2T
echo "Processing speech to text.."
python3 ../speech2text/s2t-gs-v2.test.py "$GOOGLE_CLOUD_TMP_FILE_NAME" > "${tmpdir}/s2t.out"

# 4. Pipe into GPT and get a summary
echo "Summarizing journal.."
python3 ../text-analysis/gpt-test.py "${tmpdir}/s2t.out" > "${tmpdir}/gpt.out"

if [[ "${overwrite:-N}" = "y" ]] ; then
	cat "${tmpdir}/s2t.out" > "$outfile"
	echo >> "$outfile"
	cat "${tmpdir}/gpt.out" >> "$outfile"
else
	cat "${tmpdir}/s2t.out" "${tmpdir}/gpt.out"
fi

