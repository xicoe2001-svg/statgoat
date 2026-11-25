# STATGOAT

Índice compuesto de valor histórico de jugadores de BAA, NBA y ABA. 2.908 jugadores, 1947–2026.

**Web:** https://xicoe2001-svg.github.io/statgoat/

La página es un único HTML estático. Todo el cálculo (pesos ajustables, buscador, fichas) pasa en el navegador: no hay servidor ni base de datos.

---

## Actualización automática

El workflow `.github/workflows/rebuild.yml` se ejecuta:

- **cada día hacia las 09:20 UTC**
- cuando tocas un `.py`, `head.html`, `app.js` o uno de los CSV
- a mano, desde la pestaña **Actions → Rebuild STATGOAT → Run workflow**

El ciclo es: descargar fuentes → recalcular → verificar → si algo cambió, commit del `index.html`. GitHub Pages lo republica solo.

Si una fuente falla o alguna verificación no pasa, **el workflow aborta y la web se queda como estaba.** Nunca se publica un índice roto ni con datos viejos: hay comprobaciones que fallan si los playoffs, el campeón, el Finals MVP, el MVP o los All-NBA no llegan a la última temporada terminada.

### De dónde sale cada dato

- **Temporada regular:** volcado público de Basketball-Reference (`sumitrodatta/bball-reference-datasets`). La temporada en curso se lee cada día directamente de Basketball-Reference, porque el volcado va con semanas de retraso.
- **Playoffs, campeones, Finals MVP y premios recientes:** directamente de las páginas de Basketball-Reference, con `fetch_bref_extra.py`. Va despacio a propósito (una petición cada 4 segundos, muy por debajo de su límite) y guarda todo en `cache/`, así que cada día solo vuelve a pedir la temporada en curso y la anterior.

La primera ejecución descarga la historia entera de playoffs (unos 12 minutos). Las siguientes, menos de un minuto.

## Qué es cada fichero

| Fichero | Para qué |
|---|---|
| `fetch_sources.py` | Descarga las fuentes y verifica que llegan enteras |
| `statgoat_pipeline.py` | z-scores por temporada y agregación de carrera |
| `statgoat_compose.py` | Playoffs, premios, anillos, bonus y puntuación final |
| `export_web.py` | Exporta los 2.908 jugadores a JSON columnar |
| `build_site.py` | Ensambla `index.html` |
| `fetch_bref_extra.py` | Playoffs, campeones, Finals MVP y premios recientes |
| `verify_build.py` | Comprobaciones de integridad y frescura antes de publicar |
| `head.html` | Estructura y estilos de la web |
| `app.js` | Lógica del visor |
| `champions.csv` | Campeones por temporada · se amplía solo |
| `finals_mvp.csv` | Finals MVP por temporada · se amplía solo |
| `cache/` | Lo descargado de Basketball-Reference · se actualiza solo |
| `index.html` | La web · se regenera sola |
| `data.json` | Los datos en crudo, por si alguien los quiere reutilizar |

Las carpetas `_raw/` y `_build/` son temporales y están en el `.gitignore`.

## Mantenimiento

Ninguno. Campeón, Finals MVP, playoffs y premios se recogen solos cuando Basketball-Reference los publica.

Si un día sale en rojo, abre el paso que falla en **Actions**: el mensaje dice qué dato falta o qué comprobación no cuadra.

## Ejecutar en local

```bash
pip install -r requirements.txt
python fetch_sources.py
python fetch_bref_extra.py
python statgoat_pipeline.py
python statgoat_compose.py
python export_web.py
python build_site.py
python verify_build.py
```

La primera vez, unos 15 minutos (la descarga de playoffs). Después, unos 3.

## Metodología

Ninguna estadística se compara en bruto entre épocas. Todo se convierte a z-score dentro de su propia temporada y liga, contra los jugadores cualificados de ese año. Se mide dominancia relativa, no producción absoluta.

Siete bloques ponderables: Producción 15%, Eficiencia 7%, Impacto 20%, Defensa 13%, Playoffs 20%, Títulos 15%, Premios 10%. Los pesos se cambian en vivo desde la web.

**Carrera:** cada bloque se resume como 40 % media de las 3 mejores temporadas + 40 % de las 7 mejores + 20 % acumulado. Antes de sumarlo, el acumulado se pasa a la misma escala que el pico a partir de su percentil histórico, para que cada porcentaje pese lo que dice (en bruto, el «20 %» llegaba a pesar la mitad en las carreras largas). Si un jugador tiene menos de 3 o de 7 temporadas computables, las que faltan cuentan como 0 (jugador medio de la liga).

**Escala:** títulos y premios se llevan por percentil a la escala de los bloques estadísticos, para que los pesos signifiquen lo que dicen (antes el palmarés pesaba un 34 % en el top 10 en vez de su 25 %). La escala es continua: el 0 queda en el percentil medio de su grupo y los demás se reparten desde ahí hasta arriba, así que un anillo testimonial o un solo All-Star valen casi lo mismo que nada. El anillo no cuenta para quien fue traspasado antes de los playoffs.

