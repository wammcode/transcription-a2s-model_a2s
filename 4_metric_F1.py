#!pip install mir_eval==0.7
#!pip install pretty_midi==0.2.10

import os
from mir_eval.transcription import precision_recall_f1_overlap
import pandas as pd
import pretty_midi as pm
import time
import numpy as np
pm.pretty_midi.MAX_TICK = 1e10


########## Parametros Dinamicas ##########
dataset = 'saxophone'
model = 'transformer'
##########################################
est_midi_path = f"metrics/amt/saxophone/midi"
midi_path =     f"metrics/amt/target/midi"
method = 'AMT'



def listar_archivos_midi(directorio):
    """ Lista todos los archivos con extensión .midi y .mid en un directorio """
    archivos = []
    for archivo in os.listdir(directorio):
        if archivo.endswith('.midi') or archivo.endswith('.mid'):
            archivos.append(archivo)
    return archivos

def verificar_archivos(est_midi_path, midi_path):
    # Obtener los archivos de ambas carpetas
    archivos_est_midi = listar_archivos_midi(est_midi_path)
    archivos_midi = listar_archivos_midi(midi_path)

    # Comprobar si todos los archivos de 'midi' están en 'est_midi'
    archivos_faltantes = [archivo for archivo in archivos_midi if archivo not in archivos_est_midi]

    if archivos_faltantes:
        print("Archivos faltantes en 'est_midi':")
        for archivo in archivos_faltantes:
            print(f"- {archivo}")
    else:
        print("Todos los archivos de 'midi' están presentes en 'est_midi'.")


def midi_to_txt(file_in):
    # Cargar archivo MIDI fuente
    in_midi = pm.PrettyMIDI(file_in)
    # Obtener la ruta base sin extensión
    base_name, _ = os.path.splitext(file_in)
    # Abrir los archivos de salida para escribir los datos
    with open(base_name + '_int.txt', 'w') as fint, \
         open(base_name + '_pitch.txt', 'w') as fpitch:

        # Iterar a través de los diferentes eventos
        for instrument in in_midi.instruments:
            for note in instrument.notes:
                # Escribir las notas de inicio y fin
                fint.write("{},{}\n".format(note.start, note.end))
                # Escribir la frecuencia correspondiente a la nota
                fpitch.write("{}\n".format(pm.note_number_to_hz(note.pitch)))

def process_midi_to_txt(folder_paths, midi_to_txt_function):
    """
    Aplicar la función `midi_to_txt` a todos los archivos `.mid` en las carpetas proporcionadas.

    :param folder_paths: Lista de rutas de carpetas donde buscar archivos `.mid`.
    :param midi_to_txt_function: Función a aplicar a cada archivo MIDI.
    """
    for folder in folder_paths:
        # Obtener todos los archivos .mid en la carpeta
        midi_files = [f for f in os.listdir(folder) if f.endswith(('.mid', '.midi'))]

        for midi_file in midi_files:
            input_path = os.path.join(folder, midi_file)
            # Aplicar la función a cada archivo MIDI
            #midi_to_txt_function(input_path)
            print(f"Archivo Procesando: {input_path}")
            midi_to_txt_function(input_path)

def load_midi_data(intervals_file, pitch_file):
    # Cargar los intervalos desde el archivo
    with open(intervals_file) as fint:
        intervals = np.array([[float(u.split(",")[0]), float(u.split(",")[1])] for u in fint.readlines()])

    # Cargar las frecuencias de las notas desde el archivo
    with open(pitch_file) as fpitch:
        pitches = np.array([float(u) for u in fpitch.readlines()])

    return intervals, pitches

# Ejecutar la verificación
verificar_archivos(est_midi_path, midi_path)
#input("Presione enter para continuar...")

# Rutas a las carpetas con archivos MIDI
folders = [est_midi_path, midi_path]

# Aplicar la función `midi_to_txt` a todos los archivos en las carpetas
process_midi_to_txt(folders, midi_to_txt)
print("Proceso de conversión MIDI TO TXT finalizado.")
time.sleep(4)

# Proceso para calcular las métricas entre los archivos MIDI
folder_1 = est_midi_path
folder_2 = midi_path

