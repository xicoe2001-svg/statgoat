#!/usr/bin/env python3
"""Completa la fuente con lo que el volcado gratuito no trae o trae con retraso.

Descarga de Basketball-Reference, respetando su límite de velocidad:
  1. Estadísticas de playoffs de cada temporada (totales y avanzadas), 1947-hoy,
     incluidas BAA y ABA. Se guardan en cache/ y solo se vuelven a pedir las dos
     últimas temporadas, así que una ejecución normal hace muy pocas peticiones.
  2. Campeón y Finals MVP de las temporadas que aún no estén en champions.csv
     y finals_mvp.csv (se añaden solos).
  3. Votaciones de premios y equipos All-NBA / All-Defensive / All-Rookie de las
     temporadas que el volcado todavía no incluye.
  4. Liga regular de la temporada en curso (totales y avanzadas): el volcado va
     con semanas de retraso, así que se lee cada lunes y el pipeline la usa en
     lugar de la del volcado cuando trae más partidos.

Si Basketball-Reference bloquea o falla, se conserva lo que ya hay en cache/ y
verify_build.py decide si los datos siguen siendo lo bastante recientes.
"""
import csv
import html as HT
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from lxml import html as LH

ROOT = Path(__file__).resolve().parent
BREF = ROOT / '_raw' / 'bref'
CACHE = ROOT / 'cache'
CACHE.mkdir(exist_ok=True)

BASE = 'https://www.basketball-reference.com'
UA = 'Mozilla/5.0 (compatible; STATGOAT/1.0; +https://statgoat.org/)'
DELAY = 4.0             # segundos entre peticiones: 15/min, por debajo de su límite de 20/min
MAX_REQUESTS = 230      # tope por ejecución (la primera descarga completa necesita ~190)
LOG_PATH = CACHE / 'fetch_log.json'

PO_TOT = CACHE / 'playoffs_totals.csv'
PO_ADV = CACHE / 'playoffs_advanced.csv'
AW_EXTRA = CACHE / 'awards_extra.csv'
EOS_EXTRA = CACHE / 'eos_extra.csv'
POW_PATH = CACHE / 'pow.csv'               # Jugador de la semana, todas las temporadas
RS_TOT = CACHE / 'rs_current_totals.csv'
RS_ADV = CACHE / 'rs_current_advanced.csv'
CHAMPS = ROOT / 'champions.csv'
FMVP = ROOT / 'finals_mvp.csv'

TOT_COLS = {'Tm': 'team', 'Team': 'team', 'Pos': 'pos', 'Age': 'age', 'G': 'g', 'GS': 'gs', 'MP': 'mp',
            'FG': 'fg', 'FGA': 'fga', '3P': 'x3p', '3PA': 'x3pa', 'FT': 'ft', 'FTA': 'fta',
            'ORB': 'orb', 'DRB': 'drb', 'TRB': 'trb', 'AST': 'ast', 'STL': 'stl', 'BLK': 'blk',
            'TOV': 'tov', 'PF': 'pf', 'PTS': 'pts'}
ADV_COLS = {'Tm': 'team', 'Team': 'team', 'G': 'g', 'MP': 'mp', 'PER': 'per', 'TS%': 'ts_percent',
            'ORB%': 'orb_percent', 'DRB%': 'drb_percent', 'TRB%': 'trb_percent', 'AST%': 'ast_percent',
            'STL%': 'stl_percent', 'BLK%': 'blk_percent', 'TOV%': 'tov_percent', 'USG%': 'usg_percent',
            'OWS': 'ows', 'DWS': 'dws', 'WS': 'ws', 'WS/48': 'ws_48', 'OBPM': 'obpm', 'DBPM': 'dbpm',
            'BPM': 'bpm', 'VORP': 'vorp'}
RS_ADV_COLS = {**ADV_COLS, 'Pos': 'pos', 'Age': 'age', 'GS': 'gs'}
AWARD_KEYS = [('Most Valuable Player', 'nba mvp'), ('Rookie of the Year', 'nba roy'),
              ('Defensive Player of the Year', 'nba dpoy'), ('Sixth Man', 'nba smoy'),
              ('Most Improved', 'nba mip'), ('Clutch Player', 'nba clutch_poy')]
TEAM_KEYS = [('All-NBA', 'All-NBA'), ('All-Defensive', 'All-Defense'), ('All-Rookie', 'All-Rookie')]
TIER = {'1T': '1st', '2T': '2nd', '3T': '3rd', '1st': '1st', '2nd': '2nd', '3rd': '3rd'}

# ------------------------------------------------------------------ red
class Blocked(Exception):
    pass


