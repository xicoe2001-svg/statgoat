#!/usr/bin/env python3
"""
STATGOAT - indice compuesto de valor historico de jugadores NBA/BAA/ABA.

Fuente de datos: volcado publico de Basketball-Reference (1947-2026)
  https://github.com/sumitrodatta/bball-reference-datasets
Complementos:
  - RAPTOR historico y moderno (FiveThirtyEight, 1977-2022)
  - PPG de playoffs de carrera (leaderboard Basketball-Reference, top 250)
  - Campeones por temporada y Finals MVP (verificados 2023-2026 por busqueda web)

Principio de diseno: ninguna metrica cruda se compara entre eras. Todo se
convierte a z-score DENTRO de su temporada-liga, contra el grupo de jugadores
cualificados de esa temporada. Se mide dominancia relativa, no produccion bruta.
"""

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
D = ROOT / '_raw'
OUT = ROOT / '_build'
OUT.mkdir(exist_ok=True)

Z_CAP = 4.0          # winsorizado de z-scores
MIN_MP_SEASON = 1000  # temporada "computable" para pico/prime (post-1952)
MIN_G_EARLY = 40      # equivalente pre-1952 (sin minutos registrados)
ABA_DISCOUNT = 0.90   # descuento de fuerza de liga para la ABA

# ---------------------------------------------------------------- carga
def load():
    adv = pd.read_csv(D / 'bref' / 'Advanced.csv')
    pg = pd.read_csv(D / 'bref' / 'Player Per Game.csv')
    tot = pd.read_csv(D / 'bref' / 'Player Totals.csv')
    aw = pd.read_csv(D / 'bref' / 'Player Award Shares.csv')
    eos = pd.read_csv(D / 'bref' / 'End of Season Teams.csv')
    astar = pd.read_csv(D / 'bref' / 'All-Star Selections.csv')
    tsum = pd.read_csv(D / 'bref' / 'Team Summaries.csv')
    tpg = pd.read_csv(D / 'bref' / 'Team Stats Per Game.csv')
    tabb = pd.read_csv(D / 'bref' / 'Team Abbrev.csv')
    career = pd.read_csv(D / 'bref' / 'Player Career Info.csv')
    return adv, pg, tot, aw, eos, astar, tsum, tpg, tabb, career


def dedupe_multiteam(df):
    """Si un jugador cambio de equipo, quedarse solo con la fila agregada (2TM/3TM...)."""
    df = df.copy()
    df['is_agg'] = df['team'].astype(str).str.match(r'^\d TM$|^\dTM$')
    keys = ['season', 'lg', 'player_id']
    has_agg = df.groupby(keys)['is_agg'].transform('max')
    keep = (~has_agg.astype(bool)) | df['is_agg']
    return df[keep].drop_duplicates(subset=keys, keep='first').drop(columns='is_agg')


# ------------------------------------------------- z-scores intra-temporada
def season_z(df, cols, qual_mask, cap=Z_CAP):
    """z-score de cada columna dentro de (season, lg), usando como referencia
    la media/sd del grupo cualificado de esa temporada."""
    out = pd.DataFrame(index=df.index)
    g = df[qual_mask].groupby(['season', 'lg'])
    for c in cols:
        stats = g[c].agg(['mean', 'std']).rename(columns={'mean': f'_m', 'std': f'_s'})
        j = df[['season', 'lg']].merge(stats, left_on=['season', 'lg'],
                                       right_index=True, how='left')
        z = (df[c].values - j['_m'].values) / j['_s'].replace(0, np.nan).values
        out[c + '_z'] = np.clip(z, -cap, cap)
    return out


def wmean(frame, weights):
    """Media ponderada ignorando NaN y renormalizando los pesos disponibles."""
    w = pd.Series(weights)
    sub = frame[list(w.index)]
    mask = sub.notna()
    wm = mask.mul(w, axis=1)
    denom = wm.sum(axis=1).replace(0, np.nan)
    return (sub.fillna(0).mul(w, axis=1).sum(axis=1)) / denom, mask.mul(w, axis=1).sum(axis=1) / w.sum()


