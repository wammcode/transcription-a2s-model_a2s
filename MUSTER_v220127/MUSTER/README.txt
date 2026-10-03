Compilación:

./compile.sh


Uso:

Prepare una partitura estimada (por ejemplo, `008_EST.xml`) y una partitura de referencia (*ground truth*, por ejemplo, `008_GT.xml`). A continuación, ejecute el siguiente comando:

./evaluate_XML_voicePlus.sh 008_GT 008_EST ER

Las métricas de evaluación se escribirán en `ER.txt`. De izquierda a derecha, las métricas de salida son:

(1)  tasa de error de altura (%)
(2)  tasa de notas omitidas (%)
(3)  tasa de notas añadidas (%)
(4)  tasa de error del instante de inicio (%)
(5)  tasa de error del instante de finalización (%)
(6)  media de (1) a (5)
(7)  tasa de error de voz (%)
(8)  media de (1) a (5) y (7)
(9)  precisión de voz (%)
(10) recuperación de voz (%)
(11) medida F de voz (%)
(12) error de escala del valor de nota
(13) tasa de error de mano (%)

Los detalles del análisis de errores se escriben en `008_EST_err_detail.txt`, donde se proporciona toda la información de alineamiento nota a nota y de los errores detectados. Los identificadores de nota se describen mediante símbolos de la forma `PXX-YY-ZZ`, que indica la nota ZZ del compás YY de la parte XX del archivo MusicXML. `GtID` se refiere al archivo MusicXML de referencia y `EstID` al archivo MusicXML estimado.


Observación:

Cuando el archivo MusicXML estimado contiene muchos errores, el proceso de alineamiento puede acumular una cantidad importante de errores, lo que afectará al análisis. Puede revisar el resultado del alineamiento de la siguiente forma. Después de ejecutar el script de evaluación:

./evaluate_XML_voicePlus.sh 008_GT 008_EST ER

encontrará los archivos `008_GT_fmt3x.txt` y `008_EST_auto_match.txt`. Visite:

https://midialignment.github.io/score-performance-match-editor/ScorePerformanceMatchEditor.html

y abra ambos archivos en el navegador. Así podrá ver el resultado del alineamiento y comprobar cómo se identificaron los errores de altura, las notas añadidas y las notas omitidas.


Historial de actualizaciones:

(2022/01/27) Se actualizaron algunos módulos internos.
(2022/01/18) Se añadió un archivo de salida con detalles del análisis de errores. Se modificaron algunos módulos internos.
(2021/12/17) Se corrigieron algunos errores.

Puede acceder a versiones anteriores en el siguiente enlace:

https://github.com/amtevaluation/amtevaluation.github.io


Referencias:

Consulte los siguientes artículos para conocer las definiciones de las métricas.

Eita Nakamura, Emmanouil Benetos, Kazuyoshi Yoshii, Simon Dixon,
Towards Complete Polyphonic Music Transcription: Integrating Multi-Pitch Detection and Rhythm Quantization.
Proc. 43rd IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), pp. 101-105, 2018.

Yuki Hiramatsu, Eita Nakamura, Kazuyoshi Yoshii,
Joint Estimation of Note Values and Voices for Audio-to-Score Piano Transcription
Proc. 22nd International Society for Music Information Retrieval Conference (ISMIR), 2021.

Contacto:

Para cualquier consulta, contacte con:
Eita Nakamura (eita.nakamura@gmail.com)
