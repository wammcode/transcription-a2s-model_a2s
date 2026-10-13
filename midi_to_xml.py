import os
import shutil
from music21 import converter as converterm21

def midi2xml(in_file, out_folder):
    """Convierte un archivo .krn a .midi y lo guarda en la carpeta de salida."""
    midi_path = os.path.join(out_folder, os.path.splitext(os.path.basename(in_file))[0] + ".xml")
    #print(in_file)
    converterm21.parse(in_file).write("xml", midi_path)
    #return midi_file

def batch_convert_krn_to_midi(input_folder, output_folder):
    """Convierte todos los archivos .krn en input_folder y los guarda en output_folder."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(input_folder):
        if file.endswith(".mid"):
            in_file = os.path.join(input_folder, file)
            try:
                midi2xml(in_file, output_folder)
                print(f"Convertido: {file} → musicxml guardado en {output_folder}")
            except Exception as e:
                print(f"Error al convertir {file}: {e}")

# Rutas de las carpetas (cámbialas según tu caso)
input_folder =  f"metrics/holistic/target/quartets/midi"
output_folder = f"metrics/holistic/target/quartets/musicxml"

# Ejecutar conversión en batch
batch_convert_krn_to_midi(input_folder, output_folder)