#!/bin/bash
#SBATCH --job-name=docker          # Nombre del trabajo
#SBATCH --output=%j.out         # Nombre del archivo de salida
#SBATCH --error=%j.err          # Nombre del archivo de error
#SBATCH --cpus-per-task=6            # Número de CPUs por tarea
#SBATCH --mem=20G                      # Memoria por nodo
#SBATCH --partition=bacterio           # Cola (partición) a la que enviar el trabajo
#SBATCH --gres=gpu:1

# Aquí empieza la sección de comandos que se van a ejecutar

echo "Iniciando trabajo en `hostname` a las `date` $SLURM_IDX"
nvidia-smi

# Define la ruta al directorio de trabajo
R="/home/grfia/wilson/project_2025_2/A2S/code/transformer_asap/a2s-transformer"
# Define el comando a ejecutar
#coman="python /project_2025_2/AMT/code/bytedance/piano_transcription/pytorch/main.py train --workspace /project_2025_2/AMT/code/bytedance/piano_transcription --model_type=Regress_onset_offset_frame_velocity_CRNN --loss_type=regress_onset_offset_frame_velocity_bce --augmentation=none --max_note_shift=0 --batch_size=8 --learning_rate=5e-4 --reduce_iteration=10000 --resume_iteration=0 --early_stop=100000 --cuda"
#coman = "python /project_2025_2/A2S/code/CRNN/real-a2s/train.py --experiment_id 1 --encoding kern --batch_size 16 --epochs 300 --patience 300"
#coman = "ls"
# Define el nombre del entorno
entorno="a2s-transformer"

# Ejecuta tu programa aquí (reemplaza esto con lo que desees ejecutar)
# Ejecutar el contenedor con acceso a la GPU
docker build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -t $entorno .
#docker run --name $SLURM_JOB_ID --gpus device=$SLURM_IDX --rm -v $R:/project_2025_2 kels
#docker run --name $SLURM_JOB_ID --gpus device=$SLURM_IDX --rm -v $R:/project_2025_2 $entorno $coman  > $SLURM_JOB_ID.log 2>&1
docker run --name $SLURM_JOB_ID --gpus device=$SLURM_IDX --rm -v $R:/a2s-transformer $entorno  > $SLURM_JOB_ID.log 2>&1

echo "Trabajo finalizado a las `date`"
