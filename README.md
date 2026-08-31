# STATGOAT

Índice compuesto de valor histórico de jugadores de BAA, NBA y ABA. 2.908 jugadores, 1947–2026.

**Web:** https://xicoe2001-svg.github.io/statgoat/

La página es un único HTML estático. Todo el cálculo (pesos ajustables, buscador, fichas) pasa en el navegador: no hay servidor ni base de datos.

---

## Actualización automática

El workflow `.github/workflows/rebuild.yml` se ejecuta:

- **cada lunes a las 04:00 UTC**
- cuando tocas un `.py`, `head.html`, `app.js` o uno de los CSV
- a mano, desde la pestaña **Actions → Rebuild STATGOAT → Run workflow**

El ciclo es: descargar fuentes → recalcular → verificar → si algo cambió, commit del `index.html`. GitHub Pages lo republica solo.

Si una fuente falla o alguna de las 12 verificaciones no pasa, **el workflow aborta y la web se queda como estaba.** Nunca se publica un índice roto.

### Cadencia real

El volcado de Basketball-Reference se refresca cada cierto tiempo, no en directo. El ciclo efectivo es: cuando la fuente publica datos nuevos, esta web los recoge el lunes siguiente. Un índice de carrera no se mueve en tiempo real: un partido suelto cambia la media de quince años en milésimas.

## Qué es cada fichero

| Fichero | Para qué |
|---|---|
| `fetch_sources.py` | Descarga las fuentes y verifica que llegan enteras |
| `statgoat_pipeline.py` | z-scores por temporada y agregación de carrera |
| `statgoat_compose.py` | Playoffs, premios, anillos, bonus y puntuación final |
| `export_web.py` | Exporta los 2.908 jugadores a JSON columnar |
| `build_site.py` | Ensambla `index.html` |
| `verify_build.py` | 12 comprobaciones antes de publicar |
| `head.html` | Estructura y estilos de la web |
| `app.js` | Lógica del visor |
| `champions.csv` | Campeones por temporada · **mantenimiento manual** |
| `playoff_ppg_career.csv` | Anotación de playoffs de carrera · **mantenimiento manual** |
| `index.html` | La web · se regenera sola |
| `data.json` | Los datos en crudo, por si alguien los quiere reutilizar |

Las carpetas `_raw/` y `_build/` son temporales y están en el `.gitignore`.

## Mantenimiento: una vez al año

Al acabar cada temporada hay tres cosas que ninguna fuente abierta sirve en bruto:

**1. `champions.csv`** — añade una fila con el campeón:
```csv
2027,NBA,XXX
```
`XXX` es la abreviatura del equipo tal como aparece en `_raw/bref/Team Abbrev.csv`.

**2. `statgoat_compose.py`** — añade el Finals MVP al diccionario `FMVP`:
```python
2027: 'Nombre del jugador',
```

**3. `playoff_ppg_career.csv`** — refresca la anotación de playoffs desde el leaderboard de Basketball-Reference. Cubre el top 250; el resto se estima con la anotación de liga regular.

El parche manual del MVP 2026 se desactiva solo en cuanto la fuente incluya esa votación. No hay que tocarlo.

## Ejecutar en local

```bash
pip install -r requirements.txt
python fetch_sources.py
python statgoat_pipeline.py
python statgoat_compose.py
python export_web.py
python build_site.py
python verify_build.py
```

Unos 3 minutos, casi todo en la descarga.

## Metodología

Ninguna estadística se compara en bruto entre épocas. Todo se convierte a z-score dentro de su propia temporada y liga, contra los jugadores cualificados de ese año. Se mide dominancia relativa, no producción absoluta.

Siete bloques ponderables: Producción 15%, Eficiencia 7%, Impacto 20%, Defensa 13%, Playoffs 20%, Títulos 15%, Premios 10%. Los pesos se cambian en vivo desde la web.

El glosario completo está en la propia página.

**Límite principal:** no existe fuente abierta y masiva de rebotes, asistencias y defensa de playoffs. El bloque de postemporada mide anotación, títulos e impacto parcial. Russell y Wilt salen penalizados por eso.

## Fuentes

- Basketball-Reference, vía el volcado público de `sumitrodatta/bball-reference-datasets`
- RAPTOR de FiveThirtyEight · CC BY 4.0
- NBA.com para campeones y Finals MVP

Si reutilizas esto, cita las tres.

## Aviso

STATGOAT no está afiliado ni respaldado por la NBA, la NBPA, Basketball-Reference ni FiveThirtyEight. Es un análisis histórico bajo una ponderación concreta: no es predicción, ni recomendación de apuestas, ni una verdad establecida.