class Client:
    def __init__(self):
        self.n = 0
        self.last = 0.0
        self.blocked = None

    def get(self, path):
        """Devuelve el HTML, o None si la página no existe (404)."""
        if self.blocked:
            raise Blocked(self.blocked)
        if self.n >= MAX_REQUESTS:
            raise Blocked(f'tope de {MAX_REQUESTS} peticiones en esta ejecución')
        for attempt in range(3):
            wait = self.last + DELAY - time.time()
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            self.n += 1
            req = urllib.request.Request(BASE + path, headers={'User-Agent': UA, 'Accept': 'text/html'})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return r.read().decode('utf-8', errors='replace')
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                if e.code == 429:
                    ra = e.headers.get('Retry-After')
                    secs = int(ra) if ra and ra.isdigit() else 3600
                    if secs > 90 or attempt == 2:
                        self.blocked = f'429 Too Many Requests (Retry-After {secs}s)'
                        raise Blocked(self.blocked)
                    time.sleep(secs)
                    continue
                if e.code == 403:
                    self.blocked = '403 Forbidden: Basketball-Reference rechaza las peticiones'
                    raise Blocked(self.blocked)
                if attempt == 2:
                    raise
                time.sleep(10 * (attempt + 1))
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == 2:
                    raise
                time.sleep(10 * (attempt + 1))
        return None


# ------------------------------------------------------------------ HTML
PID = re.compile(r'/players/[a-z]/([^/.]+)\.html')
TEAM = re.compile(r'/teams/([A-Z0-9]{2,4})/(\d{4})\.html')


def tables(raw):
    """Todas las tablas de la página, incluidas las que Basketball-Reference
    esconde dentro de comentarios HTML."""
    raw = raw.replace('<!--', '').replace('-->', '')
    doc = LH.fromstring(raw)
    out = []
    for t in doc.iter('table'):
        cap = t.find('caption')
        out.append({'id': t.get('id') or '',
                    'caption': (cap.text_content().strip() if cap is not None else ''),
                    'el': t})
    return doc, out


def cell_list(tr):
    cells = []
    for c in tr.xpath('./th|./td'):
        href = c.xpath('.//a/@href')
        item = (c.text_content().strip(), href[0] if href else None)
        cells.append(item)
        for _ in range(int(c.get('colspan') or 1) - 1):
            cells.append(('', None))
    return cells


def parse_table(t):
    """Lista de filas {cabecera: (texto, enlace)} usando el texto de la cabecera,
    que es más estable que los atributos internos de la página."""
    thead = t.find('thead')
    if thead is None:
        return [], []
    hrows = thead.findall('tr')
    if not hrows:
        return [], []
    hdr = [h for h, _ in cell_list(hrows[-1])]
    body = t.findall('tbody')
    trs = [tr for b in body for tr in b.findall('tr')] if body else t.findall('tr')
    rows = []
    for tr in trs:
        cls = tr.get('class') or ''
        if 'thead' in cls or 'over_header' in cls:
            continue
        cells = cell_list(tr)
        if not cells or all(txt == '' for txt, _ in cells):
            continue
        if cells[0][0] == hdr[0] and len(cells) > 1 and cells[1][0] == hdr[1]:
            continue                                    # cabecera repetida sin clase
        row = {}
        for h, v in zip(hdr, cells):
            if h not in row:                            # primera aparición de cada nombre
                row[h] = v
        rows.append(row)
    return hdr, rows


