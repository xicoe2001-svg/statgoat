#!/usr/bin/env python3
"""STATGOAT - capa 2: playoffs, premios, anillos, bonus de totales y score final.

Todo sale de datos que se actualizan solos:
  - temporada regular y premios históricos: volcado de Basketball-Reference (_raw/bref)
  - playoffs de cada temporada, premios recientes: cache/ (fetch_bref_extra.py)
  - campeones y Finals MVP: champions.csv y finals_mvp.csv (se amplían solos)
"""

import numpy as np
import pandas as pd
from pathlib import Path

from statgoat_pipeline import ts_added

ROOT = Path(__file__).resolve().parent
BREF = ROOT / '_raw' / 'bref'
CACHE = ROOT / 'cache'
OUT = ROOT / '_build'

Z_CAP = 4.0
ABA_DISCOUNT = 0.90
SHRINK_K = 600          # minutos de playoffs que "valen" lo mismo que la previsión por liga regular
PEAK_MIN = 4000         # se mide a cada uno por sus mejores 4.000 minutos de playoffs (≈ 4-5 rondas largas)
PO_SUBDIMS = {
    'PROD': {'pts_pg_z': .40, 'trb_pg_z': .20, 'ast_pg_z': .20, 'stl_pg_z': .10, 'blk_pg_z': .10},
    'EFIC': {'tsa_z': .70, 'tov_neg_z': .30},
    'IMP': {'per_z': .30, 'ws_48_z': .35, 'bpm_z': .35},
}
PO_DIM_W = {'PROD': .30, 'EFIC': .15, 'IMP': .55}


def z(x):
    x = pd.to_numeric(x, errors='coerce')
    return (x - x.mean()) / x.std()


def soft(x, k=2.0):
    """Compresion logaritmica de las colas por encima de |k| SD.

    Los bloques de anillos y premios estan brutalmente sesgados a la derecha
    (11 anillos de Russell, 6 FMVP de Jordan). Sin comprimir, un bloque con
    cola gruesa se come el peso nominal de todos los demas. soft() conserva
    el orden pero devuelve a los pesos su significado."""
    x = pd.to_numeric(x, errors='coerce')
    sgn = np.sign(x)
    a = x.abs()
    return sgn * np.where(a <= k, a, k + k * np.log1p((a - k) / k))


def wmean(frame, weights):
    """Media ponderada ignorando NaN y renormalizando los pesos disponibles."""
    w = pd.Series(weights)
    sub = frame[list(w.index)]
    wm = sub.notna().mul(w, axis=1)
    den = wm.sum(axis=1).replace(0, np.nan)
    return sub.fillna(0).mul(w, axis=1).sum(axis=1) / den


def season_z(df, cols, qual):
    out = pd.DataFrame(index=df.index)
    g = df[qual].groupby(['season', 'lg'])
    for c in cols:
        st = g[c].agg(['mean', 'std'])
        j = df[['season', 'lg']].merge(st, left_on=['season', 'lg'], right_index=True, how='left')
        zz = (df[c].values - j['mean'].values) / j['std'].replace(0, np.nan).values
        out[c + '_z'] = np.clip(zz, -Z_CAP, Z_CAP)
    return out


def merge_extra(dump, extra, keys):
    """Añade al volcado solo las combinaciones (temporada, premio/equipo) que no trae."""
    if extra is None or extra.empty:
        return dump
    have = set(map(tuple, dump[keys].drop_duplicates().values))
    add = extra[[tuple(r) not in have for r in extra[keys].values]]
    if len(add):
        print(f'  + {len(add)} filas recientes que el volcado aún no trae ({sorted(add.season.unique())})')
    return pd.concat([dump, add], ignore_index=True)


def read(path):
    return pd.read_csv(path) if path.exists() and path.stat().st_size > 0 else pd.DataFrame()


