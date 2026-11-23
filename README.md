# STATGOAT

Índice compuesto de valor histórico de jugadores de BAA, NBA y ABA. 2.908 jugadores, 1947–2026.

**Web:** https://xicoe2001-svg.github.io/statgoat/

La página es un único HTML estático. Todo el cálculo (pesos ajustables, buscador, fichas) pasa en el navegador: no hay servidor ni base de datos.

---

## Actualización automática

El workflow `.github/workflows/rebuild.yml` se ejecuta:

- **cada lunes hacia las 04:30 UTC**
- cuando tocas un `.py`, `head.html`, `app.js` o uno de los CSV
- a mano, desde la pestaña **Actions → Rebuild STATGOAT → Run workflow**

El ciclo es: descargar fuentes → recalcular → verificar → si algo cambió, commit del `index.html`. GitHub Pages lo republica solo.

Si una fuente falla o alguna verificación no pasa, **el workflow aborta y la web se queda como estaba.** Nunca se publica un índice roto ni con datos viejos: hay comprobaciones que fallan si los playoffs, el campeón, el Finals MVP, el MVP o los All-NBA no llegan a la última temporada terminada.

### De dónde sale cada dato

- **Temporada regular:** volcado público de Basketball-Reference (`sumitrodatta/bball-reference-datasets`).
- **Playoffs, campeones, Finals MVP y premios recientes:** directamente de las páginas de Basketball-Reference, con `fetch_bref_extra.py`. Va despacio a propósito (una petición cada 4 segundos, muy por debajo de su límite) y guarda todo en `cache/`, así que cada lunes solo vuelve a pedir la temporada en curso y la anterior.

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

Si un lunes sale en rojo, abre el paso que falla en **Actions**: el mensaje dice qué dato falta o qué comprobación no cuadra.

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

**Puntuación:** suma de los siete bloques por sus pesos, de 0 a 100. El bonus por totales de carrera (hasta 3 puntos) es opcional y está desactivado por defecto: compara totales en bruto entre épocas y la longevidad ya cuenta un 20 % en cada bloque.

**Mejores temporadas:** la misma fórmula aplicada a un solo año (liga regular, playoffs de ese año, anillo según su aportación y premios de esa temporada), desde 1951-52. La web exporta las mejores 1.200 con los pesos por defecto más las 150 mejores de cada bloque, y las reordena con los pesos que ponga el usuario.

**Eficiencia:** puntos añadidos por eficiencia, `(TS% propio − TS% de su liga) × intentos` (70 %), y control de pérdidas (30 %). Mide eficiencia y volumen a la vez; se usa igual en liga regular y en playoffs.

El glosario completo está en la propia página.

**Playoffs:** cada postemporada se mide en z-score contra los jugadores de esa misma postemporada (producción, eficiencia e impacto). El bloque combina el nivel en sus mejores 4.000 minutos de playoffs (55 %), el plus de playoffs —si crece o se encoge frente a su liga regular de ese mismo año— (25 %) y el volumen de Win Shares (20 %). Con pocos minutos de playoffs, el nivel se acerca a lo que predice su temporada regular y el plus, a 0.

**Límite:** antes de 1974 no hay BPM, y antes de 1952 no hay minutos. A cada jugador se le mide con lo que su época registró.

## Fuentes

- Basketball-Reference: temporada regular vía el volcado público de `sumitrodatta/bball-reference-datasets`; playoffs, campeones y premios recientes, de sus páginas.

Si reutilizas esto, cítala.

## Aviso

STATGOAT no está afiliado ni respaldado por la NBA, la NBPA ni Basketball-Reference. Es un análisis histórico bajo una ponderación concreta: no es predicción, ni recomendación de apuestas, ni una verdad establecida.