colum_dataset = 'Dataset'
colum_file = 'File'
colum_method = 'Method'
colum_model = 'Model'
colum_precision = 'Precision'
colum_recall = 'Recall'
colum_f1 = 'F-measure'
colum_or = 'Average Overlap Ratio'

columnas = [colum_method, colum_dataset, colum_model, colum_file, colum_precision, colum_recall, colum_f1, colum_or]

# Crea el DataFrame
df = pd.DataFrame(columns=columnas)

# /target/midi/MAPS_MUS-liz_et5_AkPnCGdD.mid
search_files = [f for f in os.listdir(folder_2) if f.endswith('int.txt')]

search_files = [
    f for f in os.listdir(folder_2)
    if f.endswith("_int.txt")
]

for txt_file in search_files:

    print("\nArchivo Procesando:", txt_file)

    file_int_est = os.path.join(folder_1, txt_file)
    file_pitch_est = os.path.join(
        folder_1,
        txt_file.replace("_int.txt", "_pitch.txt")
    )

    file_int_ref = os.path.join(folder_2, txt_file)
    file_pitch_ref = os.path.join(
        folder_2,
        txt_file.replace("_int.txt", "_pitch.txt")
    )

    file_save = txt_file.replace("_int.txt", ".mid")

    # --------------------------------------------------
    # Verificar que existen los archivos estimados
    # --------------------------------------------------
    if not os.path.exists(file_int_est):
        print(f"ADVERTENCIA: No existe intervalo estimado:")
        print(f"  {file_int_est}")

        P, R, F1, OR = np.nan, np.nan, np.nan, np.nan

        df.loc[len(df)] = [
            method,
            dataset,
            model,
            file_save,
            P,
            R,
            F1,
            OR
        ]

        continue

    if not os.path.exists(file_pitch_est):
        print(f"ADVERTENCIA: No existe pitch estimado:")
        print(f"  {file_pitch_est}")

        P, R, F1, OR = np.nan, np.nan, np.nan, np.nan

        df.loc[len(df)] = [
            method,
            dataset,
            model,
            file_save,
            P,
            R,
            F1,
            OR
        ]

        continue

    # --------------------------------------------------
    # Verificar referencia
    # --------------------------------------------------
    if not os.path.exists(file_int_ref):
        print(f"ADVERTENCIA: No existe intervalo de referencia:")
        print(f"  {file_int_ref}")
        continue

    if not os.path.exists(file_pitch_ref):
        print(f"ADVERTENCIA: No existe pitch de referencia:")
        print(f"  {file_pitch_ref}")
        continue

    # --------------------------------------------------
    # Cargar datos
    # --------------------------------------------------
    intervals, pitches = load_midi_data(
        file_int_est,
        file_pitch_est
    )

    intervals_target, pitches_target = load_midi_data(
        file_int_ref,
        file_pitch_ref
    )

    # --------------------------------------------------
    # Calcular métricas
    # --------------------------------------------------
    if intervals.size > 0:

        P, R, F1, OR = precision_recall_f1_overlap(
            ref_intervals=intervals_target,
            ref_pitches=pitches_target,
            est_intervals=intervals,
            est_pitches=pitches
        )

    else:

        print("ADVERTENCIA: MIDI estimado sin notas.")

        P, R, F1, OR = np.nan, np.nan, np.nan, np.nan

    # --------------------------------------------------
    # Guardar resultado
    # --------------------------------------------------
    df.loc[len(df)] = [
        method,
        dataset,
        model,
        file_save,
        P,
        R,
        F1,
        OR
    ]
# Exportar a archivo Excel
output_dir = os.path.dirname(os.path.normpath(est_midi_path))
ruta_archivo = os.path.join(output_dir, f"F1_Score_Eval_Midi_{model}_{dataset}.xlsx")
#ruta_archivo = 'Results_Magenta.xlsx'  # Nombre del archivo
print(f"Exportando DataFrame a '{ruta_archivo}'...")
df.to_excel(ruta_archivo, index=False)  # index=False elimina la columna de índices
print(f"DataFrame exportado exitosamente como '{ruta_archivo}'.")