**Puntuación:** suma de los siete bloques por sus pesos, de 0 a 100. Ficha desplegable: `export_web.py` escribe un archivo por jugador en `det/` (temporadas bloque a bloque, playoffs, anillos con su valor y premios año a año) que la web descarga al abrir la ficha, para que la página siga pesando lo mismo.

Margen de puesto: 2.000 sorteos de pesos alrededor de los de base (Dirichlet de concentración 50) dan el rango de puestos (percentiles 10-90) de cada jugador, que se muestra en su ficha.

El bonus por totales de carrera es opcional y está desactivado por defecto. Da puntos por el puesto histórico en puntos, rebotes, asistencias, robos, tapones o triples (1.º = 3 · 2.º = 2,4 · 3.º = 1,8 · 4.º = 1,2 · 5.º = 0,6; cuenta solo la mejor categoría). No va en la nota por defecto porque compara totales en bruto entre épocas y la longevidad ya cuenta un 20 % en cada bloque.

**Por temporada:** todas las temporadas medibles de un año (1.000+ minutos), con los mismos siete bloques y la escala de Mejores temporadas, en `yr/<año>.json` (se descargan al elegir el año).

**Temporada en curso:** se recalcula cada día. Umbrales de minutos proporcionales a lo jugado (1.000 para contar y 500 para el grupo del z, por la fracción de 82 partidos), bloques medidos contra las temporadas cerradas. Mientras no hay playoffs solo puntúan la liga regular y Premios, previsto por el Jugador de la semana; Playoffs y Títulos entran cuando se juegan (hasta entonces su peso se reparte) y el primero de la temporada marca 100 (`cache/pow.csv`; ritmo proyectado con contracción de 8 semanas y convertido al bloque de Premios medio de 2001-02 a 2025-26 para ese número de premios). Entra en las carreras y en Mejores temporadas cuando acaba la liga regular (82 partidos o empiezan los playoffs).

**Navegación:** en el móvil los pesos van en un panel que se abre con el botón «Pesos»; las pestañas se quedan fijas al bajar; las fichas empiezan por «De dónde sale la nota», tienen botón de compartir y de cerrar, y enlazan jugador ↔ temporada ↔ año. La ficha de jugador dibuja la nota de cada temporada (`ss` en `det/`), y en la temporada en curso cada jugador lleva su cambio de puesto desde el día anterior (`cache/live_ranks.json`). La vista previa al compartir usa `og.png`, `favicon.svg` y `apple-touch-icon.png`.

**Desde 1979-80:** segunda vista del mismo índice que cuenta solo lo jugado desde 1979-80 (primera temporada con línea de 3 y con todas las estadísticas registradas). Los z-scores no cambian; la carrera, los playoffs, los anillos (cada uno con su crédito), los premios, los totales, la escala y el margen se recalculan con lo jugado desde ese año (`statgoat_compose.py`, `ERA0`). La web la muestra con el selector «Toda la historia / Desde 1979-80»; en Mejores temporadas solo filtra por año.

**Mejores temporadas:** la misma fórmula aplicada a un solo año (liga regular, playoffs de ese año, anillo según su aportación y premios de esa temporada), desde 1951-52. Títulos y premios se llevan a la escala de los bloques estadísticos por percentil, para que pesen lo que dicen sus porcentajes. La web exporta las mejores 1.200 con los pesos por defecto más las 150 mejores de cada bloque, y las reordena con los pesos que ponga el usuario.

**Eficiencia:** puntos añadidos por eficiencia, `(TS% propio − TS% de su liga) × intentos` (70 %), y control de pérdidas (30 %). Mide eficiencia y volumen a la vez; se usa igual en liga regular y en playoffs.

El glosario completo está en la propia página.

**Playoffs:** cada postemporada se mide en z-score contra los jugadores de esa misma postemporada (producción, eficiencia e impacto). El bloque combina el nivel en sus mejores 4.000 minutos de playoffs (80 %) y el volumen de Win Shares (20 %). Con pocos minutos de playoffs, el nivel se acerca a lo que predice su temporada regular. El plus de playoffs —si crece o se encoge frente a su liga regular de ese mismo año— se muestra en la ficha pero no puntúa: el nivel ya lo recoge, y sumarlo aparte castigaba a quien hacía una gran liga regular.

**Límite:** antes de 1974 no hay BPM, y antes de 1952 no hay minutos. A cada jugador se le mide con lo que su época registró.

## Fuentes

- Basketball-Reference: temporada regular vía el volcado público de `sumitrodatta/bball-reference-datasets` (la temporada en curso, de sus páginas cada día); playoffs, campeones y premios recientes, de sus páginas.

Si reutilizas esto, cítala.

## Aviso

STATGOAT no está afiliado ni respaldado por la NBA, la NBPA ni Basketball-Reference. Es un análisis histórico bajo una ponderación concreta: no es predicción, ni recomendación de apuestas, ni una verdad establecida.


