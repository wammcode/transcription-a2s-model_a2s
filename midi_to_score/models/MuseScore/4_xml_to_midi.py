import importlib.util
import os
import subprocess
import sys

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    def tqdm(iterable, **kwargs):  # type: ignore[override]
        return iterable



carpeta_origen =  "/home/wilson/Documentos/Experimentos_2026/07_Models_AMT_A2S/midi_to_score/predict/saxophone/musicxml"
carpeta_destino = "/home/wilson/Documentos/Experimentos_2026/07_Models_AMT_A2S/midi_to_score/predict/saxophone/midi"


def main() -> None:
    if not os.path.isdir(carpeta_origen):
        raise FileNotFoundError(f"No existe la carpeta de entrada: {carpeta_origen}")

    if importlib.util.find_spec("converter21") is None:
        raise ModuleNotFoundError(
            "No se encontró el módulo 'converter21' en este entorno.\n"
            f"Python activo: {sys.executable}\n"
            "Instálalo con: python -m pip install converter21"
        )

    os.makedirs(carpeta_destino, exist_ok=True)
    archivos_xml = sorted(
        f for f in os.listdir(carpeta_origen) if f.lower().endswith((".xml", ".musicxml"))
    )

    if not archivos_xml:
        print("No se encontraron archivos .xml/.musicxml para convertir.")
        return

    errores = []
    for archivo in tqdm(archivos_xml, desc="Convirtiendo XML a MIDI"):
        ruta_xml = os.path.join(carpeta_origen, archivo)
        nombre_salida = os.path.splitext(archivo)[0]
        ruta_midi = os.path.join(carpeta_destino, f"{nombre_salida}.mid")

        # Usar el mismo intérprete activo evita mezclar entornos de Python.
        resultado = subprocess.run(
            [sys.executable, "-m", "converter21", "-f", "musicxml", "-t", "midi", "-c", ruta_xml, ruta_midi],
            capture_output=True,
            text=True,
        )
        if resultado.returncode != 0:
            stderr = (resultado.stderr or "").strip()
            errores.append(f"{archivo}: {stderr or 'error sin detalle en stderr'}")

    convertidos = len(archivos_xml) - len(errores)
    print(f"Conversión finalizada. OK: {convertidos} | Error: {len(errores)}")
    if errores:
        print("Primeros errores:")
        for detalle in errores[:5]:
            print(f"- {detalle}")


if __name__ == "__main__":
    main()