# ------------------------------------------------------------------ playoffs
def playoff_seasons():
    tot, adv = read(CACHE / 'playoffs_totals.csv'), read(CACHE / 'playoffs_advanced.csv')
    if tot.empty:
        raise SystemExit('ABORTA: no hay estadísticas de playoffs en cache/. Ejecuta antes fetch_bref_extra.py')
    keep = ['season', 'lg', 'player_id', 'per', 'ts_percent', 'tov_percent', 'usg_percent', 'ows', 'dws',
            'ws', 'ws_48', 'obpm', 'dbpm', 'bpm', 'vorp']
    adv = adv[[c for c in keep if c in adv.columns]] if not adv.empty else pd.DataFrame(columns=keep[:3])
    ps = tot.merge(adv.drop_duplicates(['season', 'lg', 'player_id']), on=['season', 'lg', 'player_id'], how='left')
    ps = ps[ps['g'].fillna(0) > 0].copy()
    for c in ['pts', 'trb', 'ast', 'stl', 'blk']:
        ps[c + '_pg'] = ps[c] / ps['g']
    den = 2 * (ps['fga'].fillna(0) + 0.44 * ps['fta'].fillna(0))
    ps['ts'] = np.where(den > 0, ps['pts'] / den, np.nan)
    ps['ts'] = ps['ts'].fillna(ps.get('ts_percent'))
    ps['tov_neg'] = -ps['tov_percent'] if 'tov_percent' in ps else np.nan
    # peso de cada temporada: minutos jugados; antes de 1952 no hay minutos -> 30 por partido
    ps['w'] = ps['mp'].where(ps['mp'].notna(), ps['g'] * 30.0)
    # Win Shares de playoffs: donde la fuente no las da (primeros años) se estiman
    # con la relación WS/punto de todo el histórico
    have = ps['ws'].notna() & (ps['pts'] > 0)
    ratio = (ps.loc[have, 'ws'] / ps.loc[have, 'pts']).median() if have.any() else 0.0
    ps['ws_f'] = ps['ws'].fillna(ps['pts'] * ratio)

    qual = (ps['g'] >= 3) & ((ps['mp'] >= 60) | ps['mp'].isna())
    ps['tsa'] = ts_added(ps, 'pts_pg', 'ts', qual)      # mismo criterio que en liga regular
    zc = ['pts_pg', 'trb_pg', 'ast_pg', 'stl_pg', 'blk_pg', 'ts', 'tsa', 'tov_neg', 'per', 'ws_48', 'bpm']
    ps = pd.concat([ps, season_z(ps, [c for c in zc if c in ps], qual)], axis=1)
    for d, w in PO_SUBDIMS.items():
        ps['PO_' + d] = wmean(ps, {k: v for k, v in w.items() if k in ps})
    ps['PO_SEASON'] = wmean(ps, {'PO_' + k: v for k, v in PO_DIM_W.items()})
    ps.loc[ps['lg'].eq('ABA'), 'PO_SEASON'] *= ABA_DISCOUNT
    return ps


