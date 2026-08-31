#!/usr/bin/env python3
"""Exporta el dataset completo de la web: 2.908 jugadores con toda su ficha.

Formato columnar (cabecera + filas como arrays) para reducir el peso del JSON
embebido: sin repetir nombres de campo, el fichero baja de ~1,1 MB a ~600 KB.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_build'
s = pd.read_pickle(OUT / 'seasons.pkl')
R = pd.read_csv(OUT / 'statgoat_full.csv')

ids = set(R.player_id)
s = s[s.player_id.isin(ids)].copy()
s['w'] = s['g'].fillna(0)
s['wm'] = s['mp'].fillna(0)


def wavg(gr, col, wcol='w'):
    v = pd.to_numeric(gr[col], errors='coerce')
    w = gr[wcol].where(v.notna(), 0)
    return float((v.fillna(0) * w).sum() / w.sum()) if w.sum() else None


# --------------------------------------------------- agregados de carrera
rows = {}
for pid, gr in s.groupby('player_id'):
    gr = gr.sort_values('season')
    car = {
        'mpg': wavg(gr, 'mp_per_game'), 'ppg': wavg(gr, 'pts_per_game'),
        'rpg': wavg(gr, 'trb_per_game'), 'apg': wavg(gr, 'ast_per_game'),
        'spg': wavg(gr, 'stl_per_game'), 'bpg': wavg(gr, 'blk_per_game'),
        'topg': wavg(gr, 'tov_per_game'),
        'per': wavg(gr, 'per', 'wm'), 'ts': wavg(gr, 'ts_percent', 'wm'),
        'ws48': wavg(gr, 'ws_48', 'wm'), 'bpm': wavg(gr, 'bpm', 'wm'),
        'obpm': wavg(gr, 'obpm', 'wm'), 'dbpm': wavg(gr, 'dbpm', 'wm'),
        'usg': wavg(gr, 'usg_percent', 'wm'), 'tovp': wavg(gr, 'tov_percent', 'wm'),
        'stlp': wavg(gr, 'stl_percent', 'wm'), 'blkp': wavg(gr, 'blk_percent', 'wm'),
        'drbp': wavg(gr, 'drb_percent', 'wm'), 'orbp': wavg(gr, 'orb_percent', 'wm'),
        'astp': wavg(gr, 'ast_percent', 'wm'),
        'ws': float(pd.to_numeric(gr['ws'], errors='coerce').sum()),
        'vorp': float(pd.to_numeric(gr['vorp'], errors='coerce').sum()),
        'mp': float(pd.to_numeric(gr['mp'], errors='coerce').sum()),
    }
    cs = gr[gr['countable']].copy()
    if len(cs) == 0:
        cs = gr.copy()
    cs['SS'] = (0.22 * cs['PROD'] + 0.10 * cs['EFIC']
                + 0.42 * cs['IMPACTO'] + 0.26 * cs['DEF'])
    best = cs.nlargest(3, 'SS')
    seas = []
    for _, b in best.iterrows():
        seas.append([int(b.season), str(b.team),
                     None if pd.isna(b.pts_per_game) else round(float(b.pts_per_game), 1),
                     None if pd.isna(b.trb_per_game) else round(float(b.trb_per_game), 1),
                     None if pd.isna(b.ast_per_game) else round(float(b.ast_per_game), 1),
                     None if pd.isna(b.per) else round(float(b.per), 1),
                     None if pd.isna(b.ws_48) else round(float(b.ws_48), 3),
                     None if pd.isna(b.bpm) else round(float(b.bpm), 1)])
    teams = list(dict.fromkeys([t for t in gr['team'] if 'TM' not in str(t)]))
    rows[pid] = (car, seas, teams[:6])

# --------------------------------------------------- cabecera columnar
FIELDS = ['rk', 'n', 'sc',                                     # 0-2
          'PROD', 'EFIC', 'IMPACTO', 'DEF', 'PLAYOFFS', 'TITULOS', 'PREMIOS', 'bt',  # 3-10
          'y0', 'y1', 'sea', 'g', 'mp',                        # 11-15
          'mpg', 'ppg', 'rpg', 'apg', 'spg', 'bpg', 'topg',    # 16-22
          'per', 'ts', 'ws48', 'ws', 'bpm', 'obpm', 'dbpm', 'vorp',  # 23-30
          'usg', 'tovp', 'stlp', 'blkp', 'drbp', 'orbp', 'astp',     # 31-37
          'tpts', 'trb', 'tast', 'tstl', 'tblk',               # 38-42
          'po', 'poe',                                          # 43-44
          'ring', 'best', 'fmvp', 'mvp', 'mvps_v', 'dpoy', 'anba', 'adef', 'ast',  # 45-53
          'cov', 'rec', 'lg', 'seas', 'tm']                     # 54-58

r2 = lambda v, d=2: None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), d)
i0 = lambda v: None if pd.isna(v) else int(v)

data = []
for _, r in R.iterrows():
    pid = r.player_id
    car, seas, teams = rows.get(pid, ({}, [], []))
    g = car.get
    data.append([
        int(r['rank']), r['player'], r2(r['STATGOAT']),
        r2(r['PROD'], 3), r2(r['EFIC'], 3), r2(r['IMPACTO'], 3), r2(r['DEF'], 3),
        r2(r['PLAYOFFS'], 3), r2(r['TITULOS'], 3), r2(r['PREMIOS'], 3), r2(r['BONUS_TOTALES']),
        int(r['first']), int(r['last']), int(r['seasons']), i0(r['g_total']), i0(g('mp')),
        r2(g('mpg'), 1), r2(g('ppg'), 1), r2(g('rpg'), 1), r2(g('apg'), 1),
        r2(g('spg'), 1), r2(g('bpg'), 1), r2(g('topg'), 1),
        r2(g('per'), 1), r2(g('ts'), 3), r2(g('ws48'), 3), r2(g('ws'), 1),
        r2(g('bpm'), 1), r2(g('obpm'), 1), r2(g('dbpm'), 1), r2(g('vorp'), 1),
        r2(g('usg'), 1), r2(g('tovp'), 1), r2(g('stlp'), 1), r2(g('blkp'), 1),
        r2(g('drbp'), 1), r2(g('orbp'), 1), r2(g('astp'), 1),
        i0(r['pts_total']), i0(r['trb_total']), i0(r['ast_total']),
        i0(r['stl_total']), i0(r['blk_total']),
        r2(r['po_ppg'], 1), 1 if r['po_estimated'] else 0,
        i0(r['rings']), i0(r['rings_as_best']), i0(r['fmvp']), i0(r['mvps']),
        r2(r['mvp_share'], 2), i0(r['dpoys']), r2(r['allnba_pts'], 1),
        r2(r['alldef_pts'], 1), i0(r['allstar']),
        r2(r['cov_min'], 2), ('' if pd.isna(r['_records']) else str(r['_records'])),
        r['lg_main'], seas, teams,
    ])

payload = {'f': FIELDS, 'd': data}
raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
open(OUT / 'all.min.json', 'w').write(raw)
print('jugadores:', len(data), '| KB:', round(len(raw) / 1024, 1))
