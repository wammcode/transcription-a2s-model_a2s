#!/usr/bin/env python3

import subprocess
from pathlib import Path

# ==========================================
# CONFIGURACIÓN
# ==========================================

# Carpeta donde están los archivos .mid
INPUT_DIR =  Path("/home/wilson/Documentos/Experimentos_2026/07_Models_AMT_A2S/midi_to_score/data/saxophone/midi")

# Carpeta donde se guardarán los .musicxml
OUTPUT_DIR = Path("/home/wilson/Documentos/Experimentos_2026/07_Models_AMT_A2S/midi_to_score/predict/saxophone/musicxml")

# Comando de MuseScore
MSCORE_COMMAND = "mscore"


def convertir_midi_a_musicxml():
    # Crear carpeta de salida si no existe
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Buscar todos los archivos .mid
    archivos_midi = sorted(INPUT_DIR.glob("*.mid"))

    print(f"Archivos MIDI encontrados: {len(archivos_midi)}")
    print()

    for i, midi_path in enumerate(archivos_midi, start=1):

        # Mantener el mismo nombre, cambiando extensión
        output_path = OUTPUT_DIR / f"{midi_path.stem}.musicxml"

        print(
            f"[{i}/{len(archivos_midi)}] "
            f"Convirtiendo: {midi_path.name}"
        )

        comando = [
            MSCORE_COMMAND,
            "-o",
            str(output_path),
            str(midi_path),
        ]

        try:
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if resultado.returncode == 0:
                print(f"   OK -> {output_path.name}")

            else:
                print("   ERROR durante la conversión")
                print(f"   Código: {resultado.returncode}")

                if resultado.stderr:
                    print(f"   STDERR: {resultado.stderr.strip()}")

        except Exception as e:
            print(f"   ERROR: {e}")

    print()
    print("Proceso terminado.")


if __name__ == "__main__":
    convertir_midi_a_musicxml()