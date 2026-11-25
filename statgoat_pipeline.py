#!/usr/bin/env python3
"""
STATGOAT - indice compuesto de valor historico de jugadores NBA/BAA/ABA.

Fuente de datos: volcado publico de Basketball-Reference (1947-2026)
  https://github.com/sumitrodatta/bball-reference-datasets
Playoffs, campeones, Finals MVP y premios recientes: paginas de
Basketball-Reference via fetch_bref_extra.py (se actualizan solos).

Principio de diseno: ninguna metrica cruda se compara entre eras. Todo se
convierte a z-score DENTRO de su temporada-liga, contra el grupo de jugadores
cualificados de esa temporada. Se mide dominancia relativa, no produccion bruta.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from statistics import NormalDist
from franchises import franchise

ROOT = Path(__file__).resolve().parent
D = ROOT / '_raw'
OUT = ROOT / '_build'
OUT.mkdir(exist_ok=True)

Z_CAP = 4.0          # winsorizado de z-scores
MIN_MP_SEASON = 1000  # temporada "computable" para pico/prime (post-1952)
MIN_G_EARLY = 40      # equivalente pre-1952 (sin minutos registrados)
ABA_DISCOUNT = 0.90   # descuento de fuerza de liga para la ABA
FULL_G = 82           # partidos de una temporada completa (para la temporada en curso)

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
    adv, pg, tot = current_season(adv, pg, tot)
    return adv, pg, tot, aw, eos, astar, tsum, tpg, tabb, career


def current_season(adv, pg, tot):
    """La liga regular de la temporada en curso, leída cada lunes de
    Basketball-Reference (fetch_bref_extra.py), sustituye a la del volcado
    cuando trae más partidos. El resto de temporadas sale del volcado."""
    ct, ca = ROOT / 'cache' / 'rs_current_totals.csv', ROOT / 'cache' / 'rs_current_advanced.csv'
    if not (ct.exists() and ca.exists()):
        return adv, pg, tot
    T, A = pd.read_csv(ct), pd.read_csv(ca)
    div = lambda x, y: (x / y).where(y > 0)
    for season in sorted(set(T['season']) & set(A['season'])):
        t = T[T['season'] == season].copy()
        a = A[A['season'] == season].copy()
        old = tot[(tot['season'] == season) & (tot['lg'] == 'NBA')]
        if len(t) < 100 or len(a) < 100 or t['g'].sum() <= old['g'].sum():
            continue
        t['lg'] = a['lg'] = 'NBA'
        # totales, con los porcentajes que trae el volcado
        t['x2p'], t['x2pa'] = t['fg'] - t['x3p'], t['fga'] - t['x3pa']
        t['fg_percent'], t['x3p_percent'] = div(t['fg'], t['fga']), div(t['x3p'], t['x3pa'])
        t['x2p_percent'], t['ft_percent'] = div(t['x2p'], t['x2pa']), div(t['ft'], t['fta'])
        t['e_fg_percent'] = div(t['fg'] + 0.5 * t['x3p'], t['fga'])
        # por partido
        p = t.copy()
        for c in ['mp', 'fg', 'fga', 'x3p', 'x3pa', 'x2p', 'x2pa', 'ft', 'fta', 'orb', 'drb', 'trb',
                  'ast', 'stl', 'blk', 'tov', 'pf', 'pts']:
            p[c + '_per_game'] = div(p[c], p['g'])
        # avanzadas: tasas de tiro calculadas desde los totales
        a = a.merge(t[['player_id', 'team', 'x3pa', 'fga', 'fta']], on=['player_id', 'team'], how='left')
        a['x3p_ar'], a['f_tr'] = div(a['x3pa'], a['fga']), div(a['fta'], a['fga'])
        drop = lambda df: df[~((df['season'] == season) & (df['lg'] == 'NBA'))]
        tot = pd.concat([drop(tot), t.reindex(columns=tot.columns)], ignore_index=True)
        pg = pd.concat([drop(pg), p.reindex(columns=pg.columns)], ignore_index=True)
        adv = pd.concat([drop(adv), a.reindex(columns=adv.columns)], ignore_index=True)
        print(f'  liga regular {season}: Basketball-Reference ({len(t)} filas, hasta {int(t["g"].max())} '
              f'partidos) en lugar del volcado ({len(old)} filas, hasta {int(old["g"].max()) if len(old) else 0})')
    return adv, pg, tot


def dedupe_multiteam(df):
    """Si un jugador cambio de equipo, quedarse solo con la fila agregada (2TM/3TM...)."""
    df = df.copy()
    df['is_agg'] = df['team'].astype(str).str.match(r'^\d TM$|^\dTM$')
    keys = ['season', 'lg', 'player_id']
    has_agg = df.groupby(keys)['is_agg'].transform('max')
    keep = (~has_agg.astype(bool)) | df['is_agg']
    return df[keep].drop_duplicates(subset=keys, keep='first').drop(columns='is_agg')


# ------------------------------------------------- z-scores intra-temporada
def ts_added(df, pts, ts, qual_mask):
    """Puntos por partido añadidos por eficiencia frente al TS% de su liga ese año.

    TS% de la liga = puntos / intentos de los jugadores cualificados, donde
    intentos = puntos / TS%. Resultado: pts x (1 - TS% liga / TS% propio)."""
    t = df[ts].where(df[ts] > 0)
    ok = qual_mask & t.notna() & df[pts].notna()
    key = [df['season'], df['lg']]
    lg_ts = (df[pts].where(ok).groupby(key).transform('sum')
             / (df[pts] / t).where(ok).groupby(key).transform('sum'))
    return df[pts] * (1 - lg_ts / t)


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


DIMS = ['PROD', 'EFIC', 'IMPACTO', 'DEF']
DIM_W = {
    'PROD': {'pts_per_game_z': .40, 'trb_per_game_z': .20, 'ast_per_game_z': .20,
             'stl_per_game_z': .10, 'blk_per_game_z': .10},
    'EFIC': {'tsa_z': .70, 'tov_neg_z': .30},
    'IMPACTO': {'per_z': .30, 'ws_48_z': .35, 'bpm_z': .35},
    'DEF': {'dbpm_z': .40, 'dws_48_z': .30, 'stl_percent_z': .10,
            'blk_percent_z': .10, 'drb_percent_z': .10},
}
ZCOLS = ['pts_per_game', 'trb_per_game', 'ast_per_game', 'stl_per_game',
         'blk_per_game', 'ts_percent', 'tsa', 'tov_neg', 'per', 'ws_48', 'bpm',
         'obpm', 'dbpm', 'dws_48', 'stl_percent', 'blk_percent',
         'drb_percent', 'usg_percent']
PGC = ['pts_per_game', 'trb_per_game', 'ast_per_game', 'stl_per_game',
       'blk_per_game', 'tov_per_game', 'mp_per_game']
TOTC = ['pts', 'trb', 'ast', 'stl', 'blk', 'x3p']


def team_seasons(s, qual, adv_raw, pg_raw, tot_raw):
    """Temporadas por equipo, para la vista por franquicia.

    Si un jugador fue traspasado, su temporada se parte en una fila por equipo con
    sus números en ese equipo. Cada fila se mide contra el mismo grupo de referencia
    que la temporada entera (la media y la desviación de los cualificados de ese año),
    así que su z significa lo mismo. Las demás temporadas son las de siempre."""
    key = ['season', 'lg', 'player_id']
    k2 = key + ['team']
    a = adv_raw.copy()
    agg = a['team'].astype(str).str.match(r'^\d TM$|^\dTM$|^TOT$')
    multi = agg.groupby([a[c] for c in key]).transform('max').astype(bool)
    sp = a[multi & ~agg].copy()
    pg_ = pg_raw[k2 + [c for c in PGC if c in pg_raw.columns]].drop_duplicates(k2)
    tt_ = tot_raw[k2 + TOTC].drop_duplicates(k2).rename(columns={c: c + '_tot' for c in TOTC})
    sp = sp.merge(pg_, on=k2, how='left').merge(tt_, on=k2, how='left')
    extra = s[key + ['season_g', 'running', 'frac']].drop_duplicates(key)
    sp = sp.merge(extra, on=key, how='left')
    sp['dws_48'] = np.where(sp['mp'] > 0, sp['dws'] / sp['mp'] * 48, np.nan)
    sp['ows_48'] = np.where(sp['mp'] > 0, sp['ows'] / sp['mp'] * 48, np.nan)
    sp['tov_neg'] = -sp['tov_percent']
    # TS% de la liga y media/desviación de cada métrica: los de la temporada entera
    ok = qual & s['ts_percent'].gt(0) & s['pts_per_game'].notna()
    lg = (s[ok].assign(att=s['pts_per_game'] / s['ts_percent'])
          .groupby(['season', 'lg']).agg(p=('pts_per_game', 'sum'), a=('att', 'sum')))
    lg['lg_ts'] = lg['p'] / lg['a']
    sp = sp.merge(lg[['lg_ts']], left_on=['season', 'lg'], right_index=True, how='left')
    t = sp['ts_percent'].where(sp['ts_percent'] > 0)
    sp['tsa'] = sp['pts_per_game'] * (1 - sp['lg_ts'] / t)
    ref = s[qual].groupby(['season', 'lg'])
    for c in ZCOLS:
        st = ref[c].agg(['mean', 'std'])
        j = sp[['season', 'lg']].merge(st, left_on=['season', 'lg'], right_index=True, how='left')
        sp[c + '_z'] = np.clip((sp[c].values - j['mean'].values) / j['std'].replace(0, np.nan).values, -Z_CAP, Z_CAP)
    for name, w in DIM_W.items():
        val, cov = wmean(sp, w)
        sp[name] = val
        sp[name + '_cov'] = cov
    aba = sp['lg'].eq('ABA')
    for name in DIM_W:
        sp.loc[aba, name] = sp.loc[aba, name] * ABA_DISCOUNT
    sp['countable'] = (((sp['mp'] >= MIN_MP_SEASON) |
                        (sp['mp'].isna() & (sp['g'] >= MIN_G_EARLY)))
                       & ~sp['running'].fillna(False).astype(bool))
    sk = s.set_index(key).index
    split = sk.isin(sp.set_index(key).index)
    st = pd.concat([s[~split], sp[[c for c in s.columns if c in sp.columns]]], ignore_index=True)
    st['fr'] = st['team'].map(franchise)
    return st


def careers(s):
    """Agrega las temporadas de cada jugador en su carrera (40 % mejores 3, 40 % mejores 7,
    20 % acumulado). Se llama con todas las temporadas y, para la vista desde 1979-80,
    solo con las de ese año en adelante."""
    dims = DIMS
    # ------------------------------------------------ agregacion de carrera
    def career_dim(gr, col):
        v = gr.loc[gr['countable'], col].dropna().sort_values(ascending=False)
        if len(v) == 0:
            v = gr[col].dropna().sort_values(ascending=False)
        if len(v) == 0:
            return pd.Series({'peak3': np.nan, 'prime7': np.nan, 'sustain': np.nan})
        # La media de las 3 y de las 7 mejores exige 3 y 7 temporadas: las que
        # faltan cuentan como 0 (jugador medio de la liga), no se ignoran.
        return pd.Series({
            'peak3': v.head(3).sum() / 3,
            'prime7': v.head(7).sum() / 7,
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
        rec['x3p_total'] = gr['x3p_tot'].sum(min_count=1)   # sin dato antes de existir la línea de 3
        w = gr['g'].fillna(0)
        rec['rs_ppg'] = np.average(gr['pts_per_game'].fillna(0), weights=w) if w.sum() else np.nan
        rec['first'] = gr['season'].min()
        rec['last'] = gr['season'].max()
        rec['lg_main'] = gr['lg'].mode().iloc[0]
        # posición principal: la que más minutos jugó (antes de 1952, por partidos)
        pp = gr['pos'].fillna('').astype(str).str.split('-').str[0]
        ok = pp.isin(['PG', 'SG', 'SF', 'PF', 'C'])
        pw = gr['mp'].fillna(gr['g'] * 30).fillna(0)
        rec['pos'] = pw[ok].groupby(pp[ok]).sum().idxmax() if ok.any() else ''
        rows.append(rec)
    C = pd.DataFrame(rows)

    # El acumulado se pasa a la misma escala que el pico antes de sumarlo, para
    # que cada porcentaje pese lo que dice. En bruto es una suma muy asimétrica
    # (casi todos los jugadores cerca de 0, las carreras largas a +15) y el
    # "20 %" llegaba a pesar la mitad de la nota. Se usa su percentil:
    # percentil -> puntuación normal -> mismo centro y dispersión que el pico.
    # Referencia: los jugadores que entran en el índice (1+ temporada computable).
    nd = NormalDist()
    ref = C['seasons'] >= 1
    for name in dims:
        pk = C.loc[ref, name + '_peak']
        pool = np.sort(C.loc[ref, name + '_sustain'].dropna().values)
        n = len(pool)
        v = C[name + '_sustain'].values
        pct = (np.searchsorted(pool, v, 'left') + np.searchsorted(pool, v, 'right')) / (2 * n)
        pct = np.clip(pct, 0.5 / n, 1 - 0.5 / n)
        ns = np.array([nd.inv_cdf(q) if np.isfinite(x) else np.nan for q, x in zip(pct, v)])
        C[name + '_sustain_z'] = pk.mean() + pk.std() * ns
        C[name + '_career'] = (0.40 * C[name + '_peak'] + 0.40 * C[name + '_prime']
                               + 0.20 * C[name + '_sustain_z'])
    return C


# ---------------------------------------------------------------- principal
def build():
    adv, pg, tot, aw, eos, astar, tsum, tpg, tabb, career = load()
    adv_raw, pg_raw, tot_raw = adv, pg, tot
    adv = dedupe_multiteam(adv)
    pg = dedupe_multiteam(pg)
    tot = dedupe_multiteam(tot)

    key = ['season', 'lg', 'player_id']
    pgc = ['pts_per_game', 'trb_per_game', 'ast_per_game', 'stl_per_game',
           'blk_per_game', 'tov_per_game', 'mp_per_game']
    s = adv.merge(pg[key + [c for c in pgc if c in pg.columns]], on=key, how='left')
    s = s.merge(tot[key + ['pts', 'trb', 'ast', 'stl', 'blk', 'x3p']].rename(
        columns={c: c + '_tot' for c in ['pts', 'trb', 'ast', 'stl', 'blk', 'x3p']}),
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

    # Temporada en curso: hasta que acaba la liga regular (82 partidos o empiezan
    # los playoffs) no entra en las carreras ni en Mejores temporadas. Sus umbrales
    # de minutos se escalan a la parte de temporada jugada: con 19 partidos, 500
    # minutos los tendrían solo unos pocos titulares y el z saldría sesgado.
    last = s['season'].max()
    played = s.groupby(['season', 'lg'])['g'].transform('max')
    po_csv = ROOT / 'cache' / 'playoffs_totals.csv'
    po_done = set(pd.read_csv(po_csv, usecols=['season'])['season']) if po_csv.exists() else set()
    running = (s['season'] == last) & (played < FULL_G) & (last not in po_done)
    s['running'] = running
    s['frac'] = np.where(running, (played / FULL_G).clip(upper=1.0), 1.0)

    # grupo de referencia de cada temporada
    qual = ((s['mp'] >= 500 * s['frac']) |
            (s['mp'].isna() & (s['g'] >= 0.4 * s['season_g'])))

    # Eficiencia con volumen: puntos por partido añadidos por anotar por encima
    # del True Shooting de la liga = (TS% propio - TS% liga) x intentos.
    # Con el TS% a secas, un pívot que tira 5 veces al 65 % "valía" más que
    # alguien que tira 20 al 63 %.
    s['tsa'] = ts_added(s, 'pts_per_game', 'ts_percent', qual)
    zcols = ZCOLS
    Z = season_z(s, zcols, qual)
    s = pd.concat([s.reset_index(drop=True), Z.reset_index(drop=True)], axis=1)

    # --------------------------------------------- dimensiones por temporada
    dims = DIM_W
    for name, w in dims.items():
        val, cov = wmean(s, w)
        s[name] = val
        s[name + '_cov'] = cov

    # descuento ABA
    aba = s['lg'].eq('ABA')
    for name in dims:
        s.loc[aba, name] = s.loc[aba, name] * ABA_DISCOUNT

    # temporada "computable" para pico: la temporada en curso no cuenta hasta que acaba
    s['countable'] = (((s['mp'] >= MIN_MP_SEASON) |
                       (s['mp'].isna() & (s['g'] >= MIN_G_EARLY)))
                      & ~running)

    C = careers(s)
    st = team_seasons(s, qual.reset_index(drop=True), adv_raw, pg_raw, tot_raw)

    return s, C, (adv, aw, eos, astar, tabb, career, tpg, st)


if __name__ == '__main__':
    s, C, extra = build()
    s.to_pickle(OUT / 'seasons.pkl')
    extra[-1].to_pickle(OUT / 'seasons_team.pkl')
    print('temporadas por equipo:', len(extra[-1]), '| sin franquicia:', int(extra[-1]['fr'].eq('').sum()))
    C.to_pickle(OUT / 'careers_raw.pkl')
    print('player-seasons:', len(s), '| jugadores:', len(C))
    print(C.nlargest(15, 'IMPACTO_career')[['player', 'IMPACTO_career', 'PROD_career', 'seasons']].to_string())
