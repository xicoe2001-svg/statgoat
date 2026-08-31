#!/usr/bin/env python3
"""STATGOAT - capa 2: postemporada, premios, anillos, bonus de totales y score final."""

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
D = ROOT
OUT = ROOT / '_build'

# ---- Finals MVP 1969-2026 (Bill Russell Trophy). 2023-2026 verificado por busqueda web.
FMVP = {
    1969: 'Jerry West', 1970: 'Willis Reed', 1971: 'Kareem Abdul-Jabbar',
    1972: 'Wilt Chamberlain', 1973: 'Willis Reed', 1974: 'John Havlicek',
    1975: 'Rick Barry', 1976: 'Jo Jo White', 1977: 'Bill Walton',
    1978: 'Wes Unseld', 1979: 'Dennis Johnson', 1980: 'Magic Johnson',
    1981: 'Cedric Maxwell', 1982: 'Magic Johnson', 1983: 'Moses Malone',
    1984: 'Larry Bird', 1985: 'Kareem Abdul-Jabbar', 1986: 'Larry Bird',
    1987: 'Magic Johnson', 1988: 'James Worthy', 1989: 'Joe Dumars',
    1990: 'Isiah Thomas', 1991: 'Michael Jordan', 1992: 'Michael Jordan',
    1993: 'Michael Jordan', 1994: 'Hakeem Olajuwon', 1995: 'Hakeem Olajuwon',
    1996: 'Michael Jordan', 1997: 'Michael Jordan', 1998: 'Michael Jordan',
    1999: 'Tim Duncan', 2000: "Shaquille O'Neal", 2001: "Shaquille O'Neal",
    2002: "Shaquille O'Neal", 2003: 'Tim Duncan', 2004: 'Chauncey Billups',
    2005: 'Tim Duncan', 2006: 'Dwyane Wade', 2007: 'Tony Parker',
    2008: 'Paul Pierce', 2009: 'Kobe Bryant', 2010: 'Kobe Bryant',
    2011: 'Dirk Nowitzki', 2012: 'LeBron James', 2013: 'LeBron James',
    2014: 'Kawhi Leonard', 2015: 'Andre Iguodala', 2016: 'LeBron James',
    2017: 'Kevin Durant', 2018: 'Kevin Durant', 2019: 'Kawhi Leonard',
    2020: 'LeBron James', 2021: 'Giannis Antetokounmpo', 2022: 'Stephen Curry',
    2023: 'Nikola Jokić', 2024: 'Jaylen Brown', 2025: 'Shai Gilgeous-Alexander',
    2026: 'Jalen Brunson',
}
MVP_2026 = 'Shai Gilgeous-Alexander'   # dataset de premios llega a 2025


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