def playoff_career(ps, C, s):
    """Nivel, plus y volumen de playoffs de cada jugador.

    Nivel: media de sus mejores carreras de playoffs hasta sumar PEAK_MIN minutos,
      igual que la liga regular se mide por las mejores temporadas. Con la media
      de toda la carrera, quien solo tiene años de plenitud sale favorecido frente
      a quien jugó playoffs con 38-40 años.
    Plus: cuánto rindió en cada playoff frente a lo esperable por SU liga regular
      de esa misma temporada (residuo de una recta común: los playoffs son más
      duros que la liga). Media por minutos, contraída hacia 0 con pocos minutos.
    """
    g = ps.dropna(subset=['PO_SEASON']).sort_values('PO_SEASON', ascending=False)
    g['prev'] = g.groupby('player_id')['w'].cumsum() - g['w']
    g['take'] = np.minimum(g['w'], (PEAK_MIN - g['prev']).clip(lower=0))
    g['tx'] = g['take'] * g['PO_SEASON']
    q = g.groupby('player_id').agg(po_w=('w', 'sum'), po_wp=('take', 'sum'), tx=('tx', 'sum'))
    q['Q_peak'] = q['tx'] / q['po_wp']

    # plus frente a la liga regular de la misma temporada
    rs = s[['season', 'lg', 'player_id', 'PROD', 'EFIC', 'IMPACTO']].copy()
    rs['RS_SEASON'] = (PO_DIM_W['PROD'] * rs['PROD'] + PO_DIM_W['EFIC'] * rs['EFIC']
                       + PO_DIM_W['IMP'] * rs['IMPACTO'])
    m = g.merge(rs[['season', 'lg', 'player_id', 'RS_SEASON']], on=['season', 'lg', 'player_id']).dropna(subset=['RS_SEASON'])
    sw = np.sqrt(m['w'].values)
    A = np.column_stack([np.ones(len(m)), m['RS_SEASON']])
    b, *_ = np.linalg.lstsq(A * sw[:, None], m['PO_SEASON'].values * sw, rcond=None)
    m['res'] = m['PO_SEASON'] - A @ b
    pl = m.assign(wr=m['w'] * m['res']).groupby('player_id').agg(w=('w', 'sum'), wr=('wr', 'sum'))
    pl['po_plus'] = pl['wr'] / (pl['w'] + SHRINK_K)
    print(f'  playoffs: esperado = {b[0]:.2f} + {b[1]:.2f} × liga regular de esa temporada ({len(m)} temporadas)')

    def wavg(col):
        d = ps.dropna(subset=[col])
        return (d[col] * d['w']).groupby(d['player_id']).sum() / d.groupby('player_id')['w'].sum()

    agg = ps.groupby('player_id').agg(po_g=('g', 'sum'), po_mp=('mp', 'sum'), po_pts=('pts', 'sum'),
                                      po_trb=('trb', 'sum'), po_ast=('ast', 'sum'),
                                      po_fga=('fga', 'sum'), po_fta=('fta', 'sum'),
                                      po_ws=('ws', lambda s: s.sum(min_count=1)), po_ws_f=('ws_f', 'sum'),
                                      po_runs=('season', 'nunique'))
    agg['po_ppg'] = agg['po_pts'] / agg['po_g']
    agg['po_rpg'] = agg['po_trb'] / agg['po_g']
    agg['po_apg'] = agg['po_ast'] / agg['po_g']
    den = 2 * (agg['po_fga'] + 0.44 * agg['po_fta'])
    agg['po_ts'] = np.where(den > 0, agg['po_pts'] / den, np.nan)
    agg['po_per'] = wavg('per')
    agg['po_bpm'] = wavg('bpm')
    agg['po_mp'] = agg['po_mp'].replace(0, np.nan)
    agg = agg.join(q[['po_w', 'po_wp', 'Q_peak']]).join(pl[['po_plus']])

    C = C.merge(agg.reset_index(), on='player_id', how='left')
    C['po_w'] = C['po_w'].fillna(0)
    C['po_wp'] = C['po_wp'].fillna(0)
    C['po_plus'] = C['po_plus'].fillna(0)
    # previsión de su nivel en playoffs a partir de su carrera en liga regular
    X = C[['PROD_career', 'EFIC_career', 'IMPACTO_career']].copy()
    X = X.fillna(X.median())
    fit = (C['po_w'] >= 1500) & C['Q_peak'].notna()
    A = np.column_stack([np.ones(fit.sum()), X[fit].values])
    beta, *_ = np.linalg.lstsq(A, C.loc[fit, 'Q_peak'].values, rcond=None)
    C['po_prior'] = np.column_stack([np.ones(len(C)), X.values]) @ beta
    r2 = 1 - ((C.loc[fit, 'Q_peak'] - C.loc[fit, 'po_prior']) ** 2).sum() / \
        ((C.loc[fit, 'Q_peak'] - C.loc[fit, 'Q_peak'].mean()) ** 2).sum()
    print(f'  playoffs: previsión desde liga regular ajustada con {int(fit.sum())} jugadores (R²={r2:.2f})')
    # contracción: con pocos minutos manda la previsión; con muchos, lo que hizo de verdad
    C['po_quality'] = ((C['po_wp'] * C['Q_peak'].fillna(0) + SHRINK_K * C['po_prior'])
                       / (C['po_wp'] + SHRINK_K))
    C['po_volume'] = np.log1p(C['po_ws_f'].fillna(0).clip(lower=0))
    return C


