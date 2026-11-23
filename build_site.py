#!/usr/bin/env python3
"""Ensambla index.html en la raíz, que es de donde GitHub Pages sirve la web."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
head = (ROOT / 'head.html').read_text(encoding='utf-8')
app = (ROOT / 'app.js').read_text(encoding='utf-8')
data = (ROOT / '_build' / 'all.min.json').read_text(encoding='utf-8')
info = json.loads((ROOT / 'build_info.json').read_text(encoding='utf-8'))

if 'const RAW=__DATA__;' not in head:
    raise SystemExit('ABORTA: head.html no contiene el marcador const RAW=__DATA__;')

# recuentos que se muestran en la cabecera
player_seasons = playoff_seasons = playoff_max = None
try:
    import pandas as pd
    player_seasons = int(len(pd.read_pickle(ROOT / '_build' / 'seasons.pkl')))
    ps = pd.read_pickle(ROOT / '_build' / 'playoff_seasons.pkl')
    playoff_seasons, playoff_max = int(len(ps)), int(ps['season'].max())
except Exception as e:                                # noqa: BLE001
    print('AVISO: no se pudieron contar las temporadas:', e)

now = datetime.now(timezone.utc)
meta = {'built': now.strftime('%d/%m/%Y'),
        'built_iso': now.strftime('%Y-%m-%d'),
        'season_max': info.get('season_max'),
        'season_min': info.get('season_min'),
        'player_seasons': player_seasons,
        'playoff_seasons': playoff_seasons,
        'playoff_max': playoff_max}

html = head.replace('const RAW=__DATA__;',
                    f'const BUILD={json.dumps(meta, ensure_ascii=False)};\n'
                    f'const RAW={data};\n{app}')

(ROOT / 'index.html').write_text(html, encoding='utf-8')
(ROOT / 'data.json').write_text(data, encoding='utf-8')
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\n', encoding='utf-8')
# evita que GitHub Pages procese el HTML con Jekyll
(ROOT / '.nojekyll').write_text('', encoding='utf-8')

print(f'index.html · {len(html)//1024} KB · temporadas hasta {meta["season_max"]} · '
      f'{player_seasons} temporadas individuales · {playoff_seasons} de playoffs (hasta {playoff_max})')
