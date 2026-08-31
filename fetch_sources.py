#!/usr/bin/env python3
"""Descarga las fuentes externas y deja constancia de qué versión se usó.

Se ejecuta cada semana desde GitHub Actions. Si una fuente falla o llega
corrupta, aborta con error: es preferible que la web se quede con los datos
de la semana pasada a que se publique un índice roto.
"""
import csv
import io
import json
import shutil
import sys
import tarfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / '_raw'
RAW.mkdir(parents=True, exist_ok=True)

BREF_TAR = 'https://codeload.github.com/sumitrodatta/bball-reference-datasets/tar.gz/refs/heads/master'
RAPTOR = 'https://raw.githubusercontent.com/fivethirtyeight/data/master/nba-raptor/historical_RAPTOR_by_player.csv'

REQUIRED = ['Advanced.csv', 'Player Per Game.csv', 'Player Totals.csv',
            'Player Award Shares.csv', 'End of Season Teams.csv',
            'All-Star Selections.csv', 'Team Summaries.csv',
            'Team Stats Per Game.csv', 'Team Abbrev.csv']

UA = {'User-Agent': 'statgoat-rebuild/1.0'}


def fetch(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:                       # noqa: BLE001
            last = e
            print(f'  intento {i+1}/{tries} falló: {e}', file=sys.stderr)
    raise SystemExit(f'ABORTA: no se pudo descargar {url} · {last}')


def main():
    info = {'built_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}

    print('Descargando volcado de Basketball-Reference…')
    blob = fetch(BREF_TAR)
    info['bref_bytes'] = len(blob)
    dest = RAW / 'bref'
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as tar:
        members = [m for m in tar.getmembers()
                   if m.isfile() and '/Data/' in m.name and m.name.endswith('.csv')]
        if not members:
            raise SystemExit('ABORTA: el tar no contiene la carpeta Data')
        for m in members:
            with tar.extractfile(m) as s, open(dest / Path(m.name).name, 'wb') as fh:
                shutil.copyfileobj(s, fh)
        info['bref_files'] = len(members)

    missing = [f for f in REQUIRED if not (dest / f).exists()]
    if missing:
        raise SystemExit(f'ABORTA: faltan ficheros en la fuente: {missing}')

    with open(dest / 'Advanced.csv', encoding='utf-8') as fh:
        seasons = {int(r['season']) for r in csv.DictReader(fh) if r.get('season')}
    info['season_min'], info['season_max'] = min(seasons), max(seasons)
    print(f'  {len(members)} ficheros · temporadas {min(seasons)}–{max(seasons)}')

    print('Descargando RAPTOR de FiveThirtyEight…')
    rap = fetch(RAPTOR)
    if len(rap) < 500_000:
        raise SystemExit('ABORTA: RAPTOR llegó demasiado pequeño, posible error de red')
    (RAW / 'raptor_hist.csv').write_bytes(rap)
    info['raptor_bytes'] = len(rap)
    print(f'  {len(rap)//1024} KB')

    for f in ('champions.csv', 'playoff_ppg_career.csv'):
        if not (ROOT / f).exists():
            raise SystemExit(f'ABORTA: falta el fichero estático {f}')
    info['static_ok'] = True

    (ROOT / 'build_info.json').write_text(
        json.dumps(info, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Fuentes listas.')


if __name__ == '__main__':
    main()