def season_ranking(s, ps, aw, eos, astar, ch, fmv):
    """Mejores temporadas completas: los mismos siete bloques del índice, en un solo año.

    Liga regular (producción, eficiencia, impacto, defensa), los playoffs de ese
    año, el anillo según su aportación y los premios de esa temporada. Cada bloque
    se estandariza contra todas las temporadas medibles y se comprime igual que en
    el índice. Solo entran temporadas computables con los cuatro bloques de liga
    regular medibles (desde 1951-52: antes no hay minutos, ni impacto ni defensa).
    """
    key = ['season', 'lg', 'player_id']
    t = s[s['countable'] & s[['PROD', 'EFIC', 'IMPACTO', 'DEF']].notna().all(axis=1)].copy()
    # premios de esa temporada
    mvp = aw[aw.award.isin(['nba mvp', 'aba mvp'])].groupby(['season', 'player_id'])['share'].sum().rename('mvp_share')
    dpoy = aw[aw.award == 'nba dpoy'].groupby(['season', 'player_id'])['share'].sum().rename('dpoy_share')
    e = eos.copy()
    e['val'] = e['number_tm'].map({'1st': 5.0, '2nd': 3.0, '3rd': 1.5}).fillna(1.5)
    anba = e[e.type.isin(['All-NBA', 'All-ABA', 'All-BAA'])].groupby(['season', 'player_id'])['val'].sum().rename('anba')
    tier = (e[e.type.isin(['All-NBA', 'All-ABA', 'All-BAA'])].groupby(['season', 'player_id'])['number_tm']
            .first().rename('anba_tm'))
    d = eos[eos.type == 'All-Defense'].copy()
    d['val'] = d['number_tm'].map({'1st': 3.0, '2nd': 1.5}).fillna(1.5)
    adef = d.groupby(['season', 'player_id'])['val'].sum().rename('adef')
    asg = astar.groupby(['season', 'player_id']).size().rename('allstar')
    for x in (mvp, dpoy, anba, tier, adef, asg):
        t = t.merge(x.reset_index(), on=['season', 'player_id'], how='left')
    for c in ['mvp_share', 'dpoy_share', 'anba', 'adef', 'allstar']:
        t[c] = t[c].fillna(0)
    best = t.groupby('season')[['mvp_share', 'dpoy_share']].transform('max')
    t['mvp_win'] = ((t['mvp_share'] > 0) & t['mvp_share'].eq(best['mvp_share'])).astype(int)
    t['dpoy_win'] = ((t['dpoy_share'] > 0) & t['dpoy_share'].eq(best['dpoy_share'])).astype(int)
    # playoffs de esa temporada (mismo esquema que el bloque de carrera)
    g = ps.dropna(subset=['PO_SEASON']).groupby(key).agg(
        po=('PO_SEASON', 'mean'), pw=('w', 'sum'), pws=('ws_f', 'sum'),
        po_g=('g', 'sum'), po_pts=('pts', 'sum')).reset_index()
    t = t.merge(g, on=key, how='left')
    t['pw'] = t['pw'].fillna(0)
    t['pws'] = t['pws'].fillna(0)
    rs = PO_DIM_W['PROD'] * t['PROD'] + PO_DIM_W['EFIC'] * t['EFIC'] + PO_DIM_W['IMP'] * t['IMPACTO']
    ok = t['po'].notna()
    sw = np.sqrt(t.loc[ok, 'pw'].values)
    A = np.column_stack([np.ones(ok.sum()), rs[ok]])
    b, *_ = np.linalg.lstsq(A * sw[:, None], t.loc[ok, 'po'].values * sw, rcond=None)
    exp = b[0] + b[1] * rs
    t['po_level'] = (t['pw'] * t['po'].fillna(0) + SHRINK_K * exp) / (t['pw'] + SHRINK_K)
    t['po_plus'] = (t['pw'] * (t['po'] - exp)).fillna(0) / (t['pw'] + SHRINK_K)
    t['po_vol'] = np.log1p(t['pws'].clip(lower=0))
    # anillo según la aportación en esa carrera al título, y Finals MVP
    chm = ch.rename(columns={'abbrev': 'team'})[['season', 'lg', 'team']]
    po = ps.merge(chm, on=['season', 'lg', 'team'])
    po['wsp'] = po['ws_f'].clip(lower=0)
    tot = po.groupby(['season', 'team'])['wsp'].transform('sum')
    po['share'] = np.where(tot > 0, po['wsp'] / tot, np.nan)
    top_share = po.loc[po.groupby(['season', 'team'])['wsp'].transform('max').eq(po['wsp']) & (po['wsp'] > 0), 'share'].median()
    po['ring'] = np.clip(1.6 * po['share'] / top_share, 0.05, 2.2)
    t = t.merge(po.groupby(key)['ring'].max().reset_index(), on=key, how='left')
    t['ring'] = t['ring'].fillna(0)
    t = t.merge(fmv[['season', 'player_id']].drop_duplicates().assign(fmvp=1), on=['season', 'player_id'], how='left')
    t['fmvp'] = t['fmvp'].fillna(0).astype(int)
    t['champ'] = (t['ring'] > 0).astype(int)
    # los siete bloques de una temporada
    t['b_PROD'] = soft(z(t['PROD']))
    t['b_EFIC'] = soft(z(t['EFIC']))
    t['b_IMPACTO'] = soft(z(t['IMPACTO']))
    t['b_DEF'] = soft(z(0.75 * z(t['DEF']) + 0.25 * z(t['adef'] + 2.5 * t['dpoy_share'])))
    t['b_PLAYOFFS'] = soft(z(0.55 * z(t['po_level']) + 0.25 * z(t['po_plus']) + 0.20 * z(t['po_vol'])))
    t['b_TITULOS'] = soft(z(0.70 * z(t['ring']) + 0.30 * z(t['fmvp'])))
    t['b_PREMIOS'] = soft(z(0.45 * z(t['mvp_share']) + 0.35 * z(t['anba']) + 0.20 * z(t['allstar'])))
    W = {'PROD': .15, 'EFIC': .07, 'IMPACTO': .20, 'DEF': .13, 'PLAYOFFS': .20, 'TITULOS': .15, 'PREMIOS': .10}
    t['FULL'] = sum(t['b_' + k] * v for k, v in W.items())
    t = t.sort_values('FULL', ascending=False).reset_index(drop=True)
    t['srank'] = np.arange(1, len(t) + 1)
    print(f'  temporadas completas medibles: {len(t)} (desde {int(t.season.min())})')
    print('  mejores: ' + ' | '.join(f"{r.player} {int(r.season) - 1}-{str(int(r.season))[-2:]}"
                                     for r in t.head(5).itertuples()))
    return t