# ---------------------------------------------------------------- principal
def build():
    adv, pg, tot, aw, eos, astar, tsum, tpg, tabb, career = load()
    adv = dedupe_multiteam(adv)
    pg = dedupe_multiteam(pg)
    tot = dedupe_multiteam(tot)

    key = ['season', 'lg', 'player_id']
    pgc = ['pts_per_game', 'trb_per_game', 'ast_per_game', 'stl_per_game',
           'blk_per_game', 'tov_per_game', 'mp_per_game']
    s = adv.merge(pg[key + [c for c in pgc if c in pg.columns]], on=key, how='left')
    s = s.merge(tot[key + ['pts', 'trb', 'ast', 'stl', 'blk']].rename(
        columns={c: c + '_tot' for c in ['pts', 'trb', 'ast', 'stl', 'blk']}),
        on=key, how='left')

    # numero de partidos de la temporada (para escalar umbrales)
    tg = tsum[~tsum.team.astype(str).str.contains('League Average', na=False)]
    season_len = tpg.groupby(['season', 'lg'])['g'].median().rename('season_g')
    s = s.merge(season_len, left_on=['season', 'lg'], right_index=True, how='left')
    s['season_g'] = s['season_g'].fillna(82)

    # dws por 48 minutos (dws viene como total)
    s['dws_48'] = np.where(s['mp'] > 0, s['dws'] / s['mp'] * 48, np.nan)
    s['ows_48'] = np.where(s['mp'] > 0, s['ows'] / s['mp'] * 48, np.nan)
    s['tov_neg'] = -s['tov_percent']

    # grupo de referencia de cada temporada
    qual = ((s['mp'] >= 500) |
            (s['mp'].isna() & (s['g'] >= 0.4 * s['season_g'])))

    zcols = ['pts_per_game', 'trb_per_game', 'ast_per_game', 'stl_per_game',
             'blk_per_game', 'ts_percent', 'tov_neg', 'per', 'ws_48', 'bpm',
             'obpm', 'dbpm', 'dws_48', 'stl_percent', 'blk_percent',
             'drb_percent', 'usg_percent']
    Z = season_z(s, zcols, qual)
    s = pd.concat([s.reset_index(drop=True), Z.reset_index(drop=True)], axis=1)

    # --------------------------------------------- dimensiones por temporada
    dims = {
        'PROD': {'pts_per_game_z': .40, 'trb_per_game_z': .20, 'ast_per_game_z': .20,
                 'stl_per_game_z': .10, 'blk_per_game_z': .10},
        'EFIC': {'ts_percent_z': .70, 'tov_neg_z': .30},
        'IMPACTO': {'per_z': .30, 'ws_48_z': .35, 'bpm_z': .35},
        'DEF': {'dbpm_z': .40, 'dws_48_z': .30, 'stl_percent_z': .10,
                'blk_percent_z': .10, 'drb_percent_z': .10},
    }
    for name, w in dims.items():
        val, cov = wmean(s, w)
        s[name] = val
        s[name + '_cov'] = cov

    # descuento ABA
    aba = s['lg'].eq('ABA')
    for name in dims:
        s.loc[aba, name] = s.loc[aba, name] * ABA_DISCOUNT

    # temporada "computable" para pico
    # Una temporada aun en curso tiene minutos parciales y falsearia el pico.
    # Se descarta el ultimo curso si la liga no ha jugado un calendario casi completo.
    last = s['season'].max()
    incomplete = (s['season'] == last) & (s['season_g'] < 0.9 * s.loc[s['season'] == last, 'season_g'].max()) \
        if len(s) else False
    played = s.groupby(['season', 'lg'])['g'].transform('max')
    running = (s['season'] == last) & (played < 65)
    s['countable'] = (((s['mp'] >= MIN_MP_SEASON) |
                       (s['mp'].isna() & (s['g'] >= MIN_G_EARLY)))
                      & ~running)

    # ------------------------------------------------ agregacion de carrera
    def career_dim(gr, col):
        v = gr.loc[gr['countable'], col].dropna().sort_values(ascending=False)
        if len(v) == 0:
            v = gr[col].dropna().sort_values(ascending=False)
        if len(v) == 0:
            return pd.Series({'peak3': np.nan, 'prime7': np.nan, 'sustain': np.nan})
        return pd.Series({
            'peak3': v.head(3).mean(),
            'prime7': v.head(7).mean(),
            'sustain': v.clip(lower=0).sum() / 12.0,
        })

    rows = []
    for pid, gr in s.groupby('player_id'):
        rec = {'player_id': pid, 'player': gr['player'].iloc[-1]}
        for name in dims:
            d = career_dim(gr, name)
            rec[name + '_peak'] = d['peak3']
            rec[name + '_prime'] = d['prime7']
            rec[name + '_sustain'] = d['sustain']
            rec[name + '_cov'] = gr.loc[gr['countable'], name + '_cov'].mean()
        rec['seasons'] = int(gr['countable'].sum())
        rec['g_total'] = gr['g'].sum()
        rec['mp_total'] = gr['mp'].sum()
        rec['pts_total'] = gr['pts_tot'].sum()
        rec['trb_total'] = gr['trb_tot'].sum()
        rec['ast_total'] = gr['ast_tot'].sum()
        rec['stl_total'] = gr['stl_tot'].sum()
        rec['blk_total'] = gr['blk_tot'].sum()
        w = gr['g'].fillna(0)
        rec['rs_ppg'] = np.average(gr['pts_per_game'].fillna(0), weights=w) if w.sum() else np.nan
        rec['first'] = gr['season'].min()
        rec['last'] = gr['season'].max()
        rec['lg_main'] = gr['lg'].mode().iloc[0]
        rows.append(rec)
    C = pd.DataFrame(rows)

    for name in dims:
        C[name + '_sustain_z'] = ((C[name + '_sustain'] - C[name + '_sustain'].mean())
                                  / C[name + '_sustain'].std())
        C[name + '_career'] = (0.40 * C[name + '_peak'] + 0.40 * C[name + '_prime']
                               + 0.20 * C[name + '_sustain_z'])

    return s, C, (adv, aw, eos, astar, tabb, career, tpg)


if __name__ == '__main__':
    s, C, extra = build()
    s.to_pickle(OUT / 'seasons.pkl')
    C.to_pickle(OUT / 'careers_raw.pkl')
    print('player-seasons:', len(s), '| jugadores:', len(C))
    print(C.nlargest(15, 'IMPACTO_career')[['player', 'IMPACTO_career', 'PROD_career', 'seasons']].to_string())
