# Trazabilidad de `a2s-transformer`

## Procedencia

- Repositorio de origen: `https://github.com/multiscore/a2s-transformer.git`
- Rama local integrada: `main`
- Base remota: `origin/main` en `7d95545faf39572595df17891a4d0ce54bc23577` (`2025-02-19`, `speed it up thanks to @ffuhu :)`).
- Línea base funcional incorporada: `42e825f62afae65f31186e7d50de8ccd28f0a056`.
- Estado actual incorporado en el repositorio global: `11a88e32548be2253d6b309ccae680f0dfd85b85`.
- Referencias preservadas: todas las referencias locales y remotas disponibles al crear `control_version/a2s-transformer.bundle`.

## Ajustes locales preservados

Estos commits se encontraban por delante de `origin/main` y forman parte de la línea base del repositorio global:

| Fecha | Commit | Descripción original |
| --- | --- | --- |
| 2026-08-20 | `1c2bcda567be911865869c13b0a88c07fc05ecd1` | `polifonía variable` |
| 2026-08-26 | `41256b94891376f5bfa39a77598261a471c3ec9f` | `Soporte dual AMT y A2s` |
| 2026-08-26 | `a185f514816fbae2d9882d323eacf4af9078dab8` | `ajuste de limpieza de krn y prediccion funcional` |
| 2026-08-27 | `e8eee0ec665b34acc025fd2aa0a3afad21706b56` | `Ajuste train en AMT` |
| 2026-09-29 | `42e825f62afae65f31186e7d50de8ccd28f0a056` | `Ajustes prediccion AMT` |

## Cambios de documentación incorporados

| Fecha | Commit | Descripción |
| --- | --- | --- |
| 2026-10-03 | `11a88e32548be2253d6b309ccae680f0dfd85b85` | Traducción del README de `a2s-transformer` al español. |

## Mantenimiento

1. Realice y confirme los cambios del componente desde `a2s-transformer/`.
2. Desde la raíz global, ejecute `bash scripts/actualizar_historial_a2s.sh`.
3. Actualice este documento si cambia la procedencia, la rama integrada o se incorpora un ajuste relevante.
4. Confirme juntos el bundle y la documentación en el repositorio global.

El bundle no sustituye al repositorio Git anidado: proporciona una copia recuperable de su historial dentro del control de versiones global. El repositorio anidado sigue siendo la fuente de verdad para el historial detallado del componente.