def titles(ps, ch, adv_rs, s):
    """Crédito de cada anillo según la aportación real en esa carrera al título."""
    ch = ch.rename(columns={'abbrev': 'team'})[['season', 'lg', 'team']]
    po = ps.merge(ch, on=['season', 'lg', 'team'])
    po['wsp'] = po['ws_f'].clip(lower=0)
    tot = po.groupby(['season', 'team'])['wsp'].transform('sum')
    po['share'] = np.where(tot > 0, po['wsp'] / tot, np.nan)
    po['is_best'] = po.groupby(['season', 'team'])['wsp'].transform('max').eq(po['wsp']) & (po['wsp'] > 0)
    best_share = po.loc[po['is_best'], 'share'].median()
    po['credit'] = np.clip(1.6 * po['share'] / best_share, 0.05, 2.2)
    print(f'  anillos: parte mediana del mejor jugador de cada campeón = {best_share:.0%} de los WS de su playoff')

    # temporadas de campeones sin datos de playoffs: método anterior (minutos en liga regular)
    covered = set(map(tuple, po[['season', 'team']].drop_duplicates().values))
    rs = adv_rs[~adv_rs['team'].astype(str).str.contains('TM')].merge(ch, on=['season', 'lg', 'team'])
    fb = rs[[(a, b) not in covered for a, b in rs[['season', 'team']].values]].copy()
    if len(fb):
        print(f'  anillos: {fb[["season", "team"]].drop_duplicates().shape[0]} campeones sin datos de playoffs, método por minutos')
        fb['mpg'] = fb['mp'] / fb['g']
        fb['credit'] = np.clip(fb['mpg'] / 30.0, 0.15, 1.0)
        b = fb.groupby(['season', 'team'])['ws'].transform('max').eq(fb['ws'])
        fb['is_best'] = b
        fb.loc[b, 'credit'] *= 1.6
    # en la plantilla en liga regular pero sin jugar esos playoffs (lesión, etc.)
    rs_only = rs[[(a, b) in covered for a, b in rs[['season', 'team']].values]]
    rs_only = rs_only[~rs_only.set_index(['season', 'player_id']).index.isin(
        po.set_index(['season', 'player_id']).index)].copy()
    rs_only['credit'] = 0.05
    rs_only['is_best'] = False

    allr = pd.concat([po[['season', 'player_id', 'credit', 'is_best']],
                      fb[['season', 'player_id', 'credit', 'is_best']] if len(fb) else None,
                      rs_only[['season', 'player_id', 'credit', 'is_best']]], ignore_index=True)
    allr = allr.sort_values('credit', ascending=False).drop_duplicates(['season', 'player_id'])
    allr['best_i'] = allr['is_best'].astype(int)
    return allr.groupby('player_id').agg(rings=('season', 'nunique'), ring_credit=('credit', 'sum'),
                                         rings_as_best=('best_i', 'sum')).reset_index()


