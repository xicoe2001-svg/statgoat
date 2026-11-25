"""Franquicias de la NBA, la ABA y la BAA.

Cada sigla de Basketball-Reference se asigna a su franquicia actual siguiendo la
historia oficial de la NBA (los Minneapolis Lakers son los Lakers, los Sonics son
los Thunder, los Bullets son los Wizards y los Hornets de 1988-2002 son Charlotte).
Los equipos de la ABA que entraron en la NBA (Nets, Nuggets, Pacers, Spurs) llevan
sus años ABA. Los equipos desaparecidos se agrupan por su linaje y van aparte.
"""

FR = {
    # actuales
    'ATL': 'ATL', 'TRI': 'ATL', 'MLH': 'ATL', 'STL': 'ATL',
    'BOS': 'BOS',
    'BRK': 'BRK', 'NJN': 'BRK', 'NYN': 'BRK', 'NYA': 'BRK', 'NJA': 'BRK',
    'CHO': 'CHA', 'CHA': 'CHA', 'CHH': 'CHA',
    'CHI': 'CHI',
    'CLE': 'CLE',
    'DAL': 'DAL',
    'DEN': 'DEN', 'DNA': 'DEN', 'DNR': 'DEN',
    'DET': 'DET', 'FTW': 'DET',
    'GSW': 'GSW', 'SFW': 'GSW', 'PHW': 'GSW',
    'HOU': 'HOU', 'SDR': 'HOU',
    'IND': 'IND', 'INA': 'IND',
    'LAC': 'LAC', 'SDC': 'LAC', 'BUF': 'LAC',
    'LAL': 'LAL', 'MNL': 'LAL',
    'MEM': 'MEM', 'VAN': 'MEM',
    'MIA': 'MIA',
    'MIL': 'MIL',
    'MIN': 'MIN',
    'NOP': 'NOP', 'NOH': 'NOP', 'NOK': 'NOP',
    'NYK': 'NYK',
    'OKC': 'OKC', 'SEA': 'OKC',
    'ORL': 'ORL',
    'PHI': 'PHI', 'SYR': 'PHI',
    'PHO': 'PHO',
    'POR': 'POR',
    'SAC': 'SAC', 'KCK': 'SAC', 'KCO': 'SAC', 'CIN': 'SAC', 'ROC': 'SAC',
    'SAS': 'SAS', 'SAA': 'SAS', 'TEX': 'SAS', 'DLC': 'SAS',
    'TOR': 'TOR',
    'UTA': 'UTA', 'NOJ': 'UTA',
    'WAS': 'WAS', 'WSB': 'WAS', 'CAP': 'WAS', 'BAL': 'WAS', 'CHZ': 'WAS', 'CHP': 'WAS',
    # desaparecidos (BAA y NBA)
    'AND': 'AND', 'BLB': 'BLB', 'CHS': 'CHS', 'CLR': 'CLR', 'DTF': 'DTF', 'DNN': 'DNN',
    'INJ': 'INJ', 'INO': 'INO', 'PIT': 'PIT', 'PRO': 'PRO', 'SHE': 'SHE', 'STB': 'STB',
    'TRH': 'TRH', 'WAT': 'WAT', 'WSC': 'WSC',
    # desaparecidos (ABA), por linaje
    'KEN': 'KEN',
    'ANA': 'UTS', 'LAS': 'UTS', 'UTS': 'UTS',
    'OAK': 'VIR', 'WSA': 'VIR', 'VIR': 'VIR',
    'HSM': 'SSL', 'CAR': 'SSL', 'SSL': 'SSL',
    'NOB': 'MMS', 'MMP': 'MMS', 'MMT': 'MMS', 'MMS': 'MMS',
    'PTP': 'PTC', 'MNP': 'PTC', 'PTC': 'PTC',
    'MNM': 'FLO', 'MMF': 'FLO', 'FLO': 'FLO',
    'SDA': 'SDS', 'SDS': 'SDS',
}

NAMES = {
    'ATL': 'Atlanta Hawks', 'BOS': 'Boston Celtics', 'BRK': 'Brooklyn Nets', 'CHA': 'Charlotte Hornets',
    'CHI': 'Chicago Bulls', 'CLE': 'Cleveland Cavaliers', 'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets',
    'DET': 'Detroit Pistons', 'GSW': 'Golden State Warriors', 'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers',
    'LAC': 'Los Angeles Clippers', 'LAL': 'Los Angeles Lakers', 'MEM': 'Memphis Grizzlies', 'MIA': 'Miami Heat',
    'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves', 'NOP': 'New Orleans Pelicans', 'NYK': 'New York Knicks',
    'OKC': 'Oklahoma City Thunder', 'ORL': 'Orlando Magic', 'PHI': 'Philadelphia 76ers', 'PHO': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers', 'SAC': 'Sacramento Kings', 'SAS': 'San Antonio Spurs', 'TOR': 'Toronto Raptors',
    'UTA': 'Utah Jazz', 'WAS': 'Washington Wizards',
    'AND': 'Anderson Packers', 'BLB': 'Baltimore Bullets (1947-55)', 'CHS': 'Chicago Stags', 'CLR': 'Cleveland Rebels',
    'DTF': 'Detroit Falcons', 'DNN': 'Denver Nuggets (1949-50)', 'INJ': 'Indianapolis Jets', 'INO': 'Indianapolis Olympians',
    'PIT': 'Pittsburgh Ironmen', 'PRO': 'Providence Steamrollers', 'SHE': 'Sheboygan Red Skins', 'STB': 'St. Louis Bombers',
    'TRH': 'Toronto Huskies', 'WAT': 'Waterloo Hawks', 'WSC': 'Washington Capitols',
    'KEN': 'Kentucky Colonels (ABA)', 'UTS': 'Utah Stars (ABA)', 'VIR': 'Virginia Squires (ABA)',
    'SSL': 'Spirits of St. Louis (ABA)', 'MMS': 'Memphis Sounds (ABA)', 'PTC': 'Pittsburgh Condors (ABA)',
    'FLO': 'The Floridians (ABA)', 'SDS': 'San Diego Sails (ABA)',
}
CURRENT = ['ATL', 'BOS', 'BRK', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM',
           'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']


def franchise(team):
    return FR.get(str(team), '')
