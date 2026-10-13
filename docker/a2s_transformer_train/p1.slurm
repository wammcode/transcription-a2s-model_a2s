#!/usr/bin/env bash
#SBATCH --job-name=a2s-quartets
#SBATCH --output=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s/docker/a2s_transformer/%x-%j.out
#SBATCH --error=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s/docker/a2s_transformer/%x-%j.err
#SBATCH --chdir=/home/grfia/wilson/project_2026_1/transcription-a2s-model_a2s
#SBATCH --cpus-per-task=6
#SBATCH --mem=20G
#SBATCH --partition=bacterio
#SBATCH --gres=gpu:1

set -euo pipefail

# SLURM executes a copy of this script from /var/spool; BASH_SOURCE is not
# the repository path. --chdir above supplies the project root instead.
project_root="$(pwd -P)"
model_dir="$project_root/a2s-transformer"
data_dir="$project_root/data/data_quartets/Quartets"
docker_dir="$project_root/docker/a2s_transformer"
image_name="a2s-transformer:quartets-${SLURM_JOB_ID:-local}"

for split in train val test; do
    test -s "$data_dir/a2s_partitions/quartets/$split.txt" || {
        echo "Falta el manifiesto $split en $data_dir/a2s_partitions/quartets" >&2
        exit 1
    }
done
test -d "$data_dir/wav" && test -d "$data_dir/krn_clean" || {
    echo "Faltan los directorios wav o krn_clean en $data_dir" >&2
    exit 1
}

gpu_device="${SLURM_JOB_GPUS:-${CUDA_VISIBLE_DEVICES:-}}"
if [[ -z "$gpu_device" ]]; then
    echo "No se ha asignado una GPU (SLURM_JOB_GPUS/CUDA_VISIBLE_DEVICES)." >&2
    exit 1
fi

mkdir -p "$model_dir/weights" "$model_dir/wandb" "$model_dir/logs"
echo "Entrenamiento A2S Quartets en $(hostname), $(date)"
echo "GPU: $gpu_device"

docker build -t "$image_name" "$docker_dir"
if ! docker image inspect "$image_name" >/dev/null 2>&1; then
    echo "La imagen $image_name no se construyó; revise el error de docker build en este registro." >&2
    exit 1
fi
completion_marker="$model_dir/logs/a2s-quartets-${SLURM_JOB_ID:-local}.complete"
rm -f "$completion_marker"
docker run --rm --name "a2s-quartets-${SLURM_JOB_ID:-local}" \
    --gpus "device=$gpu_device" \
    --shm-size=8g \
    --user "$(id -u):$(id -g)" \
    --mount "type=bind,src=$model_dir,dst=/workspace/a2s-transformer" \
    --mount "type=bind,src=$data_dir,dst=/workspace/data/data_quartets/Quartets" \
    --workdir /workspace/a2s-transformer \
    --env WANDB_MODE=offline \
    --env WANDB_DIR=/workspace/a2s-transformer/wandb \
    --env HOME=/tmp \
    --env MPLCONFIGDIR=/tmp/a2s-matplotlib \
    --env "A2S_FINISH_MARKER=/workspace/a2s-transformer/logs/$(basename "$completion_marker")" \
    "$image_name" bash -e -c 'python -u train.py "$@" && touch "$A2S_FINISH_MARKER"' -- \
        --task a2s \
        --model_type transformer \
        --ds_name quartets \
        --data_root ../data/data_quartets/Quartets \
        --partitions_dir a2s_partitions \
        --audio_dir wav \
        --audio_extension .wav \
        --score_dir krn_clean \
        --token_normalization clean \
        --batch_size 16 \
        --eval_batch_size 16 \
        --num_workers 4 \
        --attn_window 100 \
        --epochs 1000 \
        --patience 5 \
        --check_val_every_n_epoch 5

if [[ ! -f "$completion_marker" ]]; then
    echo "El entrenamiento no terminó correctamente; revise el error de docker run en este registro." >&2
    exit 1
fi
echo "Entrenamiento terminado: $(date)"
