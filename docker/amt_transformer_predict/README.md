# Predicción AMT Transformer con QUARTETS

Desde la raíz del proyecto, envíe `sbatch docker/amt_transformer_predict/p1.slurm`.
El trabajo usa una GPU de la partición `bacterio` y el checkpoint entrenado
`a2s-transformer/weights/transformer-AMT/quartets.ckpt` para transcribir los
7.611 WAV de `data/data_quartets/Quartets/amt_partitions/quartets/test.txt`.

Los MIDI se guardan con extensión `.mid` en
`a2s-transformer/predict/quartets/midi`, con el mismo nombre base que cada WAV.
El manifiesto usa referencias `.midi` únicamente para localizar sus pares; la
predicción se hace a partir del audio. El trabajo omite salidas completas si
se reenvía tras una interrupción. Cada MIDI se escribe primero en un archivo
temporal y se publica al terminar.

Los registros se escriben aquí como `amt-quartets-predict-<jobid>.out` y
`.err`. Consulte el estado con `squeue -j <jobid>`. El archivo
`a2s-transformer/logs/amt-quartets-predict-<jobid>.complete` se crea solo si
termina el proceso de predicción.
