# AMT Transformer con QUARTETS

Envíe el entrenamiento desde la raíz del repositorio con `sbatch docker/amt_transformer_train/p1.slurm`. El trabajo utiliza una GPU, 6 CPU y 40 GB de RAM en bacterio, las particiones `data/data_quartets/Quartets/amt_partitions/quartets`, audio WAV y referencias MIDI con extensión `.midi`.

Los registros quedan en este directorio como `amt-quartets-<jobid>.out` y `.err`. Consulte el estado con `squeue -j <jobid>`. El mejor punto de control se escribe en `a2s-transformer/weights/transformer-AMT/quartets.ckpt`; el trabajo crea `a2s-transformer/logs/amt-quartets-<jobid>.complete` solamente después de terminar el entrenamiento y la evaluación de prueba.

El entrenamiento usa secuencias MIDILike de hasta 1024 posiciones, lotes de 8, validación cada 5 épocas, parada temprana con paciencia de 5 validaciones y seguimiento de `val_loss`. Los experimentos de Weights & Biases quedan en modo sin conexión. La comprobación previa encontró 293 MIDI (0,77 % del corpus) cuya secuencia supera el límite y se trunca por el prefijo.
