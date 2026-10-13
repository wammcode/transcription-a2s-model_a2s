# Clonar el proyecto en otra ubicación

```bash
git clone https://github.com/wammcode/transcription-a2s-model_a2s.git
cd transcription-a2s-model_a2s

git clone control_version/a2s-transformer.bundle a2s-transformer
git -C a2s-transformer remote set-url origin https://github.com/multiscore/a2s-transformer.git
git -C a2s-transformer fetch origin
```

Los audios WAV/FLAC, los pesos `.ckpt`, los registros y las cachés no se incluyen en GitHub. Cópialos desde el equipo original o desde su almacenamiento externo si los necesitas.

## Actualizar ambos repositorios

`a2s-transformer` es un repositorio Git independiente e ignorado por el repositorio grande. Por eso, `git pull` en la raíz solo actualiza el archivo de respaldo `control_version/a2s-transformer.bundle`; no cambia la copia de trabajo de `a2s-transformer`.

Antes de actualizar, revisa los cambios locales en ambos repositorios y guárdalos en commits o con `git stash`:

```bash
git status --short
git -C a2s-transformer status --short
```

Para incorporar los cambios publicados en el repositorio grande, ejecuta desde su raíz:

```bash
git pull --ff-only origin main
git -C a2s-transformer fetch ../control_version/a2s-transformer.bundle main
git -C a2s-transformer merge --ff-only FETCH_HEAD
```

El primer comando descarga el bundle más reciente. Los dos siguientes importan su rama `main` en el repositorio anidado y avanzan `a2s-transformer` si el cambio es un avance directo. Se puede repetir este bloque cada vez que se publique una nueva versión del bundle.

El remoto `origin` de `a2s-transformer` apunta a `multiscore/a2s-transformer`. Si también quieres consultar y aplicar cambios publicados allí, usa:

```bash
git -C a2s-transformer pull --ff-only origin main
```

El bundle y `origin` son fuentes distintas. `--ff-only` evita crear una combinación automática si las ramas han divergido; si un comando se detiene por divergencia, conserva el estado y revisa las ramas antes de decidir cómo integrarlas. No uses `reset --hard` para resolverlo, porque podría descartar commits locales.

## Publicar cambios de ambos repositorios

`a2s-transformer` conserva su Git interno, pero su remoto `origin` corresponde al proyecto original de MultiScore. No ejecute `git -C a2s-transformer push origin main`: no es necesario para el repositorio global y requiere permisos sobre `multiscore/a2s-transformer`.

Para publicar los cambios de ambos repositorios en tu repositorio global de GitHub, actualiza la copia de seguridad del historial interno y publica el repositorio global:

```bash
bash scripts/actualizar_historial_a2s.sh
git add .
git commit -m "Actualizar trazabilidad de a2s-transformer"
git push origin main --follow-tags
```

Si hay cambios sin confirmar dentro de `a2s-transformer`, confírmalos allí antes de ejecutar esos comandos. El script incorporará todos sus commits, incluido su historial, en `control_version/a2s-transformer.bundle`, que se publicará en `wammcode/transcription-a2s-model_a2s`.
