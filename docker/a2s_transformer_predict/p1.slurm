#!/usr/bin/env bash
#SBATCH --job-name=a2s-quartets-predict
#SBATCH --output=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s/docker/a2s_transformer_predict/%x-%j.out
#SBATCH --error=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s/docker/a2s_transformer_predict/%x-%j.err
#SBATCH --chdir=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s
#SBATCH --cpus-per-task=6
#SBATCH --mem=20G
#SBATCH --partition=bacterio
#SBATCH --gres=gpu:1
#SBATCH --time=5-00:00:00

set -euo pipefail

project_root="$(pwd -P)"
model_dir="$project_root/a2s-transformer"
data_dir="$project_root/data/data_quartets/Quartets"
docker_dir="$project_root/docker/a2s_transformer_predict"
checkpoint="$model_dir/weights/transformer-VCT/quartets.ckpt"
manifest="$data_dir/a2s_partitions/quartets/test.txt"
output_dir="$model_dir/predict/quartets/krn"
image_name="a2s-transformer:quartets-predict-${SLURM_JOB_ID}"
completion_marker="$model_dir/logs/a2s-quartets-predict-${SLURM_JOB_ID}.complete"

test -s "$checkpoint" && test -s "$manifest" && test -d "$data_dir/wav" && test -d "$data_dir/krn_clean"
gpu_device="${SLURM_JOB_GPUS:-${CUDA_VISIBLE_DEVICES:-}}"
if [[ -z "$gpu_device" ]]; then
    echo "No se ha asignado una GPU (SLURM_JOB_GPUS/CUDA_VISIBLE_DEVICES)." >&2
    exit 1
fi

mkdir -p "$output_dir" "$model_dir/logs"
rm -f "$completion_marker"
echo "Prediccion A2S Quartets en $(hostname), $(date)"
echo "GPU: $gpu_device; checkpoint: $checkpoint; manifiesto: $manifest"

docker build -t "$image_name" "$docker_dir"
docker image inspect "$image_name" >/dev/null
docker run --rm --name "a2s-quartets-predict-${SLURM_JOB_ID}" \
    --gpus "device=$gpu_device" \
    --shm-size=8g \
    --user "$(id -u):$(id -g)" \
    --mount "type=bind,src=$model_dir,dst=/workspace/a2s-transformer" \
    --mount "type=bind,src=$data_dir,dst=/workspace/data/data_quartets/Quartets,readonly" \
    --workdir /workspace/a2s-transformer \
    --env HOME=/tmp \
    --env MPLCONFIGDIR=/tmp/a2s-matplotlib \
    --env OMP_NUM_THREADS=6 \
    "$image_name" python -u predict.py \
        --checkpoint weights/transformer-VCT/quartets.ckpt \
        --data_root ../data/data_quartets/Quartets \
        --output_dir predict/quartets/krn \
        --ds_name quartets \
        --split test \
        --audio_dir wav \
        --audio_extension .wav \
        --score_dir krn_clean \
        --partitions_dir a2s_partitions \
        --accelerator gpu \
        --skip_existing True \
        --use_cache True

# Check the requested result, rather than treating process exit alone as success.
python - "$manifest" "$output_dir" <<'PY'
from pathlib import Path
import sys

manifest, output_dir = map(Path, sys.argv[1:])
audios = [line.split("\t", 1)[0] for line in manifest.read_text().splitlines()
          if line.strip() and not line.lstrip().startswith("#")]
expected = {output_dir / Path(audio).with_suffix(".krn") for audio in audios}
missing = [path for path in expected if not path.is_file() or path.stat().st_size == 0]
print(f"Predicciones Kern: {len(expected) - len(missing)}/{len(expected)}", flush=True)
if missing:
    print(f"Falta {missing[0]}", file=sys.stderr)
    sys.exit(1)
PY
touch "$completion_marker"
echo "Prediccion terminada: $(date)"