# ------------------------------------------------------------------ principal
def main():
    s = pd.read_pickle(OUT / 'seasons.pkl')
    C = pd.read_pickle(OUT / 'careers_raw.pkl')
    adv_rs = pd.read_csv(BREF / 'Advanced.csv', usecols=['season', 'lg', 'team', 'player_id', 'g', 'mp', 'ws'])
    aw = merge_extra(pd.read_csv(BREF / 'Player Award Shares.csv'), read(CACHE / 'awards_extra.csv'), ['season', 'award'])
    eos = merge_extra(pd.read_csv(BREF / 'End of Season Teams.csv'), read(CACHE / 'eos_extra.csv'), ['season', 'type'])
    astar = pd.read_csv(BREF / 'All-Star Selections.csv')
    ch = pd.read_csv(ROOT / 'champions.csv')
    fmv = pd.read_csv(ROOT / 'finals_mvp.csv')

    # ------------------------------------------------------------ PLAYOFFS
    ps = playoff_seasons()
    ps.to_pickle(OUT / 'playoff_seasons.pkl')
    print(f'  playoffs: {len(ps)} temporadas de jugador, {ps[["season", "lg"]].drop_duplicates().shape[0]} ediciones, '
          f'hasta {int(ps.season.max())}')
    C = playoff_career(ps, C, s)
    season_ranking(s, ps, aw, eos, astar, ch, fmv).to_pickle(OUT / 'seasons_full.pkl')

    # ------------------------------------------------------------ ANILLOS Y FMVP
    C = C.merge(titles(ps, ch, adv_rs, s), on='player_id', how='left')
    if fmv['player_id'].isna().any():
        raise SystemExit('ABORTA: finals_mvp.csv tiene jugadores sin identificar')
    C = C.merge(fmv.groupby('player_id').size().rename('fmvp').reset_index(), on='player_id', how='left')

    # ------------------------------------------------------------ PREMIOS
    m = (aw[aw.award.isin(['nba mvp', 'aba mvp'])].groupby('player_id')
           .agg(mvp_share=('share', 'sum'), mvps=('winner', 'sum')).reset_index())
    C = C.merge(m, on='player_id', how='left')
    dpoy = (aw[aw.award == 'nba dpoy'].groupby('player_id')
              .agg(dpoy_share=('share', 'sum'), dpoys=('winner', 'sum')).reset_index())
    C = C.merge(dpoy, on='player_id', how='left')

    pts_tm = {'1st': 5.0, '2nd': 3.0, '3rd': 1.5}
    e = eos.copy()
    e['val'] = e['number_tm'].map(pts_tm).fillna(1.5)
    e.loc[e.lg == 'ABA', 'val'] *= 0.90
    allnba = (e[e.type.isin(['All-NBA', 'All-ABA', 'All-BAA'])]
                .groupby('player_id')['val'].sum().rename('allnba_pts').reset_index())
    alldef = (e[e.type == 'All-Defense'].assign(val=lambda d: d.number_tm.map({'1st': 3.0, '2nd': 1.5}).fillna(1.5))
                .groupby('player_id')['val'].sum().rename('alldef_pts').reset_index())
    C = C.merge(allnba, on='player_id', how='left').merge(alldef, on='player_id', how='left')
    C = C.merge(astar.groupby('player_id').size().rename('allstar').reset_index(), on='player_id', how='left')

    # ------------------------------------------------------------ POOL
    for c in ['rings', 'ring_credit', 'rings_as_best', 'fmvp', 'mvp_share', 'mvps',
              'dpoy_share', 'dpoys', 'allnba_pts', 'alldef_pts', 'allstar', 'po_g', 'po_runs']:
        C[c] = C[c].fillna(0)

    # Universo: todo jugador con al menos una temporada de 1.000+ minutos.
    pool = C[C['seasons'] >= 1].copy()
    print('pool de candidatos:', len(pool))

    B = pd.DataFrame({'player_id': pool['player_id'].values, 'player': pool['player'].values})
    P = pool.reset_index(drop=True)

    # Un bloque entero puede no existir para una epoca: antes de 1952 no hay
    # minutos, asi que PER, WS/48 y BPM no se pueden calcular. Se imputa la
    # mediana del grupo (neutro) en vez de un cero, que seria un castigo inventado.
    def blk(col):
        v = P[col]
        n_missing = int(v.isna().sum())
        if n_missing:
            print(f'  {col}: {n_missing} jugadores sin dato, imputados a la mediana')
        return z(v.fillna(v.median()))

    B['PROD'] = blk('PROD_career')
    B['EFIC'] = blk('EFIC_career')
    B['IMPACTO'] = blk('IMPACTO_career')
    B['DEF'] = z(0.75 * blk('DEF_career')
                 + 0.25 * z(P['alldef_pts'] + 2.5 * P['dpoy_share']).fillna(0))
    # Playoffs: 55 % nivel en sus mejores 4.000 minutos (contraído si jugó pocos)
    #           25 % plus: si crece o se encoge frente a su liga regular de ese año
    #           20 % volumen de aportación acumulada (Win Shares de playoffs)
    B['PLAYOFFS'] = z(0.55 * z(P['po_quality']) + 0.25 * z(P['po_plus']) + 0.20 * z(P['po_volume']))
    B['TITULOS'] = z(0.70 * z(P['ring_credit']) + 0.30 * z(P['fmvp']))
    B['PREMIOS'] = z(0.45 * z(P['mvp_share']) + 0.35 * z(P['allnba_pts'])
                     + 0.20 * z(P['allstar']))

    # ------------------------------------------------- bonus de totales
    tot_cols = ['pts_total', 'trb_total', 'ast_total', 'stl_total', 'blk_total']
    exc = pd.DataFrame(index=P.index)
    for c in tot_cols:
        v = P[c].astype(float)
        q95, mx = v.quantile(0.95), v.max()
        exc[c] = ((v - q95) / (mx - q95)).clip(lower=0).fillna(0)
    B['BONUS_TOTALES'] = 3.0 * exc.max(axis=1)          # 0-3 puntos, solo outliers
    B['_records'] = [', '.join([c.replace('_total', '').upper()
                                for c in tot_cols if P.loc[i, c] == P[c].max()])
                     for i in P.index]

    # ------------------------------------------------- score final
    W = {'PROD': .15, 'EFIC': .07, 'IMPACTO': .20, 'DEF': .13,
         'PLAYOFFS': .20, 'TITULOS': .15, 'PREMIOS': .10}
    for k in W:
        B[k] = soft(B[k])
    B['raw'] = sum(B[k] * v for k, v in W.items())
    lo, hi = B['raw'].min(), B['raw'].max()
    # La nota por defecto no lleva el bonus por totales: los totales en bruto
    # dependen de la época y la longevidad ya cuenta un 20 % en cada bloque.
    # El bonus se exporta y la web lo suma solo si el usuario lo activa.
    B['BASE'] = (100 * (B['raw'] - lo) / (hi - lo)).round(2)
    B['STATGOAT'] = B['BASE']

    P['po_lift'] = P['po_ppg'] - P['rs_ppg']
    meta = P[['player_id', 'first', 'last', 'seasons', 'g_total', 'mp_total',
              'rs_ppg', 'po_ppg', 'po_lift', 'po_g', 'po_mp', 'po_rpg', 'po_apg', 'po_ts', 'po_per',
              'po_ws', 'po_bpm', 'po_runs', 'po_w', 'po_plus',
              'pts_total', 'trb_total', 'ast_total', 'stl_total', 'blk_total',
              'rings', 'rings_as_best', 'ring_credit', 'fmvp', 'mvps',
              'mvp_share', 'dpoys', 'allnba_pts', 'alldef_pts', 'allstar',
              'PROD_cov', 'IMPACTO_cov', 'DEF_cov', 'lg_main']].copy()
    meta['cov_min'] = meta[['PROD_cov', 'IMPACTO_cov', 'DEF_cov']].fillna(0).min(axis=1)
    R = B.merge(meta, on='player_id').sort_values('STATGOAT', ascending=False)
    R.insert(0, 'rank', range(1, len(R) + 1))
    R.to_csv(OUT / 'statgoat_full.csv', index=False)

    cols = ['rank', 'player', 'STATGOAT', 'PROD', 'EFIC', 'IMPACTO', 'DEF',
            'PLAYOFFS', 'TITULOS', 'PREMIOS', 'BONUS_TOTALES']
    print(R.head(30)[cols].to_string(index=False, float_format=lambda x: f'{x:6.2f}'))

    # ------------------------------------------------- analisis de sensibilidad
    scen = {
        'BASE': W,
        'SOLO_IMPACTO': {'IMPACTO': 1.0},
        'SIN_TITULOS': {**W, 'TITULOS': 0.0},
        'PLAYOFFS_DOBLE': {**W, 'PLAYOFFS': 0.40},
        'DEFENSA_DOBLE': {**W, 'DEF': 0.26},
        'SOLO_TEMP_REGULAR': {'PROD': .30, 'EFIC': .15, 'IMPACTO': .35, 'DEF': .20},
    }
    S = B[['player']].copy()
    for nm, ww in scen.items():
        r = sum(B[k] * v for k, v in ww.items())
        S[nm] = r.rank(ascending=False).round().astype('int64')
    S = S.sort_values('BASE').head(25)
    print('\n--- sensibilidad (posicion segun ponderacion) ---')
    print(S.to_string(index=False))
    S.to_csv(OUT / 'sensibilidad.csv', index=False)
    return R


if __name__ == '__main__':
    main()
