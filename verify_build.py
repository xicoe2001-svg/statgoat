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
check(abs(R['STATGOAT'].max() - 100) < 0.6, f'el líder marca ~100 ({R["STATGOAT"].max():.2f})')
top = set(R.head(15)['player'])
anclas = {'LeBron James', 'Michael Jordan', 'Kareem Abdul-Jabbar',
          'Tim Duncan', "Shaquille O'Neal", 'Hakeem Olajuwon'}
check(len(top & anclas) >= 5, f'el top 15 sigue siendo plausible ({len(top & anclas)}/6 anclas presentes)')

# ---------------------------------------------------------------- frescura
info = json.loads((ROOT / 'build_info.json').read_text(encoding='utf-8'))
smax = int(info.get('season_max', 0))
last_done = smax - 1            # última temporada con playoffs y premios ya terminados
check(smax >= 2027, f'la fuente de temporada regular llega a la temporada en curso ({smax})')
check(info.get('bref_files', 0) >= 15, f'la fuente trae los ficheros esperados ({info.get("bref_files")})')

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

print('\nTop 25 de esta build:')
for i, r in enumerate(R.head(25).itertuples(), 1):
    print(f'  {i:>2}. {r.player:<28} {r.STATGOAT:6.1f}')

if fails:
    print(f'\n{len(fails)} comprobaciones fallaron. No se publica.')
    sys.exit(1)
print('\nTodo correcto.')