def main():
    s = pd.read_pickle(OUT / 'seasons.pkl')
    C = pd.read_pickle(OUT / 'careers_raw.pkl')
    aw = pd.read_csv(D / '_raw' / 'bref' / 'Player Award Shares.csv')
    eos = pd.read_csv(D / '_raw' / 'bref' / 'End of Season Teams.csv')
    astar = pd.read_csv(D / '_raw' / 'bref' / 'All-Star Selections.csv')
    tpg = pd.read_csv(D / '_raw' / 'bref' / 'Team Stats Per Game.csv')
    ch = pd.read_csv(D / 'champions.csv')
    tabb = pd.read_csv(D / '_raw' / 'bref' / 'Team Abbrev.csv')
    po = pd.read_csv(D / 'playoff_ppg_career.csv')

    name2id = (s.sort_values('g', ascending=False)
                 .drop_duplicates('player')[['player', 'player_id']]
                 .set_index('player')['player_id'].to_dict())

    # ------------------------------------------------------------ ANILLOS
    champ = ch[['season', 'abbrev']].rename(columns={'abbrev': 'team'}).copy()
    champ['champ'] = True
    r = s.merge(champ, on=['season', 'team'], how='left')
    r['champ'] = r['champ'].fillna(False)
    won = r[r['champ']].copy()
    # peso del anillo por rol: minutos por partido esa temporada (tope en 30 mpg)
    won['mpg'] = np.where(won['g'] > 0, won['mp'] / won['g'], np.nan)
    won['role'] = np.clip(won['mpg'].fillna(won['mp_per_game']) / 30.0, 0.15, 1.0)
    # bonus si fue el mejor jugador del equipo campeon (mayor WS del roster)
    best = won.loc[won.groupby(['season', 'team'])['ws'].idxmax(), ['season', 'team', 'player_id']]
    best['is_best'] = True
    won = won.merge(best, on=['season', 'team', 'player_id'], how='left')
    won['is_best'] = won['is_best'].fillna(False).astype(bool)
    won['champ'] = won['champ'].astype(bool).astype(int)
    won['best_i'] = won['is_best'].astype(int)
    won['ring_credit'] = won['role'] * np.where(won['is_best'], 1.6, 1.0)
    rings = won.groupby('player_id').agg(rings=('champ', 'sum'),
                                         ring_credit=('ring_credit', 'sum'),
                                         rings_as_best=('best_i', 'sum')).reset_index()
    C = C.merge(rings, on='player_id', how='left')

    # ------------------------------------------------------------ FMVP
    fm = pd.Series(FMVP).value_counts().rename_axis('player').reset_index(name='fmvp')
    fm['player_id'] = fm['player'].map(name2id)
    missing = fm[fm.player_id.isna()]
    if len(missing):
        print('AVISO - FMVP sin id:', list(missing.player))
    C = C.merge(fm[['player_id', 'fmvp']].dropna(), on='player_id', how='left')

    # ------------------------------------------------------------ PREMIOS
    mvp = aw[aw.award.isin(['nba mvp', 'aba mvp'])].copy()
    # Parche manual solo mientras la fuente no incluya la votacion de 2026.
    # En cuanto el volcado la traiga, este bloque se desactiva solo.
    already = ((aw.award.isin(['nba mvp'])) & (aw.season >= 2026)).any()
    mvp_extra = pd.DataFrame([] if already else
                             [{'player_id': name2id.get(MVP_2026), 'share': 1.0, 'winner': True}])
    if already:
        print('MVP 2026 ya presente en la fuente: parche manual desactivado')
    m = (mvp.groupby('player_id')
            .agg(mvp_share=('share', 'sum'), mvps=('winner', 'sum')).reset_index())
    for _, row in mvp_extra.iterrows():
        if row.player_id in set(m.player_id):
            m.loc[m.player_id == row.player_id, 'mvp_share'] += 1.0
            m.loc[m.player_id == row.player_id, 'mvps'] += 1
        else:
            m = pd.concat([m, pd.DataFrame([{'player_id': row.player_id,
                                             'mvp_share': 1.0, 'mvps': 1}])])
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

    ast_ = astar.groupby('player_id').size().rename('allstar').reset_index()
    C = C.merge(ast_, on='player_id', how='left')

    # ------------------------------------------------------------ PLAYOFFS
    lg_ppg = (tpg[~tpg.team.astype(str).str.contains('League Average', na=False)]
                .groupby(['season', 'lg'])['pts_per_game'].mean().rename('lg_ppg'))
    env = s.merge(lg_ppg, left_on=['season', 'lg'], right_index=True, how='left')
    env['w'] = env['g'].fillna(0)
    denom = env.groupby('player_id')['w'].sum()
    envm = (env.assign(x=env['lg_ppg'] * env['w']).groupby('player_id')['x'].sum() / denom)
    C['lg_ppg_env'] = C['player_id'].map(envm)
    C = C.merge(po, on='player_id', how='left')
    C['po_ppg_adj'] = C['po_ppg'] / C['lg_ppg_env'] * 100
    C['po_lift'] = C['po_ppg'] - C['rs_ppg']

    # RAPTOR postemporada (1977-2022), WAR de playoffs por temporada disputada
    try:
        rap = pd.read_csv(D / '_raw' / 'raptor_hist.csv')
        rp = (rap.groupby('player_id')
                 .agg(war_po=('war_playoffs', 'sum'),
                      n=('season', 'nunique')).reset_index())
        rp['war_po_per_season'] = rp['war_po'] / rp['n']
        C = C.merge(rp[['player_id', 'war_po', 'war_po_per_season']], on='player_id', how='left')
    except FileNotFoundError:
        C['war_po'] = np.nan; C['war_po_per_season'] = np.nan

    # ------------------------------------------------------------ POOL
    for c in ['rings', 'ring_credit', 'rings_as_best', 'fmvp', 'mvp_share', 'mvps',
              'dpoy_share', 'dpoys', 'allnba_pts', 'alldef_pts', 'allstar']:
        C[c] = C[c].fillna(0)

    # Universo: todo jugador con al menos una temporada de 1.000+ minutos.
    # Por debajo de eso el modelo no tiene nada que medir.
    pool = C[C['seasons'] >= 1].copy()
    print('pool de candidatos:', len(pool))

    # ------------------------------------------------- puntuaciones por bloque
    B = pd.DataFrame({'player_id': pool['player_id'].values,
                      'player': pool['player'].values})
    P = pool.reset_index(drop=True)

    # Un bloque entero puede no existir para una epoca: antes de 1952 no hay
    # minutos, asi que PER, WS/48 y BPM no se pueden calcular y el bloque de
    # Impacto sale vacio para 202 jugadores. Se imputa la mediana del grupo
    # (equivale a neutro) en vez de un cero, que seria un castigo inventado.
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

    # Los jugadores fuera del top-250 de anotacion en playoffs no tienen dato.
    # Imputar el minimo los hundiria (Rodman, Ben Wallace, Draymond). Se estima
    # su anotacion de playoffs con la de temporada regular, que es el mejor
    # predictor disponible, y se marca como estimada.
    P['po_estimated'] = P['po_ppg'].isna()
    po_fill = P['po_ppg'].fillna(P['rs_ppg'])
    P['po_ppg_adj'] = po_fill / P['lg_ppg_env'] * 100
    P['po_lift'] = po_fill - P['rs_ppg']
    po_block = (0.55 * z(P['po_ppg_adj'])
                + 0.20 * z(P['po_lift']).fillna(0)
                + 0.25 * z(P['war_po_per_season']).fillna(0))
    B['PLAYOFFS'] = z(po_block)
    B['_po_est'] = P['po_estimated'].values

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
    B['BASE'] = (97 * (B['raw'] - lo) / (hi - lo)).round(2)
    B['STATGOAT'] = (B['BASE'] + B['BONUS_TOTALES']).round(2)

    meta = P[['player_id', 'po_estimated', 'first', 'last', 'seasons', 'g_total', 'mp_total',
              'rs_ppg', 'po_ppg', 'po_lift', 'pts_total', 'trb_total', 'ast_total',
              'stl_total', 'blk_total', 'rings', 'rings_as_best', 'fmvp', 'mvps',
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
        r = sum(B[k] * v for k, v in ww.items()) + 0.03 * B['BONUS_TOTALES']
        S[nm] = r.rank(ascending=False).astype('Int64')
    S = S.sort_values('BASE').head(25)
    print('\n--- sensibilidad (posicion segun ponderacion) ---')
    print(S.to_string(index=False))
    S.to_csv(OUT / 'sensibilidad.csv', index=False)
    return R


if __name__ == '__main__':
    main()
