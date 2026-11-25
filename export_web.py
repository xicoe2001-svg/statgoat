#!/usr/bin/env python3
"""Exporta el dataset completo de la web: todos los jugadores con toda su ficha.

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
def car_rows(s):
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
    return rows


rows = car_rows(s)

# --------------------------------------------------- cabecera columnar
FIELDS = ['rk', 'n', 'sc',                                     # 0-2
          'PROD', 'EFIC', 'IMPACTO', 'DEF', 'PLAYOFFS', 'TITULOS', 'PREMIOS', 'bt',  # 3-10
          'y0', 'y1', 'sea', 'g', 'mp',                        # 11-15
          'mpg', 'ppg', 'rpg', 'apg', 'spg', 'bpg', 'topg',    # 16-22
          'per', 'ts', 'ws48', 'ws', 'bpm', 'obpm', 'dbpm', 'vorp',  # 23-30
          'usg', 'tovp', 'stlp', 'blkp', 'drbp', 'orbp', 'astp',     # 31-37
          'tpts', 'trb', 'tast', 'tstl', 'tblk',               # 38-42
          'po', 'pog', 'pomp', 'porpg', 'poapg', 'pots', 'poper', 'pows', 'pobpm', 'poruns', 'poplus',  # playoffs
          'ring', 'best', 'fmvp', 'mvp', 'mvps_v', 'dpoy', 'anba', 'adef', 'ast',  # 45-53
          'cov', 'rec', 'lg', 'seas', 'tm',                    # 54-58
          'tx3p', 'pos', 'id', 'r10', 'r90', 't1']             # 59-64

r2 = lambda v, d=2: None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), d)
i0 = lambda v: None if pd.isna(v) else int(v)

def row(r, rows):
    pid = r.player_id
    car, seas, teams = rows.get(pid, ({}, [], []))
    g = car.get
    return [
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
        r2(r['po_ppg'], 1), i0(r['po_g']), i0(r['po_mp']), r2(r['po_rpg'], 1), r2(r['po_apg'], 1),
        r2(r['po_ts'], 3), r2(r['po_per'], 1), r2(r['po_ws'], 1), r2(r['po_bpm'], 1), i0(r['po_runs']),
        (r2(r['po_plus'], 2) if r['po_g'] else None),
        i0(r['rings']), i0(r['rings_as_best']), i0(r['fmvp']), i0(r['mvps']),
        r2(r['mvp_share'], 2), i0(r['dpoys']), r2(r['allnba_pts'], 1),
        r2(r['alldef_pts'], 1), i0(r['allstar']),
        r2(r['cov_min'], 2), ('' if pd.isna(r['_records']) else str(r['_records'])),
        r['lg_main'], seas, teams,
        i0(r['x3p_total']), str(r['pos'] or ''),
        r['player_id'], i0(r['rank_p10']), i0(r['rank_p90']), r2(r['rank_top1'], 3),
    ]


data = [row(r, rows) for _, r in R.iterrows()]

# --------------------------------------------------- por franquicia
# Cada paso de un jugador por una franquicia, con solo lo hecho allí (statgoat_team.csv).
# Un archivo por franquicia en tm/<código>.json que se descarga al elegir el equipo.
from franchises import FR as TFR, NAMES as TNAMES, CURRENT as TCUR
ST = pd.read_pickle(OUT / 'seasons_team.pkl')
ST = ST[ST['fr'].ne('') & ST['fr'].notna()].copy()
ST['w'] = ST['g'].fillna(0)
ST['wm'] = ST['mp'].fillna(0)
FRS = ST.groupby(['player_id', 'season'])['fr'].agg(lambda x: ','.join(sorted(set(x)))).to_dict()
TR = pd.read_csv(OUT / 'statgoat_team.csv')
STE = ST.assign(pid=ST['player_id'], player_id=ST['player_id'] + '|' + ST['fr'])
rows_t = car_rows(STE[STE['player_id'].isin(set(TR['player_id']))])
TMD = ROOT / 'tm'
TMD.mkdir(exist_ok=True)
tms, twritten = {}, 0
iid, irk = FIELDS.index('id'), FIELDS.index('rk')
ir10, ir90, it1 = FIELDS.index('r10'), FIELDS.index('r90'), FIELDS.index('t1')
for fr, g in TR.groupby('fr'):
    out = []
    for _, r in g.sort_values('rank_fr').iterrows():
        x = row(r, rows_t)
        x[iid], x[irk] = r['pid'], int(r['rank_fr'])
        x[ir10] = x[ir90] = x[it1] = None
        out.append(x)
    txt = json.dumps({'d': out}, ensure_ascii=False, separators=(',', ':'))
    f = TMD / f'{fr}.json'
    tms[fr] = [TNAMES.get(fr, fr), len(out), int(fr in TCUR)]
    if not f.exists() or f.read_text() != txt:
        f.write_text(txt); twritten += 1
for f in TMD.glob('*.json'):
    if f.stem not in tms:
        f.unlink()
print(f'por franquicia: {len(TR)} pasos en {len(tms)} franquicias ({twritten} archivos actualizados)')

# --------------------------------------------------- mejores temporadas completas
# Se exportan las 1.200 mejores con los pesos por defecto más las 150 mejores de
# cada bloque, para que el ranking siga siendo correcto si el usuario mueve los pesos.
# La temporada en curso no entra: solo está en su pestaña (yr/).
TA = pd.read_pickle(OUT / 'seasons_full.pkl')
T = TA[TA['live'] == 0]
BK = ['PROD', 'EFIC', 'IMPACTO', 'DEF', 'PLAYOFFS', 'TITULOS', 'PREMIOS']
keep = set(T.index[:1200])
for k in BK:
    keep |= set(T['b_' + k].nlargest(150).index)
TS = T.loc[sorted(keep)]
SFIELDS = ['n', 'y', 'tm', 'lg', *BK, 'ppg', 'rpg', 'apg', 'ts', 'per', 'bpm',
           'pog', 'popg', 'mvp', 'dpoy', 'champ', 'fmvp', 'mvps', 'anba', 'as', 'srk', 'pos', 'id', 'rv', 'pol', 'poe', 'poz', 'pow', 'pows',
           'potw', 'potwp', 'live', 'g', 'mp', 'drk', 'frs']


# --------------------------------------------------- tendencia diaria de la temporada en curso
# Puesto de cada jugador con los pesos por defecto, contando como en la web solo los
# bloques que ya existen (Playoffs y Títulos cuando se juegan). Se guarda el del día
# anterior en cache/live_ranks.json para enseñar cuánto ha subido o bajado.
from datetime import datetime, timezone
DRK, PREV_DATE = {}, None
_lv = TA[TA['live'] == 1]
if len(_lv):
    W0 = {'PROD': 15, 'EFIC': 7, 'IMPACTO': 20, 'DEF': 13, 'PLAYOFFS': 20, 'TITULOS': 15, 'PREMIOS': 10}
    ks = [k for k in BK if not (k == 'PLAYOFFS' and not (_lv['pw'].fillna(0) > 0).any())
          and not (k == 'TITULOS' and not (_lv['champ'] > 0).any())]
    tw = sum(W0[k] for k in ks)
    val = sum(_lv['b_' + k] * W0[k] / tw for k in ks)
    today_rk = {pid: int(i) for i, pid in enumerate(_lv.assign(v=val.values).sort_values('v', ascending=False)['player_id'], 1)}
    lr_path = ROOT / 'cache' / 'live_ranks.json'
    old = json.loads(lr_path.read_text()) if lr_path.exists() else {}
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    season = int(_lv['season'].iloc[0])
    if old.get('season') != season:
        old = {}
    if old.get('date') and old['date'] != today:
        prev, PREV_DATE = old.get('ranks', {}), old['date']
    else:
        prev, PREV_DATE = old.get('prev', {}), old.get('prev_date')
    lr_path.write_text(json.dumps({'season': season, 'date': today, 'ranks': today_rk,
                                   'prev_date': PREV_DATE, 'prev': prev}, separators=(',', ':')))
    if prev:
        DRK = {pid: (prev[pid] - r if pid in prev else 999) for pid, r in today_rk.items()}
    print(f'tendencia diaria: {len(today_rk)} puestos de hoy' + (f', comparados con {PREV_DATE}' if PREV_DATE else ', sin día anterior todavía'))


def srow(r):
    return [
        r['player'], int(r['season']), str(r['team']), r['lg'],
        *[r2(r['b_' + k], 3) for k in BK],
        r2(r['pts_per_game'], 1), r2(r['trb_per_game'], 1), r2(r['ast_per_game'], 1),
        r2(r['ts_percent'], 3), r2(r['per'], 1), r2(r['bpm'], 1),
        i0(r['po_g']), (r2(r['po_pts'] / r['po_g'], 1) if r['po_g'] and r['po_g'] == r['po_g'] else None),
        int(r['mvp_win']), int(r['dpoy_win']), int(r['champ']), int(r['fmvp']),
        r2(r['mvp_share'], 3), ('' if pd.isna(r['anba_tm']) else str(r['anba_tm'])), int(r['allstar'] > 0),
        int(r['srank']), str(r['pos']).split('-')[0] if isinstance(r['pos'], str) else '',
        r['player_id'],
        r2(r['ring'], 2), r2(r['po_level'], 2), r2(r['po_exp'], 2), r2(r['po'], 2), i0(r['pw']), r2(r['pws'], 1),
        int(r['potw']), r2(r['potwp'], 1), int(r['live']), i0(r['g']), i0(r['mp']),
        DRK.get(r['player_id']) if int(r['live']) else None,
        FRS.get((r['player_id'], int(r['season'])), ''),
    ]


sdata = [srow(r) for _, r in TS.iterrows()]

# --------------------------------------------------- por temporada (yr/<año>.json)
# Todas las temporadas medibles de cada año, para la pestaña Por temporada. Se
# descargan al elegir el año. La temporada en curso va marcada con live = 1.
YRD = ROOT / 'yr'
YRD.mkdir(exist_ok=True)
yrs, ywritten = {}, 0
for y, g in TA.groupby('season'):
    txt = json.dumps({'d': [srow(r) for _, r in g.sort_values('FULL', ascending=False).iterrows()]},
                     ensure_ascii=False, separators=(',', ':'))
    f = YRD / f'{int(y)}.json'
    yrs[str(int(y))] = int(len(g))
    if not f.exists() or f.read_text() != txt:
        f.write_text(txt); ywritten += 1
for f in YRD.glob('*.json'):
    if f.stem not in yrs:
        f.unlink()
LIVE = json.loads((OUT / 'season_live.json').read_text())
LIVE['prev_date'] = PREV_DATE
print(f'por temporada: {len(yrs)} años en yr/ ({ywritten} actualizados)'
      + (f" · en curso {LIVE['live'] - 1}-{str(LIVE['live'])[-2:]}: {yrs.get(str(LIVE['live']), 0)} jugadores" if LIVE.get('live') else ''))
SMIN = {k: r2(T['b_' + k].min(), 3) for k in BK}

# --------------------------------------------------- vista desde 1979-80
# Misma nota contando solo lo jugado desde 1979-80. Para quien jugó solo desde
# entonces, sus estadísticas no cambian: basta con su puesto, sus bloques, su bonus
# y su margen. Quien jugó antes y después lleva su ficha entera recalculada.
ERA0 = 1980
E = pd.read_csv(OUT / 'statgoat_1980.csv')
first_all = R.set_index('player_id')['first']
cross = set(E.player_id[E.player_id.map(first_all) < ERA0])
rows80 = car_rows(s[(s['season'] >= ERA0) & s.player_id.isin(cross)])
EF = ['id', 'rk', 'sc', 'PROD', 'EFIC', 'IMPACTO', 'DEF', 'PLAYOFFS', 'TITULOS', 'PREMIOS', 'bt', 'rec', 'r10', 'r90', 't1']
edata = [[r['player_id'], int(r['rank']), r2(r['STATGOAT']),
          *[r2(r[k], 3) for k in EF[3:10]], r2(r['BONUS_TOTALES']),
          ('' if pd.isna(r['_records']) else str(r['_records'])),
          i0(r['rank_p10']), i0(r['rank_p90']), r2(r['rank_top1'], 3)] for _, r in E.iterrows()]
xdata = [row(r, rows80) for _, r in E[E.player_id.isin(cross)].iterrows()]
print('desde 1979-80:', len(edata), 'jugadores |', len(xdata), 'con temporadas antes y después')

payload = {'f': FIELDS, 'd': data, 'sf': SFIELDS, 'sd': sdata, 'smin': SMIN, 'sn': int(len(T)),
           'yrs': yrs, 'ylive': LIVE, 'tms': tms, 'tfr': TFR,
           'e': {'y0': ERA0, 'f': EF, 'd': edata, 'x': xdata, 'sn': int((T['season'] >= ERA0).sum())}}
raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
open(OUT / 'all.min.json', 'w').write(raw)
print('jugadores:', len(data), '| temporadas exportadas:', len(sdata), 'de', len(T), '| KB:', round(len(raw) / 1024, 1))

# ------------------------------------------------------------ detalle por jugador
# Un archivo pequeño por jugador (det/<id>.json) que la web descarga al abrir su
# ficha: temporadas bloque a bloque, playoffs, anillos y premios año a año.
# Solo lleva datos estables (temporadas, crédito de cada anillo, votaciones), así
# que cada lunes cambian los archivos de los jugadores en activo, no todos.
DET = ROOT / 'det'
DET.mkdir(exist_ok=True)
C0 = pd.read_pickle(OUT / 'careers_raw.pkl').set_index('player_id')
PS = pd.read_pickle(OUT / 'playoff_seasons.pkl')
RG = pd.read_pickle(OUT / 'rings.pkl')
SRC = pd.read_pickle(OUT / 'awards_src.pkl')
AW, EOS, AST, FMV = SRC['aw'], SRC['eos'], SRC['astar'], SRC['fmv']
RI = R.set_index('player_id')
SSD = {pid: g for pid, g in T.groupby('player_id')}       # temporadas cerradas, para la evolución
C80 = pd.read_pickle(OUT / 'careers_1980.pkl').set_index('player_id')
EI = E.set_index('player_id')


def rn(x, n=2):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) or pd.isna(x) else round(float(x), n)


mvp = AW[AW.award.isin(['nba mvp', 'aba mvp'])].copy()
mvp['rk'] = mvp.groupby(['season', 'award'])['share'].rank(ascending=False, method='min')
dpo = AW[AW.award == 'nba dpoy']
tier = {'1st': 1, '2nd': 2, '3rd': 3}
anb = EOS[EOS.type.isin(['All-NBA', 'All-ABA', 'All-BAA'])]
adf = EOS[EOS.type == 'All-Defense']
fset = set(zip(FMV.season, FMV.player_id))

g_s = {k: v for k, v in s.groupby('player_id')}
g_ps = {k: v for k, v in PS.groupby('player_id')}
g_rg = {k: v for k, v in RG.groupby('player_id')}
g_mvp = {k: v for k, v in mvp.groupby('player_id')}
g_dpo = {k: v for k, v in dpo.groupby('player_id')}
g_anb = {k: v for k, v in anb.groupby('player_id')}
g_adf = {k: v for k, v in adf.groupby('player_id')}
g_ast = {k: set(v.season) for k, v in AST.groupby('player_id')}

# z-score de cada métrica frente a su liga ese año (columnas 26-40 de cada temporada)
ZC = ['pts_per_game_z', 'trb_per_game_z', 'ast_per_game_z', 'stl_per_game_z', 'blk_per_game_z',
      'tsa_z', 'tov_neg_z', 'per_z', 'ws_48_z', 'bpm_z',
      'dbpm_z', 'dws_48_z', 'stl_percent_z', 'blk_percent_z', 'drb_percent_z']
def det_row(r):
    return [int(r.season), str(r.team), r.lg, rn(r.g, 0), rn(r.mp, 0), int(bool(r.countable)),
            rn(r.PROD), rn(r.EFIC), rn(r.IMPACTO), rn(r.DEF),
            rn(r.pts_per_game, 1), rn(r.trb_per_game, 1), rn(r.ast_per_game, 1),
            rn(r.stl_per_game, 1), rn(r.blk_per_game, 1),
            rn(r.ts_percent, 3), rn(r.tsa, 1), rn(r.tov_percent, 1),
            rn(r.per, 1), rn(r.ws_48, 3), rn(r.bpm, 1),
            rn(r.dbpm, 1), rn(r.dws_48, 3), rn(r.stl_percent, 1), rn(r.blk_percent, 1), rn(r.drb_percent, 1),
            *[rn(getattr(r, c)) for c in ZC]]


# temporadas con traspaso, una fila por equipo (para la ficha por franquicia)
_multi = set(zip(s.loc[s['team'].astype(str).str.match(r'^\d ?TM$'), 'player_id'],
                 s.loc[s['team'].astype(str).str.match(r'^\d ?TM$'), 'season']))
g_sf = {k: v for k, v in ST[[(p, y) in _multi for p, y in zip(ST['player_id'], ST['season'])]].groupby('player_id')}
CT = pd.read_pickle(OUT / 'careers_team.pkl').set_index('player_id')
g_tr = {k: v for k, v in TR.groupby('pid')}

keep_ids, written, total_kb = set(), 0, 0.0
for pid in R['player_id']:
    keep_ids.add(pid)
    d = {}
    ss = g_s.get(pid)
    if ss is not None:
        ss = ss.sort_values('season')
        d['s'] = [det_row(r) for r in ss.itertuples()]
    if pid in g_sf:
        d['sf'] = [det_row(r) for r in g_sf[pid].sort_values(['season', 'mp']).itertuples()]
    if pid in g_tr:                                  # cálculo de cada paso por una franquicia
        d['f'] = {}
        for q in g_tr[pid].itertuples():
            if q.player_id in CT.index:
                c = CT.loc[q.player_id]
                d['f'][q.fr] = {'c': {k: [rn(c[k + '_peak']), rn(c[k + '_prime']), rn(c[k + '_sustain_z']), rn(c[k + '_career'])]
                                      for k in ['PROD', 'EFIC', 'IMPACTO', 'DEF']},
                                'pq': [rn(q.Q_peak), rn(q.po_prior), rn(q.po_quality), rn(q.po_wp, 0), rn(q.po_ws_f, 1)]}
    if pid in C0.index:
        c = C0.loc[pid]
        d['c'] = {k: [rn(c[k + '_peak']), rn(c[k + '_prime']), rn(c[k + '_sustain_z']), rn(c[k + '_career'])]
                  for k in ['PROD', 'EFIC', 'IMPACTO', 'DEF']}
    pp = g_ps.get(pid)
    if pp is not None:
        pp = pp.sort_values('season')
        d['po'] = [[int(r.season), str(r.team), rn(r.g, 0), rn(r.mp, 0), rn(r.pts_pg, 1), rn(r.trb_pg, 1),
                    rn(r.ast_pg, 1), rn(r.bpm, 1), rn(r.ws_f, 1), rn(r.PO_SEASON)] for r in pp.itertuples()]
        q = RI.loc[pid]
        d['pq'] = [rn(q['Q_peak']), rn(q['po_prior']), rn(q['po_quality']), rn(q['po_wp'], 0), rn(q['po_ws_f'], 1)]
    rg = g_rg.get(pid)
    if rg is not None:
        rg = rg.sort_values('season')
        d['r'] = [[int(r.season), str(r.team), rn(r.share, 3), rn(r.credit), int(bool(r.is_best)),
                   int((r.season, pid) in fset)] for r in rg.itertuples()]
    fm_only = sorted(y for (y, p) in fset if p == pid and (rg is None or y not in set(rg.season)))
    if fm_only:
        d['fm'] = [int(y) for y in fm_only]          # Finals MVP sin anillo (West 1969)
    years = {}
    def slot(y):
        return years.setdefault(int(y), [int(y), None, None, 0, 0, 0, 0, None, 0])
    for r in (g_mvp.get(pid) if pid in g_mvp else pd.DataFrame()).itertuples():
        a = slot(r.season); a[1], a[2], a[3] = int(r.rk), rn(r.share, 3), int(bool(r.winner))
    for r in (g_anb.get(pid) if pid in g_anb else pd.DataFrame()).itertuples():
        slot(r.season)[4] = tier.get(r.number_tm, 3)
    for r in (g_adf.get(pid) if pid in g_adf else pd.DataFrame()).itertuples():
        slot(r.season)[5] = tier.get(r.number_tm, 2)
    for y in g_ast.get(pid, ()):
        slot(y)[6] = 1
    for r in (g_dpo.get(pid) if pid in g_dpo else pd.DataFrame()).itertuples():
        a = slot(r.season); a[7], a[8] = rn(r.share, 3), int(bool(r.winner))
    if years:
        d['a'] = [years[y] for y in sorted(years)]
    if pid in SSD:                                   # bloques de cada temporada (gráfica de evolución)
        d['ss'] = [[int(q.season), *[rn(getattr(q, 'b_' + k), 3) for k in BK]]
                   for q in SSD[pid].sort_values('season').itertuples()]
    if pid in EI.index and pid in C80.index:        # vista desde 1979-80
        c, q = C80.loc[pid], EI.loc[pid]
        d['e'] = {'c': {k: [rn(c[k + '_peak']), rn(c[k + '_prime']), rn(c[k + '_sustain_z']), rn(c[k + '_career'])]
                        for k in ['PROD', 'EFIC', 'IMPACTO', 'DEF']},
                  'pq': [rn(q['Q_peak']), rn(q['po_prior']), rn(q['po_quality']), rn(q['po_wp'], 0), rn(q['po_ws_f'], 1)]}
    txt = json.dumps(d, ensure_ascii=False, separators=(',', ':'))
    f = DET / f'{pid}.json'
    total_kb += len(txt) / 1024
    if not f.exists() or f.read_text() != txt:
        f.write_text(txt); written += 1
for f in DET.glob('*.json'):
    if f.stem not in keep_ids:
        f.unlink()
print(f'detalle: {len(keep_ids)} fichas en det/ ({written} actualizadas) | {total_kb / 1024:.1f} MB')