def num(s):
    s = (s or '').strip().replace(',', '')
    if s in ('', '—', '-'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def pick(tbls, need):
    for t in tbls:
        hdr, rows = parse_table(t['el'])
        if need.issubset(set(hdr)) and rows:
            return hdr, rows
    return None, []


# ------------------------------------------------------------------ parsers
def parse_player_stats(raw, colmap, need):
    _, tbls = tables(raw)
    hdr, rows = pick(tbls, need)
    out = []
    for r in rows:
        txt, href = r.get('Player', ('', None))
        m = PID.search(href or '')
        if not m:
            continue                                    # filas sin jugador (totales de liga, etc.)
        rec = {'player_id': m.group(1), 'player': txt.rstrip('*').strip()}
        for h, k in colmap.items():
            if h in r:
                v = r[h][0]
                rec[k] = v if k in ('team', 'pos') else num(v)
        out.append(rec)
    return out


def parse_season_summary(raw):
    """Campeón (abreviatura del equipo) y Finals MVP (id) de la página de una temporada."""
    flat = re.sub(r'\s+', ' ', raw)
    champ = fmvp = None
    i = flat.find('League Champion')
    if i >= 0:
        m = TEAM.search(flat, i, i + 600)
        if m:
            champ = m.group(1)
    i = flat.find('Finals MVP')
    if i >= 0:
        m = PID.search(flat, i, i + 600)
        nm = re.search(r'<a href="/players/[a-z]/[^"]+">([^<]+)</a>', flat[i:i + 600])
        if m:
            fmvp = (m.group(1), nm.group(1) if nm else '')
    return champ, fmvp


def parse_awards(raw, season):
    """Votaciones de premios y equipos de fin de temporada de awards_<año>.html."""
    _, tbls = tables(raw)
    shares, teams = [], []
    for t in tbls:
        label = f"{t['caption']} {t['id']}"
        hdr, rows = parse_table(t['el'])
        if not rows or 'Player' not in hdr:
            continue
        # equipos All-NBA / All-Defensive / All-Rookie (una fila por jugador, columna de nivel)
        tkey = next((v for k, v in TEAM_KEYS if k.lower() in label.lower()), None)
        if tkey is None and t['id']:
            tid = t['id'].lower()
            tkey = 'All-NBA' if 'all_nba' in tid else 'All-Defense' if 'all_def' in tid else 'All-Rookie' if 'all_rook' in tid else None
        if tkey and ('#Tm' in hdr or 'Tm' in hdr):
            tier_col = '#Tm' if '#Tm' in hdr else hdr[0]
            for r in rows:
                tier = TIER.get(r.get(tier_col, ('', None))[0])
                m = PID.search(r['Player'][1] or '')
                if tier and m:
                    teams.append({'season': season, 'lg': 'NBA', 'type': tkey, 'number_tm': tier,
                                  'player': r['Player'][0].rstrip('*').strip(), 'player_id': m.group(1),
                                  'position': r.get('Pos', ('', None))[0] or None})
            continue
        # votaciones individuales
        akey = next((v for k, v in AWARD_KEYS if k.lower() in label.lower()), None)
        if akey is None and t['id']:
            akey = {'mvp': 'nba mvp', 'roy': 'nba roy', 'dpoy': 'nba dpoy', 'smoy': 'nba smoy',
                    'mip': 'nba mip', 'clutch_poy': 'nba clutch_poy'}.get(t['id'].lower().replace('nba_', ''))
        if akey and 'Share' in hdr:
            for r in rows:
                m = PID.search(r['Player'][1] or '')
                if not m:
                    continue
                rank = (r.get('Rank') or r.get('Rk') or ('', None))[0]
                shares.append({'season': season, 'award': akey,
                               'player': r['Player'][0].rstrip('*').strip(), 'player_id': m.group(1),
                               'age': num(r.get('Age', ('', None))[0]),
                               'first': num(r.get('First', ('', None))[0]),
                               'pts_won': num(r.get('Pts Won', ('', None))[0]),
                               'pts_max': num(r.get('Pts Max', ('', None))[0]),
                               'share': num(r.get('Share', ('', None))[0]),
                               'winner': rank.strip().rstrip('T') == '1'})
    return shares, teams


def parse_pow(raw):
    """Jugadores de la semana: /awards/pow.html lista cada temporada (2026-27),
    cada semana (Oct 26) y su ganador o ganadores (uno por conferencia desde 2001-02)."""
    raw = raw.replace('<!--', '').replace('-->', '')
    mon = 'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
    tok = re.compile(r'<h[1-4][^>]*>\s*(?:<[^>]+>\s*)*(\d{4})-(\d{2})\s*(?:<[^>]+>\s*)*</h[1-4]>'
                     r'|<(?:strong|b)[^>]*>\s*((?:' + mon + r')\.? \d{1,2})\s*</(?:strong|b)>'
                     r'|<a[^>]+href="/players/[a-z]/([^/".]+)\.html"[^>]*>([^<]+)</a>')
    rows, season, week, n = [], None, None, 0
    for m in tok.finditer(raw):
        if m.group(1):
            season, week = int(m.group(1)) + 1, None
        elif m.group(3):
            week, n = m.group(3), 0
        elif m.group(4) and season and week and n < 2:
            rows.append({'season': season, 'week': week, 'player_id': m.group(4),
                         'player': HT.unescape(m.group(5)).strip()})
            n += 1
    return rows


# ------------------------------------------------------------------ caché
def load(path):
    return pd.read_csv(path) if path.exists() and path.stat().st_size > 0 else pd.DataFrame()


def upsert(path, new_rows, keys):
    """Sustituye en la caché las filas de las temporadas recién descargadas."""
    old = load(path)
    new = pd.DataFrame(new_rows)
    if new.empty:
        return old
    if not old.empty:
        drop = old.set_index(keys).index.isin(new[keys].drop_duplicates().set_index(keys).index)
        old = old[~drop]
    out = pd.concat([old, new], ignore_index=True).sort_values(keys + ['player_id'])
    out.to_csv(path, index=False)
    return out


def main():
    log = json.loads(LOG_PATH.read_text()) if LOG_PATH.exists() else {}
    log.setdefault('pages', {})
    adv = pd.read_csv(BREF / 'Advanced.csv', usecols=['season', 'lg'])
    pairs = sorted(set(map(tuple, adv[['season', 'lg']].drop_duplicates().values)))
    smax = int(adv['season'].max())
    cli = Client()
    stats = {'ok': 0, 'missing': 0, 'parse_error': 0, 'skipped': 0}
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')

    def mark(key, status, rows=None):
        log['pages'][key] = {'status': status, 'at': now, **({'rows': rows} if rows is not None else {})}

    try:
        # -------------------------------------------- 0. liga regular en curso
        today = datetime.now(timezone.utc)
        cur = today.year + 1 if today.month >= 9 else today.year
        for season in sorted({smax, cur}):
            for kind, colmap, need, path in [
                    ('totals', TOT_COLS, {'Player', 'G', 'PTS'}, RS_TOT),
                    ('advanced', RS_ADV_COLS, {'Player', 'PER', 'WS'}, RS_ADV)]:
                key = f'leagues/NBA_{season}_{kind}'
                raw = cli.get(f'/leagues/NBA_{season}_{kind}.html')
                if raw is None:
                    mark(key, 'missing'); continue          # temporada aún sin empezar
                rows = parse_player_stats(raw, colmap, need)
                if len(rows) < 100:
                    mark(key, 'parse_error', len(rows)); stats['parse_error'] += 1
                    print(f'  AVISO {key}: solo {len(rows)} filas leídas, no se toca la caché')
                    continue
                for r in rows:
                    r['season'], r['lg'] = season, 'NBA'
                upsert(path, rows, ['season', 'lg'])
                mark(key, 'ok', len(rows)); stats['ok'] += 1
                if kind == 'totals':
                    log['rs_current'] = {'season': season, 'rows': len(rows), 'at': now,
                                         'max_g': int(max((r.get('g') or 0) for r in rows))}
                    print(f'  liga regular {season}: {len(rows)} filas, hasta '
                          f'{log["rs_current"]["max_g"]} partidos por jugador')

        # -------------------------------------------- 1. estadísticas de playoffs
        tot, advp = load(PO_TOT), load(PO_ADV)
        have_tot = set(map(tuple, tot[['season', 'lg']].drop_duplicates().values)) if not tot.empty else set()
        have_adv = set(map(tuple, advp[['season', 'lg']].drop_duplicates().values)) if not advp.empty else set()
        # primero lo reciente (lo que más importa), luego el histórico que falte
        order = sorted(pairs, key=lambda p: (-(p[0] >= smax - 1), -p[0]))
        for season, lg in order:
            recent = season >= smax - 1
            for kind, have, colmap, need, path in [
                    ('totals', have_tot, TOT_COLS, {'Player', 'G', 'PTS'}, PO_TOT),
                    ('advanced', have_adv, ADV_COLS, {'Player', 'PER', 'WS'}, PO_ADV)]:
                key = f'playoffs/{lg}_{season}_{kind}'
                st = log['pages'].get(key, {}).get('status')
                if (season, lg) in have and not recent:
                    continue
                if st == 'missing' and not recent:
                    continue                                # no existe y no va a existir
                raw = cli.get(f'/playoffs/{lg}_{season}_{kind}.html')
                if raw is None:
                    mark(key, 'missing'); stats['missing'] += 1
                    continue
                rows = parse_player_stats(raw, colmap, need)
                if len(rows) < 8:
                    mark(key, 'parse_error', len(rows)); stats['parse_error'] += 1
                    print(f'  AVISO {key}: solo {len(rows)} filas leídas, no se toca la caché')
                    continue
                for r in rows:
                    r['season'], r['lg'] = season, lg
                upsert(path, rows, ['season', 'lg'])
                mark(key, 'ok', len(rows)); stats['ok'] += 1
            if stats['ok'] and stats['ok'] % 20 == 0:
                print(f'  … {stats["ok"]} páginas de playoffs descargadas')

        # -------------------------------------------- 2. campeón y Finals MVP
        ch = pd.read_csv(CHAMPS)
        fm = pd.read_csv(FMVP)
        last_ch = int(ch['season'].max())
        for season in range(last_ch + 1, smax + 1):
            lg = 'NBA'
            raw = cli.get(f'/playoffs/{lg}_{season}.html')
            key = f'playoffs/{lg}_{season}'
            if raw is None:
                mark(key, 'missing'); continue
            champ, fmvp = parse_season_summary(raw)
            if not champ:
                mark(key, 'pending')                        # temporada sin final todavía
                continue
            with open(CHAMPS, 'a', newline='') as fh:
                csv.writer(fh).writerow([season, lg, champ])
            if fmvp and season not in set(fm['season']):
                with open(FMVP, 'a', newline='') as fh:
                    csv.writer(fh).writerow([season, lg, fmvp[0], fmvp[1]])
            mark(key, 'ok')
            print(f'  campeón {season}: {champ} · Finals MVP: {fmvp[1] if fmvp else "—"}')

        # -------------------------------------------- 3. premios que falten
        aw = pd.read_csv(BREF / 'Player Award Shares.csv', usecols=['season'])
        eos = pd.read_csv(BREF / 'End of Season Teams.csv', usecols=['season', 'lg'])
        dump_max = min(int(aw['season'].max()), int(eos[eos.lg == 'NBA']['season'].max()))
        ext = load(AW_EXTRA)
        complete = set(ext[ext.award == 'nba mvp']['season']) if not ext.empty else set()
        sh_all, tm_all = [], []
        for season in range(dump_max + 1, smax + 1):
            if season in complete and season < smax:
                continue
            raw = cli.get(f'/awards/awards_{season}.html')
            key = f'awards/{season}'
            if raw is None:
                mark(key, 'missing'); continue
            sh, tm = parse_awards(raw, season)
            mark(key, 'ok' if sh else 'pending', len(sh) + len(tm))
            if sh:
                sh_all += sh; tm_all += tm
                print(f'  premios {season}: {len(sh)} votos, {len(tm)} plazas en equipos')
        if sh_all:
            upsert(AW_EXTRA, sh_all, ['season'])
        if tm_all:
            upsert(EOS_EXTRA, tm_all, ['season'])

        # -------------------------------------------- 4. jugador de la semana
        # Una sola página con todas las temporadas. Solo sirve para la previsión de
        # Premios de la temporada en curso: si falla, se avisa y se sigue.
        raw = cli.get('/awards/pow.html')
        if raw is None:
            mark('awards/pow', 'missing')
        else:
            rows = parse_pow(raw)
            if len(rows) < 500:
                mark('awards/pow', 'parse_error', len(rows))
                print(f'  AVISO awards/pow: solo {len(rows)} filas leídas, no se toca la caché')
            else:
                pd.DataFrame(rows).to_csv(POW_PATH, index=False)
                mark('awards/pow', 'ok', len(rows)); stats['ok'] += 1
                d = pd.DataFrame(rows)
                last = int(d['season'].max())
                print(f'  jugador de la semana: {len(d)} premios en {d.season.nunique()} temporadas; '
                      f'{last - 1}-{str(last)[-2:]}: {int((d.season == last).sum())} en {d[d.season == last].week.nunique()} semanas')

    except Blocked as e:
        print(f'\nDESCARGA DETENIDA: {e}. Se conserva la caché existente.')
        log['blocked'] = {'at': now, 'reason': str(e)}
    else:
        log.pop('blocked', None)

    # -------------------------------------------- resumen
    tot = load(PO_TOT)
    cov = tot[['season', 'lg']].drop_duplicates() if not tot.empty else pd.DataFrame(columns=['season'])
    log['last_run'] = now
    log['requests'] = cli.n
    log['playoff_seasons_cached'] = int(len(cov))
    log['playoff_max_season'] = int(cov['season'].max()) if len(cov) else None
    LOG_PATH.write_text(json.dumps(log, indent=1, ensure_ascii=False, sort_keys=True))
    print(f'\n{cli.n} peticiones · páginas nuevas {stats["ok"]} · inexistentes {stats["missing"]} · '
          f'errores de lectura {stats["parse_error"]}')
    print(f'Playoffs en caché: {len(cov)} temporadas, hasta {log["playoff_max_season"]}')

    expected = len([p for p in pairs if p[0] < smax])
    if len(cov) < 0.8 * expected:
        print(f'ABORTA: solo hay playoffs de {len(cov)} de {expected} temporadas.')
        sys.exit(1)
    if stats['parse_error'] >= 3:
        print('ABORTA: varias páginas no se han podido leer; puede que Basketball-Reference haya cambiado su formato.')
        sys.exit(1)


if __name__ == '__main__':
    main()
