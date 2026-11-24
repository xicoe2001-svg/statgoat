#!/usr/bin/env python3
"""Comprobaciones antes de publicar. Si alguna falla, el Action no despliega.

Una web rota o con datos viejos nunca llega a producción: es preferible
mantener la versión anterior y que el fallo se vea en rojo en Actions.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
fails = []


def check(cond, msg):
    print(('  OK   ' if cond else '  FALLA ') + msg)
    if not cond:
        fails.append(msg)


def read(p):
    return pd.read_csv(p) if p.exists() and p.stat().st_size > 0 else pd.DataFrame()


print('Verificando build…')

# ---------------------------------------------------------------- la web
html = ROOT / 'index.html'
check(html.exists(), 'existe index.html')
size = html.stat().st_size if html.exists() else 0
check(700_000 < size < 8_000_000, f'tamaño del HTML razonable ({size//1024} KB)')
txt = html.read_text(encoding='utf-8') if html.exists() else ''
check('__DATA__' not in txt, 'no queda el marcador de plantilla sin sustituir')
check(txt.count('<script') == txt.count('</script>'), 'etiquetas script balanceadas')
check('NaN' not in txt, 'no hay valores NaN serializados en los datos')

# ---------------------------------------------------------------- el índice
R = pd.read_csv(ROOT / '_build' / 'statgoat_full.csv')
check(len(R) > 2500, f'suficientes jugadores puntuados ({len(R)})')
check(R['STATGOAT'].notna().all(), 'ninguna puntuación es nula')
check(R['STATGOAT'].is_monotonic_decreasing, 'el ranking está ordenado')
check(97 <= R['STATGOAT'].max() <= 100.01, f'el líder está entre 97 y 100 ({R["STATGOAT"].max():.2f})')
top = set(R.head(15)['player'])
anclas = {'LeBron James', 'Michael Jordan', 'Kareem Abdul-Jabbar',
          'Tim Duncan', "Shaquille O'Neal", 'Hakeem Olajuwon'}
check(len(top & anclas) >= 5, f'el top 15 sigue siendo plausible ({len(top & anclas)}/6 anclas presentes)')
pos = R.set_index('player_id')['pos']
check(all(pos.get(k) == v for k, v in {'jordami01': 'SG', 'johnsma02': 'PG', 'birdla01': 'SF',
                                        'malonka01': 'PF', 'abdulka01': 'C'}.items()),
      'posiciones: Jordan SG, Magic PG, Bird SF, Malone PF, Kareem C')
check(pos.isin(['PG', 'SG', 'SF', 'PF', 'C']).mean() > 0.9, f"posiciones: {pos.isin(['PG','SG','SF','PF','C']).mean():.0%} de jugadores con posición")
mg = R.set_index('player_id')
check(mg.loc['jordami01', 'rank_p10'] == 1 and (mg['rank_p10'] <= mg['rank']).all() and (mg['rank_p90'] >= mg['rank']).all(),
      f"margen de puesto coherente (Jordan n.º 1 en el {mg.loc['jordami01', 'rank_top1']:.0%} de las ponderaciones)")
DETD = ROOT / 'det'
nd = len(list(DETD.glob('*.json'))) if DETD.exists() else 0
check(nd == len(R), f'detalle de ficha: {nd} archivos en det/ para {len(R)} jugadores')
if (DETD / 'jordami01.json').exists():
    jd = json.loads((DETD / 'jordami01.json').read_text())
    check(len(jd.get('r', [])) == 6 and sum(x[5] for x in jd['r']) == 6 and len(jd.get('s', [])) >= 15,
          'detalle de Jordan: 6 anillos, 6 MVP de las Finales y sus 15 temporadas')
bt = R.set_index('player_id')['BONUS_TOTALES']
check(all(bt.get(p, 0) == 3 for p in ['jamesle01', 'curryst01', 'stockjo01']),
      'bonus: LeBron (puntos), Curry (triples) y Stockton (asistencias) tienen récord')
check(set(bt.round(1).unique()) <= {0.0, 0.6, 1.2, 1.8, 2.4, 3.0},
      'bonus: solo hay valores de puesto en el top 5')

# ---------------------------------------------------------------- frescura
info = json.loads((ROOT / 'build_info.json').read_text(encoding='utf-8'))
smax = int(info.get('season_max', 0))
last_done = smax - 1            # última temporada con playoffs y premios ya terminados
check(smax >= 2027, f'la fuente de temporada regular llega a la temporada en curso ({smax})')
check(info.get('bref_files', 0) >= 15, f'la fuente trae los ficheros esperados ({info.get("bref_files")})')
flog_p = ROOT / 'cache' / 'fetch_log.json'
rc = json.loads(flog_p.read_text()).get('rs_current', {}) if flog_p.exists() else {}
check(rc.get('season', 0) >= smax,
      f"liga regular en curso leída de Basketball-Reference: temporada {rc.get('season', '—')}, "
      f"hasta {rc.get('max_g', '—')} partidos ({str(rc.get('at', '—'))[:10]})")

tot = read(ROOT / 'cache' / 'playoffs_totals.csv')
eds = tot[['season', 'lg']].drop_duplicates() if not tot.empty else pd.DataFrame(columns=['season', 'lg'])
check(len(eds) >= 85, f'playoffs de todas las ediciones desde 1947 ({len(eds)})')
pmax = int(eds['season'].max()) if len(eds) else 0
check(pmax >= last_done, f'playoffs al día: hasta {pmax} (mínimo {last_done})')

ch = pd.read_csv(ROOT / 'champions.csv')
check(int(ch['season'].max()) >= last_done, f'campeón al día: hasta {int(ch["season"].max())}')
fm = pd.read_csv(ROOT / 'finals_mvp.csv')
check(int(fm['season'].max()) >= last_done and fm['player_id'].notna().all(),
      f'Finals MVP al día e identificados: hasta {int(fm["season"].max())}')

aw = pd.concat([read(ROOT / '_raw' / 'bref' / 'Player Award Shares.csv'), read(ROOT / 'cache' / 'awards_extra.csv')])
mvp_max = int(aw[aw['award'] == 'nba mvp']['season'].max())
check(mvp_max >= last_done, f'votaciones de premios al día: MVP hasta {mvp_max}')
eos = pd.concat([read(ROOT / '_raw' / 'bref' / 'End of Season Teams.csv'), read(ROOT / 'cache' / 'eos_extra.csv')])
nba_max = int(eos[eos['type'] == 'All-NBA']['season'].max())
check(nba_max >= last_done, f'equipos All-NBA al día: hasta {nba_max}')

# ---------------------------------------------------------------- datos conocidos
# Si el lector de páginas se rompe, estos valores publicados no cuadrarían.
car = tot.groupby('player_id').agg(g=('g', 'sum'), pts=('pts', 'sum')) if not tot.empty else pd.DataFrame(columns=['g', 'pts'])
if 'jordami01' in car.index:
    ppg = car.loc['jordami01', 'pts'] / car.loc['jordami01', 'g']
    check(abs(ppg - 33.45) < 0.1 and car.loc['jordami01', 'g'] == 179,
          f'Jordan en playoffs: {int(car.loc["jordami01", "g"])} partidos, {ppg:.2f} pts (real: 179, 33.45)')
else:
    check(False, 'Jordan aparece en los playoffs')
sga = tot[(tot.season == 2025) & (tot.player_id == 'gilgesh01')] if not tot.empty else tot
check(len(sga) == 1 and int(sga['pts'].iloc[0]) == 688,
      f'SGA playoffs 2025: {int(sga["pts"].iloc[0]) if len(sga) else "—"} pts (real: 688)')
jok = tot[(tot.season == 2023) & (tot.player_id == 'jokicni01')] if not tot.empty else tot
check(len(jok) == 1 and jok['team'].iloc[0] == 'DEN', 'Jokić aparece en los playoffs de 2023 con DEN')
c25 = ch[ch.season == 2025]
check(len(c25) == 1 and c25['abbrev'].iloc[0] == 'OKC', 'campeón 2025: OKC')

# ---------------------------------------------------------------- mejores temporadas
SF = pd.read_pickle(ROOT / '_build' / 'seasons_full.pkl')
check(len(SF) > 10000, f'temporadas completas medibles ({len(SF)})')
top25 = set(zip(SF.head(25)['player_id'], SF.head(25)['season']))
anc = {('jordami01', 1991), ('jamesle01', 2012), ('onealsh01', 2000), ('duncati01', 2003), ('olajuha01', 1994)}
check(len(top25 & anc) >= 3, f'el top 25 de temporadas es plausible ({len(top25 & anc)}/5 anclas)')

print('\nTop 25 de esta build:')
for i, r in enumerate(R.head(25).itertuples(), 1):
    print(f'  {i:>2}. {r.player:<28} {r.STATGOAT:6.1f}')

if fails:
    print(f'\n{len(fails)} comprobaciones fallaron. No se publica.')
    sys.exit(1)
print('\nTodo correcto.')
