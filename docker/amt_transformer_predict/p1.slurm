#!/usr/bin/env bash
#SBATCH --job-name=amt-quartets-predict
#SBATCH --output=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s/docker/amt_transformer_predict/%x-%j.out
#SBATCH --error=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s/docker/amt_transformer_predict/%x-%j.err
#SBATCH --chdir=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s
#SBATCH --cpus-per-task=6
#SBATCH --mem=40G
#SBATCH --time=5-00:00:00
#SBATCH --partition=bacterio
#SBATCH --gres=gpu:1

set -euo pipefail

project_root="$(pwd -P)"
model_dir="$project_root/a2s-transformer"
data_dir="$project_root/data/data_quartets/Quartets"
docker_dir="$project_root/docker/amt_transformer_predict"
checkpoint="$model_dir/weights/transformer-AMT/quartets.ckpt"
manifest="$data_dir/amt_partitions/quartets/test.txt"
output_dir="$model_dir/predict/quartets/midi"
image_name="amt-transformer-predict:quartets-${SLURM_JOB_ID:?Run this script with sbatch}"
container_name="amt-quartets-predict-${SLURM_JOB_ID}"
completion_marker="$model_dir/logs/${container_name}.complete"

test -s "$checkpoint" || { echo "Falta el checkpoint $checkpoint" >&2; exit 1; }
test -s "$manifest" || { echo "Falta el manifiesto $manifest" >&2; exit 1; }
test -d "$data_dir/wav" && test -d "$data_dir/midi" || {
    echo "Faltan los directorios wav o midi en $data_dir" >&2
    exit 1
}

gpu_device="${SLURM_JOB_GPUS:-${CUDA_VISIBLE_DEVICES:-}}"
if [[ -z "$gpu_device" ]]; then
    echo "Slurm no ha asignado una GPU." >&2
    exit 1
fi

mkdir -p "$output_dir" "$model_dir/logs"
rm -f "$completion_marker"
echo "Predicción AMT Quartets en $(hostname), $(date)"
echo "GPU asignada: $gpu_device"
echo "Checkpoint: $checkpoint"
echo "Manifiesto: $manifest"
echo "Salida: $output_dir"

docker build -t "$image_name" "$docker_dir"
docker image inspect "$image_name" >/dev/null
docker run --rm --name "$container_name" \
    --gpus "device=$gpu_device" \
    --shm-size=8g \
    --user "$(id -u):$(id -g)" \
    --mount "type=bind,src=$model_dir,dst=/workspace/a2s-transformer" \
    --mount "type=bind,src=$data_dir,dst=/workspace/data/data_quartets/Quartets" \
    --workdir /workspace/a2s-transformer \
    --env HOME=/tmp \
    --env MPLCONFIGDIR=/tmp/amt-matplotlib \
    "$image_name" python -u predict_amt.py \
        --checkpoint weights/transformer-AMT/quartets.ckpt \
        --data_root ../data/data_quartets/Quartets \
        --output_dir predict/quartets/midi \
        --ds_name quartets \
        --split test \
        --partitions_dir amt_partitions \
        --audio_dir wav \
        --audio_extension .wav \
        --midi_dir midi \
        --midi_extension .midi \
        --accelerator gpu \
        --skip_existing True \
        --use_cache True

touch "$completion_marker"
echo "Predicción terminada: $(date)"
