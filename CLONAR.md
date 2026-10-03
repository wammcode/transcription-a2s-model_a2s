# Clonar el proyecto en otra ubicación

```bash
git clone https://github.com/wammcode/transcription-a2s-model_a2s.git
cd transcription-a2s-model_a2s

git clone control_version/a2s-transformer.bundle a2s-transformer
git -C a2s-transformer remote set-url origin https://github.com/multiscore/a2s-transformer.git
git -C a2s-transformer fetch origin
```

Los audios WAV/FLAC, los pesos `.ckpt`, los registros y las cachés no se incluyen en GitHub. Cópialos desde el equipo original o desde su almacenamiento externo si los necesitas.

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
