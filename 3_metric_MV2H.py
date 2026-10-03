from pyMV2H.utils.music import Music
from pyMV2H.metrics.mv2h import mv2h
from pyMV2H.converter.midi_converter import MidiConverter as Converter
import os
import pandas as pd
import pretty_midi as pm
pm.pretty_midi.MAX_TICK = 1e10


########## Parametros Dinamicas ##########
dataset = 'saxophone'
model = 'transformer'
##########################################
path_midi_est =    f"/home/wilson/Documentos/Experimentos_2026/07_Models_AMT_A2S/metrics/amt/saxophone/midi"
path_midi_target = f"/home/wilson/Documentos/Experimentos_2026/07_Models_AMT_A2S/metrics/amt/target/midi"
method = 'AMT'
#path_midi_target = "/home/grfia/wilson/project_2025_1/AMT/code_and_data/data_test/midi"
#path_midi_est = "/home/grfia/wilson/project_2025_1/AMT/code_and_data/data_test/est_midi"

# Lista para almacenar los archivos MIDI
archivos_midi_target = []
archivos_midi_est = []

# Recorre todos los archivos en la carpeta
for archivo in os.listdir(path_midi_target):
    if archivo.lower().endswith(('.mid', '.midi')):
        archivos_midi_target.append(archivo)

# Recorre todos los archivos en la carpeta
for archivo in os.listdir(path_midi_est):
    if archivo.lower().endswith(('.mid', '.midi')):
        archivos_midi_est.append(archivo)


# Archivos en ambos directorios (por nombre)
archivos_comunes = set(archivos_midi_target) & set(archivos_midi_est)

for archivo in archivos_comunes:
    path_archivos_midi_est = os.path.join(path_midi_est, archivo)
    path_archivos_txt_est = path_archivos_midi_est.replace(".mid", "_mv2h.txt")
    converter = Converter(file=path_archivos_midi_est, output=path_archivos_txt_est)
    converter.convert_file()

    path_archivos_midi_target = os.path.join(path_midi_target, archivo)
    path_archivos_txt_target = path_archivos_midi_target.replace(".mid", "_mv2h.txt")
    print(path_archivos_midi_target)
    print(path_archivos_txt_target)
    converter = Converter(file=path_archivos_midi_target, output=path_archivos_txt_target)
    converter.convert_file()
    print("Archivo exportado en TXT:", archivo)


print("Conversion de MIDI a TXT finalizado")
"""
Multi-pitch:    0.5896353166986564
Voice:          0.9687092568448501
Meter:          0.9995410738871042
Value:          0.8735131050247034
Harmony:        0.0
MV2H:           0.6862797504910628
"""
colum_dataset = 'Dataset'
colum_file = 'File'
colum_method = 'Method'
colum_model = 'Model'
colum_mpitch = 'Multi-pitch'
colum_voice = 'Voice'
colum_meter = 'Meter'
colum_value = 'Value'
colum_harmony = 'Harmony'
colum_mv2h = 'MV2H'


columnas = [colum_method, colum_dataset, colum_model, colum_file,
            colum_mpitch, colum_voice, colum_meter, colum_value,
            colum_harmony, colum_mv2h]

# Crea el DataFrame
df = pd.DataFrame(columns=columnas)

for i in range(len(archivos_midi_target)):
    #print(path_midi_est + "/" + archivos_txt_est[i])

    path_archivos_txt_est = path_midi_est + "/" + archivos_midi_target[i].replace(".mid","_mv2h.txt")
    path_archivos_txt_target = path_midi_target + "/" + archivos_midi_target[i].replace(".mid","_mv2h.txt")

    transcription_file = Music.from_file(path_archivos_txt_est)
    reference_file = Music.from_file(path_archivos_txt_target)

    try:
        scores = mv2h(reference_file, transcription_file)
        df.loc[len(df)] = [method, dataset, model, archivos_midi_target[i],
                        scores.multi_pitch, scores.voice, scores.meter, scores.harmony,
                        scores.note_value, scores.mv2h]
    except:
        df.loc[len(df)] = [method, dataset, model, archivos_midi_target[i],
                           0,0,0,0,0,0]


    print("Calculo de metricas completado:", archivos_midi_target[i])


# Exportar a archivo Excel
ruta_archivo = os.path.join(
    os.path.dirname(path_midi_est),
    f"MV2H_Eval_Score_{model}_{dataset}_A2S.xlsx"
)  # Nombre del archivo
#ruta_archivo = 'Results_Magenta.xlsx'  # Nombre del archivo
print(f"Exportando DataFrame a '{ruta_archivo}'...")
df.to_excel(ruta_archivo, index=False)  # index=False elimina la columna de índices
print(f"DataFrame exportado exitosamente como '{ruta_archivo}'.")
