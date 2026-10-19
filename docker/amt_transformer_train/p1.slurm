#!/usr/bin/env bash
#SBATCH --job-name=amt-quartets
#SBATCH --output=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s/docker/amt_transformer_train/%x-%j.out
#SBATCH --error=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s/docker/amt_transformer_train/%x-%j.err
#SBATCH --chdir=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s
#SBATCH --cpus-per-task=6
#SBATCH --mem=40G
#SBATCH --time=5-00:00:00
#SBATCH --partition=bacterio
#SBATCH --gres=gpu:1

set -euo pipefail

# Slurm runs a copied script from its spool directory. --chdir sets this root.
project_root="$(pwd -P)"
model_dir="$project_root/a2s-transformer"
data_dir="$project_root/data/data_quartets/Quartets"
docker_dir="$project_root/docker/amt_transformer_train"
image_name="amt-transformer:quartets-${SLURM_JOB_ID:?Run this script with sbatch}"
container_name="amt-quartets-${SLURM_JOB_ID}"
completion_marker="$model_dir/logs/${container_name}.complete"

for split in train val test; do
    test -s "$data_dir/amt_partitions/quartets/$split.txt" || {
        echo "Falta el manifiesto $split en $data_dir/amt_partitions/quartets" >&2
        exit 1
    }
done
test -d "$data_dir/wav" && test -d "$data_dir/midi" || {
    echo "Faltan los directorios wav o midi en $data_dir" >&2
    exit 1
}

gpu_device="${SLURM_JOB_GPUS:-${CUDA_VISIBLE_DEVICES:-}}"
if [[ -z "$gpu_device" ]]; then
    echo "Slurm no ha asignado una GPU." >&2
    exit 1
fi

mkdir -p "$model_dir/weights/transformer-AMT" "$model_dir/wandb" "$model_dir/logs"
rm -f "$completion_marker"
echo "Entrenamiento AMT Quartets en $(hostname), $(date)"
echo "GPU asignada: $gpu_device"

docker build -t "$image_name" "$docker_dir"
docker image inspect "$image_name" >/dev/null
docker run --rm --name "$container_name" \
    --gpus "device=$gpu_device" \
    --shm-size=8g \
    --user "$(id -u):$(id -g)" \
    --mount "type=bind,src=$model_dir,dst=/workspace/a2s-transformer" \
    --mount "type=bind,src=$data_dir,dst=/workspace/data/data_quartets/Quartets" \
    --workdir /workspace/a2s-transformer \
    --env WANDB_MODE=offline \
    --env WANDB_DIR=/workspace/a2s-transformer/wandb \
    --env HOME=/tmp \
    --env MPLCONFIGDIR=/tmp/amt-matplotlib \
    --env "AMT_FINISH_MARKER=/workspace/a2s-transformer/logs/$(basename "$completion_marker")" \
    "$image_name" bash -e -c 'python -u train.py "$@" && touch "$AMT_FINISH_MARKER"' -- \
        --task amt \
        --model_type transformer \
        --ds_name quartets \
        --data_root ../data/data_quartets/Quartets \
        --partitions_dir amt_partitions \
        --audio_dir wav \
        --audio_extension .wav \
        --midi_dir midi \
        --midi_extension .midi \
        --batch_size 8 \
        --num_workers 4 \
        --max_seq_len 1024 \
        --attn_window 100 \
        --epochs 1000 \
        --patience 5 \
        --check_val_every_n_epoch 5

test -f "$completion_marker" || {
    echo "El entrenamiento no terminó correctamente; revise el registro del trabajo." >&2
    exit 1
}
echo "Entrenamiento terminado: $(date)"
