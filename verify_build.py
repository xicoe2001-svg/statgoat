#!/usr/bin/env python3
"""Comprobaciones antes de publicar. Si alguna falla, el Action no despliega.

La idea es que una web rota nunca llegue a producción: es preferible mantener
la versión de la semana pasada.
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


print('Verificando build…')

html = ROOT / 'index.html'
check(html.exists(), 'existe index.html')
size = html.stat().st_size if html.exists() else 0
check(700_000 < size < 6_000_000, f'tamaño del HTML razonable ({size//1024} KB)')

txt = html.read_text(encoding='utf-8') if html.exists() else ''
check('__DATA__' not in txt, 'no queda el marcador de plantilla sin sustituir')
check(txt.count('<script') == txt.count('</script>'), 'etiquetas script balanceadas')
check('NaN' not in txt, 'no hay valores NaN serializados en los datos')

R = pd.read_csv(ROOT / '_build' / 'statgoat_full.csv')
check(len(R) > 2500, f'suficientes jugadores puntuados ({len(R)})')
check(R['STATGOAT'].notna().all(), 'ninguna puntuación es nula')
check(R['STATGOAT'].is_monotonic_decreasing, 'el ranking está ordenado')
check(abs(R['STATGOAT'].max() - 100) < 0.6, f'el líder marca ~100 ({R["STATGOAT"].max():.2f})')

# control de cordura: los nombres del top 15 no deberían cambiar de golpe
top = set(R.head(15)['player'])
esperados = {'LeBron James', 'Michael Jordan', 'Kareem Abdul-Jabbar',
             'Tim Duncan', 'Shaquille O\'Neal', 'Hakeem Olajuwon'}
check(len(top & esperados) >= 5,
      f'el top 15 sigue siendo plausible ({len(top & esperados)}/6 anclas presentes)')

info = json.loads((ROOT / 'build_info.json').read_text(encoding='utf-8'))
check(info.get('season_max', 0) >= 2026, f'la fuente llega a 2026+ ({info.get("season_max")})')
check(info.get('bref_files', 0) >= 15, f'la fuente trae los ficheros esperados ({info.get("bref_files")})')

if fails:
    print(f'\n{len(fails)} comprobaciones fallaron. No se publica.')
    sys.exit(1)
print('\nTodo correcto.')
