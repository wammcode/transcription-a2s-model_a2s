# Experimentos globales de AMT y A2S

Este repositorio reúne los experimentos de transcripción automática de música (AMT) y de audio a partitura (A2S), los conjuntos de métricas, las conversiones MIDI/partitura y la herramienta MUSTER utilizada para la evaluación.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `a2s-transformer/` | Implementación original de A2S/AMT y su historial Git independiente. |
| `data/` | Manifiestos, partituras y datos locales del corpus de saxofón. Los audios no se versionan. |
| `metrics/` | Resultados y recursos de evaluación de las métricas. |
| `midi_to_score/` | Conversión y predicciones de MIDI a partitura. |
| `MUSTER_v220127/` | Código fuente de la herramienta MUSTER. |
| `control_version/` | Copia recuperable del historial de `a2s-transformer`. |

## Control de versiones y trazabilidad

El repositorio global usa Git desde la versión `0.1.0`. El directorio `a2s-transformer/` conserva su repositorio Git propio para no perder su historial ni sus referencias originales. Como copia de seguridad y vínculo auditable con el repositorio global, `control_version/a2s-transformer.bundle` contiene una instantánea completa de todas sus referencias Git.

La línea base funcional incorporada es el commit `42e825f62afae65f31186e7d50de8ccd28f0a056` de `a2s-transformer`, que parte de `origin/main` en `7d95545faf39572595df17891a4d0ce54bc23577`. La instantánea actual añade la traducción de su README en `11a88e32548be2253d6b309ccae680f0dfd85b85`. Los ajustes locales anteriores y posteriores están documentados en [TRAZABILIDAD_A2S_TRANSFORMER.md](TRAZABILIDAD_A2S_TRANSFORMER.md), mientras que los cambios del repositorio global se registran en [CHANGELOG.md](CHANGELOG.md).

Los audios fuente, pesos de modelos, cachés, registros de ejecución y binarios compilados se excluyen mediante `.gitignore`. Así, el historial mantiene código, documentación, manifiestos, partituras y resultados ligeros sin añadir artefactos reproducibles de gran tamaño.

### Restaurar el historial de A2S/AMT

En una copia nueva del repositorio global, recupere el repositorio anidado con:

```bash
git clone control_version/a2s-transformer.bundle a2s-transformer
git -C a2s-transformer remote set-url origin https://github.com/multiscore/a2s-transformer.git
git -C a2s-transformer fetch origin
```

### Actualizar la instantánea

Después de confirmar cambios dentro de `a2s-transformer/`, ejecute el siguiente comando desde la raíz del repositorio global y confirme el archivo bundle junto con el cambio global correspondiente:

```bash
bash scripts/actualizar_historial_a2s.sh
git add control_version/a2s-transformer.bundle TRAZABILIDAD_A2S_TRANSFORMER.md CHANGELOG.md
git commit -m "Actualizar trazabilidad de a2s-transformer"
```

## Documentación de los componentes

- [A2S Transformer](a2s-transformer/README.md)
- [MUSTER](MUSTER_v220127/MUSTER/README.txt)
