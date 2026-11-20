/* ---------- descompresión columnar ---------- */
const F={}; RAW.f.forEach((k,i)=>F[k]=i);
const P=RAW.d;
const get=(p,k)=>p[F[k]];

/* ---------- datos de compilación ---------- */
const BI=(typeof BUILD!=='undefined'&&BUILD)?BUILD:{};
const MAXY=Math.max(...P.map(p=>get(p,'y1')));
const SMAX=BI.season_max||MAXY;
const seasonLabel=y=>`${y-1}-${String(y).slice(2)}`;

/* ---------- textos ES / EN ---------- */
const I18N={
es:{
  locale:'es-ES', dec:',',
  title:`STATGOAT · índice histórico NBA 1947–${SMAX}`,
  sub:'Índice compuesto de jugadores de BAA, NBA y ABA. Ninguna estadística se compara en bruto entre épocas: todo se convierte a desviaciones típicas dentro de su propia temporada. <b>El orden no lo deciden los datos, lo deciden los pesos.</b>',
  st_players:'JUGADORES', st_years:'TEMPORADAS', st_ps:'TEMPORADAS INDIVIDUALES', st_blocks:'BLOQUES PONDERABLES', st_sources:'FUENTES DE DATOS',
  info_h:'Qué datos existían en cada época',
  info_sub:'A cada jugador se le puntúa solo con lo que su época registró, renormalizando los pesos disponibles. No se le castiga con ceros, pero sus bloques descansan sobre menos indicadores.',
  e1m:'Pts · Reb · As · TC · TL', e1n:'Solo box score básico',
  e2m:'+ Minutos · PER · WS/48', e2n:'Primeras métricas derivadas',
  e3m:'+ Pérdidas · USG% · TOV%', e3n:'Control ofensivo',
  e4m:'+ Tapones · Robos', e4n:'La defensa empieza a medirse',
  e5m:'+ BPM · VORP · DBPM', e5n:'Impacto estimado por posesión',
  e6m:'+ Triple', e6n:'Transición al juego moderno',
  e7m:'+ On/Off · Play-by-play', e7n:'Más/menos por quinteto',
  e8y:'2013–hoy', e8m:'+ Tracking óptico', e8n:'Posición de jugador y balón',
  c_weights:'PESOS', c_live:'CON ESTOS PESOS',
  bonus:'Sumar bonus por totales extraordinarios (máx. 3 pts)',
  search:'Buscar jugador…', th_player:'Jugador', th_bar:'De dónde sale la puntuación', th_score:'Punt.',
  cr_h:'Fuentes y atribución',
  cr_br:`Box score completo, métricas avanzadas, votaciones de premios, All-NBA, All-Defensivo y All-Star. 1947–${SMAX}, temporada regular. Anotación de playoffs de carrera del leaderboard público.`,
  cr_538:'RAPTOR histórico y moderno: impacto ofensivo y defensivo combinando box score con más/menos por quinteto. Cobertura 1977–2022.',
  cr_nba:'Campeones por temporada y Finals MVP 1947–2026, con verificación independiente para las temporadas 2023 a 2026.',
  cr_sg_h:'Índice STATGOAT',
  cr_sg1:'La transformación es propia: z-scores intra-temporada, compresión logarítmica de colas, ponderación de anillos por rol real y composición de los siete bloques.',
  cr_sg2:'La ponderación es una opinión formalizada, y por eso se puede cambiar arriba.',
  lg_attr:'<b>Atribución.</b> Los datos originales conservan sus licencias de origen. Si reutilizas este índice, cita Basketball-Reference, FiveThirtyEight y NBA.com.',
  lg_aff:'<b>Sin afiliación.</b> STATGOAT no está afiliado ni respaldado por la NBA, la NBPA, Basketball-Reference ni FiveThirtyEight.',
  lg_war:'<b>Sin garantía.</b> Esto es un análisis histórico bajo una ponderación concreta. No es una predicción, ni una recomendación de apuestas, ni una verdad establecida.',
  blocks:{PROD:'Producción',EFIC:'Eficiencia',IMPACTO:'Impacto',DEF:'Defensa',PLAYOFFS:'Playoffs',TITULOS:'Títulos',PREMIOS:'Premios'},
  tips:{PROD:'Pts, reb, as, robos y tapones por partido en z-score de su temporada',
    EFIC:'True Shooting relativo a la liga y control de pérdidas',
    IMPACTO:'PER, Win Shares por 48 y Box Plus/Minus',
    DEF:'DBPM, DWS/48, %robo, %tapón, %rebote defensivo, All-Defensivo y DPOY',
    PLAYOFFS:'Anotación de playoffs ajustada a la época, diferencia vs. su liga regular y RAPTOR de postemporada',
    TITULOS:'Anillos ponderados por rol real y Finals MVP',
    PREMIOS:'Votos al MVP, All-NBA por nivel y All-Star'},
  presets:{base:'Base',imp:'Solo impacto',notit:'Sin títulos',po2:'Playoffs ×2',def2:'Defensa ×2',reg:'Solo temp. regular',hon:'Solo palmarés'},
  filters:{all:'Todos',g400:'≥ 400 partidos',ring:'Con anillo',mvp:'Con MVP',pre80:'Antes de 1980',active:'En activo'},
  noWeights:'sin pesos', normalized:'normalizado a 100%',
  movers:n=>`${n} cambios de 3+ puestos en el top 25`, baseOrder:'orden base',
  count:(a,b)=>`${a} de ${b} jugadores`,
  more:n=>`Ver más jugadores (${n} restantes)`,
  record:'RÉCORD', partial:'DATOS PARCIALES', seasonsShort:'temp.',
  card:{career:'CARRERA',active:'ACTIVO',seasons:'temporadas',games:'PARTIDOS',minutes:'MINUTOS',perGame:'partido',
    teams:'EQUIPOS',league:'LIGA',pg:'POR PARTIDO',pts:'PUNTOS',reb:'REBOTES',ast:'ASISTENCIAS',stl:'ROBOS',blk:'TAPONES',tov:'PÉRDIDAS',
    poPts:'PTS PLAYOFFS',vsReg:'vs. liga regular',poEst:'fuera del top 250 anotador; estimado con su liga regular',
    effImp:'EFICIENCIA E IMPACTO',perAvg:'media liga 15,0',wsAvg:'media 0,100',off:'of.',def:'def.',
    pct:'PORCENTAJES EN PISTA',stlP:'ROBO %',blkP:'TAPÓN %',drbP:'REB. DEF. %',orbP:'REB. OF. %',astP:'ASIST. %',
    totals:'TOTALES DE CARRERA',honors:'PALMARÉS',rings:'ANILLOS',asBest:'como mejor de su equipo',
    mvpShare:'en cuota de votos acumulada',anbaScale:'1º=5 · 2º=3 · 3º=1,5',adefScale:'1º=3 · 2º=1,5',
    strength:'FUERZA POR BLOQUE',
    strengthNote:n=>`Desviaciones típicas sobre la media de los ${n} jugadores medibles. 0 = jugador medio del grupo · +2 = mejor que el 97,7%.`,
    partialNote:'<b>Datos parciales:</b> su época no registraba parte de las métricas del modelo, así que estos bloques descansan sobre menos indicadores.',
    best3:'SUS TRES MEJORES TEMPORADAS',cols:['AÑO','EQUIPO','PTS','REB','AST','PER','WS/48','BPM'],
    best3Note:'Ordenadas por un compuesto de producción, eficiencia, impacto y defensa medido en z-score de su propio año, no por puntos.'},
  footer:(s,d)=>`Datos hasta la temporada ${s}. Última actualización: ${d}.`,
  gloss:n=>`<h2>Qué es exactamente cada cosa</h2>
<p class="lead">Los colores son los mismos en los cuadraditos de los pesos y en la barra de cada jugador, así que la barra se lee directamente como el reparto de su puntuación.</p>
<h3>LOS SIETE BLOQUES</h3><dl class="gl">${glossBlocks('en la ponderación base')}</dl>
<h3>LAS MÉTRICAS QUE HAY DENTRO</h3><dl class="gl">
<dt>z-score</dt><dd>Cuántas desviaciones típicas por encima o por debajo está el jugador respecto a la media de los jugadores cualificados <b>de esa misma temporada</b>. 0 es un jugador medio de su año; +2 significa mejor que el 97,7% de sus contemporáneos. Es el mecanismo que permite comparar 1962 con ${SMAX}. Se recorta a ±4.</dd>
<dt>PER</dt><dd>Player Efficiency Rating. Resume toda la producción de caja por minuto en un número, ajustado al ritmo y calibrado para que la media de la liga sea siempre 15. No ve defensa más allá de robos y tapones.</dd>
<dt>TS%</dt><dd>True Shooting. Porcentaje de acierto que pone triples, dobles y tiros libres en la misma escala: <code>PTS / (2 × (TCI + 0,44 × TLI))</code>.</dd>
<dt>USG%</dt><dd>Porcentaje de las jugadas de su equipo que termina el jugador (tiro, falta recibida o pérdida) mientras está en pista. Mide cuánto ataque le pasa por las manos, no lo bien que lo resuelve.</dd>
<dt>TOV%</dt><dd>Pérdidas por cada 100 jugadas usadas. Entra en el índice con signo negativo: menos es mejor.</dd>
<dt>WS y WS/48</dt><dd>Win Shares. Reparte las victorias reales del equipo entre sus jugadores según su producción ofensiva y defensiva. WS/48 lo pasa a ritmo por 48 minutos para que no premie solo a quien juega más. La media de la liga ronda 0,100.</dd>
<dt>BPM</dt><dd>Box Plus/Minus. Puntos aportados por cada 100 posesiones por encima de un jugador medio, estimado desde el box score y corregido por el rendimiento real del equipo. 0 es medio, +5 nivel All-NBA, +10 una temporada histórica. <b>Solo desde 1974.</b></dd>
<dt>OBPM y DBPM</dt><dd>La descomposición ofensiva y defensiva del BPM. DBPM es el componente con más peso del bloque de Defensa.</dd>
<dt>VORP</dt><dd>Value Over Replacement Player. El BPM traducido a valor acumulado sobre un jugador de reemplazo (−2,0) y prorrateado a 82 partidos.</dd>
<dt>ROBO %, TAPÓN %, REB %</dt><dd>Porcentaje de posesiones rivales que termina robando, de tiros de dos rivales que tapona y de rebotes disponibles que captura, siempre mientras está en pista. Al ser porcentajes, no premian jugar más minutos.</dd>
<dt>ASIST. %</dt><dd>Porcentaje de canastas de compañeros que asiste mientras está en pista.</dd>
<dt>RAPTOR</dt><dd>Métrica de FiveThirtyEight que combina box score con más/menos por quinteto. Aquí solo se usa su versión de postemporada: victorias sobre reemplazo en playoffs por temporada disputada. Existe entre 1977 y 2022.</dd>
</dl>
<h3>LO QUE CALCULA ESTE ÍNDICE Y NO VIENE DE NINGUNA FUENTE</h3><dl class="gl">
<dt>Puntuación</dt><dd>Suma de los siete bloques por sus pesos, reescalada de 0 a 97 dentro del grupo, más el bonus por totales. El primero marca 100. Es una escala relativa: dice quién está por delante y por cuánto, no un valor absoluto.</dd>
<dt>Carrera</dt><dd>Cada bloque se resume como <code>40% media de las 3 mejores temporadas + 40% media de las 7 mejores + 20% acumulado</code>. Prioriza el rendimiento por partido: nadie sube por acumular temporadas mediocres. Solo cuentan las temporadas de 1.000+ minutos.</dd>
<dt>Crédito de anillo</dt><dd>Un anillo no vale igual para todos. El crédito es proporcional a los minutos por partido de ese jugador esa temporada, con tope en 30, y lleva un recargo de 1,6× si fue el jugador con más Win Shares de la plantilla campeona. Sin esto, un suplente con seis anillos superaría a Jerry West.</dd>
<dt>Bonus por totales</dt><dd>Hasta 3 puntos fuera de la ponderación para quien esté por encima del percentil 95 histórico en puntos, rebotes, asistencias, robos o tapones de carrera. Es la única vía por la que los acumulados entran en el índice.</dd>
<dt>Compresión de colas</dt><dd>Por encima de 2 desviaciones los bloques se comprimen logarítmicamente. Sin esto, los 11 anillos de Russell y los 6 Finals MVP de Jordan generaban valores de +11 y el bloque de Títulos se comía el peso nominal de los otros seis.</dd>
<dt>Datos parciales</dt><dd>Marca a los jugadores cuya época no registraba parte de las métricas. Se les puntúa solo con lo disponible, renormalizando los pesos presentes.</dd>
<dt>Estimado en playoffs</dt><dd>Los jugadores fuera del top 250 anotador de playoffs no tienen dato publicado. Se les estima con su anotación de liga regular. Imputarles el mínimo hundiría injustamente a especialistas defensivos.</dd>
<dt>Quién entra</dt><dd>Los ${n} jugadores con al menos una temporada de 1.000+ minutos. Por debajo de eso el modelo no tiene nada que medir.</dd>
</dl>`
},
en:{
  locale:'en-US', dec:'.',
  title:`STATGOAT · all-time NBA player index 1947–${SMAX}`,
  sub:'A composite index of BAA, NBA and ABA players. No stat is compared raw across eras: everything is converted into standard deviations within its own season. <b>The order isn’t set by the data. It’s set by the weights.</b>',
  st_players:'PLAYERS', st_years:'SEASONS', st_ps:'PLAYER-SEASONS', st_blocks:'ADJUSTABLE BLOCKS', st_sources:'DATA SOURCES',
  info_h:'What data existed in each era',
  info_sub:'Each player is scored only on what his era recorded, re-weighting the blocks that exist. Nobody is punished with zeros, but some players’ blocks rest on fewer indicators.',
  e1m:'Pts · Reb · Ast · FG · FT', e1n:'Basic box score only',
  e2m:'+ Minutes · PER · WS/48', e2n:'First derived metrics',
  e3m:'+ Turnovers · USG% · TOV%', e3n:'Ball security tracked',
  e4m:'+ Blocks · Steals', e4n:'Defense starts being measured',
  e5m:'+ BPM · VORP · DBPM', e5n:'Per-possession impact estimates',
  e6m:'+ Three-pointer', e6n:'Transition to the modern game',
  e7m:'+ On/Off · Play-by-play', e7n:'Lineup plus/minus',
  e8y:'2013–today', e8m:'+ Optical tracking', e8n:'Player and ball position',
  c_weights:'WEIGHTS', c_live:'WITH THESE WEIGHTS',
  bonus:'Add a bonus for extraordinary career totals (max. 3 pts)',
  search:'Search player…', th_player:'Player', th_bar:'Where the score comes from', th_score:'Score',
  cr_h:'Sources and attribution',
  cr_br:`Full box score, advanced metrics, award voting, All-NBA, All-Defensive and All-Star selections. 1947–${SMAX}, regular season. Career playoff scoring from the public leaderboard.`,
  cr_538:'Historical and modern RAPTOR: offensive and defensive impact combining box score with lineup plus/minus. Coverage 1977–2022.',
  cr_nba:'Champions by season and Finals MVPs 1947–2026, independently verified for the 2023 to 2026 seasons.',
  cr_sg_h:'STATGOAT index',
  cr_sg1:'The transformation is our own: within-season z-scores, logarithmic tail compression, rings weighted by actual role and the composition of the seven blocks.',
  cr_sg2:'The weighting is a formalized opinion, which is why you can change it above.',
  lg_attr:'<b>Attribution.</b> The original data keeps its source licenses. If you reuse this index, credit Basketball-Reference, FiveThirtyEight and NBA.com.',
  lg_aff:'<b>No affiliation.</b> STATGOAT is not affiliated with or endorsed by the NBA, the NBPA, Basketball-Reference or FiveThirtyEight.',
  lg_war:'<b>No warranty.</b> This is a historical analysis under one specific weighting. It is not a prediction, betting advice or settled truth.',
  blocks:{PROD:'Production',EFIC:'Efficiency',IMPACTO:'Impact',DEF:'Defense',PLAYOFFS:'Playoffs',TITULOS:'Titles',PREMIOS:'Awards'},
  tips:{PROD:'Points, rebounds, assists, steals and blocks per game, as a z-score within their season',
    EFIC:'True Shooting relative to the league, plus ball security',
    IMPACTO:'PER, Win Shares per 48 and Box Plus/Minus',
    DEF:'DBPM, DWS/48, steal %, block %, defensive rebound %, All-Defensive teams and DPOY votes',
    PLAYOFFS:'Era-adjusted playoff scoring, the gap vs. his regular season, and postseason RAPTOR',
    TITULOS:'Rings weighted by the player’s actual role, plus Finals MVPs',
    PREMIOS:'MVP votes, All-NBA selections by tier and All-Star nods'},
  presets:{base:'Default',imp:'Impact only',notit:'No titles',po2:'Playoffs ×2',def2:'Defense ×2',reg:'Regular season only',hon:'Honors only'},
  filters:{all:'All',g400:'≥ 400 games',ring:'Champions',mvp:'MVP winners',pre80:'Before 1980',active:'Active'},
  noWeights:'no weights', normalized:'normalized to 100%',
  movers:n=>`${n} moves of 3+ spots in the top 25`, baseOrder:'default order',
  count:(a,b)=>`${a} of ${b} players`,
  more:n=>`Show more players (${n} left)`,
  record:'RECORD', partial:'PARTIAL DATA', seasonsShort:'seasons',
  card:{career:'CAREER',active:'ACTIVE',seasons:'seasons',games:'GAMES',minutes:'MINUTES',perGame:'game',
    teams:'TEAMS',league:'LEAGUE',pg:'PER GAME',pts:'POINTS',reb:'REBOUNDS',ast:'ASSISTS',stl:'STEALS',blk:'BLOCKS',tov:'TURNOVERS',
    poPts:'PLAYOFF PTS',vsReg:'vs. regular season',poEst:'outside the top-250 playoff scorers; estimated from his regular season',
    effImp:'EFFICIENCY & IMPACT',perAvg:'league avg 15.0',wsAvg:'avg 0.100',off:'off.',def:'def.',
    pct:'ON-COURT PERCENTAGES',stlP:'STEAL %',blkP:'BLOCK %',drbP:'DEF. REB. %',orbP:'OFF. REB. %',astP:'ASSIST %',
    totals:'CAREER TOTALS',honors:'HONORS',rings:'RINGS',asBest:'as his team’s best player',
    mvpShare:'cumulative vote share',anbaScale:'1st=5 · 2nd=3 · 3rd=1.5',adefScale:'1st=3 · 2nd=1.5',
    strength:'STRENGTH BY BLOCK',
    strengthNote:n=>`Standard deviations above the average of the ${n} measurable players. 0 = average player in the group · +2 = better than 97.7%.`,
    partialNote:'<b>Partial data:</b> his era didn’t record some of the model’s metrics, so these blocks rest on fewer indicators.',
    best3:'HIS THREE BEST SEASONS',cols:['YEAR','TEAM','PTS','REB','AST','PER','WS/48','BPM'],
    best3Note:'Ranked by a composite of production, efficiency, impact and defense measured as a z-score within his own year, not by points.'},
  footer:(s,d)=>`Data through the ${s} season. Last updated: ${d}.`,
  gloss:n=>`<h2>What everything means</h2>
<p class="lead">The colors match the little squares next to the weights and each player’s bar, so the bar reads directly as the breakdown of his score.</p>
<h3>THE SEVEN BLOCKS</h3><dl class="gl">${glossBlocks('in the default weighting')}</dl>
<h3>THE METRICS INSIDE</h3><dl class="gl">
<dt>z-score</dt><dd>How many standard deviations above or below the average of qualified players <b>from that same season</b> a player is. 0 is an average player of his year; +2 means better than 97.7% of his peers. This is what makes 1962 comparable with ${SMAX}. Capped at ±4.</dd>
<dt>PER</dt><dd>Player Efficiency Rating. Sums up all box-score production per minute in one number, pace-adjusted and calibrated so the league average is always 15. It sees no defense beyond steals and blocks.</dd>
<dt>TS%</dt><dd>True Shooting. A shooting percentage that puts threes, twos and free throws on the same scale: <code>PTS / (2 × (FGA + 0.44 × FTA))</code>.</dd>
<dt>USG%</dt><dd>Share of his team’s plays a player finishes (shot, drawn foul or turnover) while on the floor. It measures how much offense runs through him, not how well he finishes it.</dd>
<dt>TOV%</dt><dd>Turnovers per 100 plays used. It enters the index with a negative sign: lower is better.</dd>
<dt>WS and WS/48</dt><dd>Win Shares. Splits the team’s actual wins among its players according to their offensive and defensive output. WS/48 turns it into a per-48-minute rate so it doesn’t just reward whoever plays the most. The league average is around 0.100.</dd>
<dt>BPM</dt><dd>Box Plus/Minus. Points contributed per 100 possessions above an average player, estimated from the box score and adjusted to the team’s real performance. 0 is average, +5 is All-NBA level, +10 is a historic season. <b>Only since 1974.</b></dd>
<dt>OBPM and DBPM</dt><dd>The offensive and defensive split of BPM. DBPM is the heaviest component of the Defense block.</dd>
<dt>VORP</dt><dd>Value Over Replacement Player. BPM turned into cumulative value over a replacement-level player (−2.0), prorated to 82 games.</dd>
<dt>STEAL %, BLOCK %, REB %</dt><dd>Share of opponent possessions he ends with a steal, of opponent two-point shots he blocks and of available rebounds he grabs, always while on the floor. As percentages, they don’t reward playing more minutes.</dd>
<dt>ASSIST %</dt><dd>Share of teammates’ baskets he assists while on the floor.</dd>
<dt>RAPTOR</dt><dd>A FiveThirtyEight metric combining box score with lineup plus/minus. Only its postseason version is used here: wins above replacement in the playoffs per season played. Available from 1977 to 2022.</dd>
</dl>
<h3>WHAT THIS INDEX CALCULATES ON ITS OWN</h3><dl class="gl">
<dt>Score</dt><dd>The sum of the seven blocks times their weights, rescaled from 0 to 97 within the group, plus the totals bonus. The leader scores 100. It’s a relative scale: it tells you who’s ahead and by how much, not an absolute value.</dd>
<dt>Career</dt><dd>Each block is summarized as <code>40% average of the 3 best seasons + 40% average of the 7 best + 20% cumulative</code>. Per-game performance comes first: nobody climbs by piling up mediocre seasons. Only seasons with 1,000+ minutes count.</dd>
<dt>Ring credit</dt><dd>Not every ring is worth the same. The credit is proportional to the player’s minutes per game that season, capped at 30, with a 1.6× boost if he had the most Win Shares on the championship roster. Without this, a bench player with six rings would outrank Jerry West.</dd>
<dt>Totals bonus</dt><dd>Up to 3 points outside the weighting for anyone above the all-time 95th percentile in career points, rebounds, assists, steals or blocks. It’s the only way career totals enter the index.</dd>
<dt>Tail compression</dt><dd>Above 2 standard deviations the blocks are compressed logarithmically. Without it, Russell’s 11 rings and Jordan’s 6 Finals MVPs produced values of +11 and the Titles block swallowed the nominal weight of the other six.</dd>
<dt>Partial data</dt><dd>Flags players whose era didn’t record some of the metrics. They’re scored only on what exists, re-weighting the blocks that are available.</dd>
<dt>Estimated playoffs</dt><dd>Players outside the top 250 playoff scorers have no published figure. Their playoff scoring is estimated from the regular season. Assigning them the minimum would unfairly sink defensive specialists.</dd>
<dt>Who’s included</dt><dd>The ${n} players with at least one season of 1,000+ minutes. Below that, the model has nothing to measure.</dd>
</dl>`
}};

/* ---------- idioma ---------- */
const LANGS=['es','en'];
function detectLang(){
  try{const q=new URLSearchParams(location.search).get('lang'); if(LANGS.includes(q)) return q;}catch(e){}
  try{const s=localStorage.getItem('statgoat_lang'); if(LANGS.includes(s)) return s;}catch(e){}
  const n=((navigator.languages&&navigator.languages[0])||navigator.language||'en').toLowerCase();
  return /^(es|ca|gl|eu)\b/.test(n)?'es':'en';
}
let LANG=detectLang();
const T=()=>I18N[LANG];
const loc=()=>T().locale;

const BLOCKS=[
 {k:'PROD',c:'var(--w-prod)',d:15},
 {k:'EFIC',c:'var(--w-efic)',d:7},
 {k:'IMPACTO',c:'var(--w-imp)',d:20},
 {k:'DEF',c:'var(--w-def)',d:13},
 {k:'PLAYOFFS',c:'var(--w-po)',d:20},
 {k:'TITULOS',c:'var(--w-tit)',d:15},
 {k:'PREMIOS',c:'var(--w-pre)',d:10}
];
const bn=k=>T().blocks[k];
const PRESETS={
 base:{PROD:15,EFIC:7,IMPACTO:20,DEF:13,PLAYOFFS:20,TITULOS:15,PREMIOS:10},
 imp:{PROD:0,EFIC:0,IMPACTO:100,DEF:0,PLAYOFFS:0,TITULOS:0,PREMIOS:0},
 notit:{PROD:18,EFIC:8,IMPACTO:24,DEF:15,PLAYOFFS:23,TITULOS:0,PREMIOS:12},
 po2:{PROD:12,EFIC:5,IMPACTO:16,DEF:10,PLAYOFFS:40,TITULOS:11,PREMIOS:6},
 def2:{PROD:12,EFIC:5,IMPACTO:16,DEF:26,PLAYOFFS:17,TITULOS:14,PREMIOS:10},
 reg:{PROD:30,EFIC:15,IMPACTO:35,DEF:20,PLAYOFFS:0,TITULOS:0,PREMIOS:0},
 hon:{PROD:0,EFIC:0,IMPACTO:0,DEF:0,PLAYOFFS:0,TITULOS:60,PREMIOS:40}
};
const FILTERS={
 all:()=>true,
 g400:p=>get(p,'g')>=400,
 ring:p=>get(p,'ring')>0,
 mvp:p=>get(p,'mvp')>0,
 pre80:p=>get(p,'y1')<1980,
 active:p=>get(p,'y1')>=MAXY
};

const $=s=>document.querySelector(s);
const CHUNK=60;
let W={...PRESETS.base}, useBonus=true, openRk=null, shown=CHUNK,
    query='', filter='all', baseRank={}, scored=[], view=[];

const nf=(v,d=1)=>v==null?'—':Number(v).toFixed(d);
const mil=v=>v==null?'—':Number(v).toLocaleString(loc());
const pc=v=>v==null?'—':(Number(v)*100).toFixed(1)+'%';
const norm=s=>s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
const NAMES=P.map(p=>norm(get(p,'n')));
const MINS={}; BLOCKS.forEach(b=>MINS[b.k]=Math.min(...P.map(p=>get(p,b.k))));

function glossBlocks(baseTxt){
  return BLOCKS.map(b=>`<dt><span class="dot" style="background:${b.c}"></span>${bn(b.k)}</dt><dd>${T().tips[b.k]}.<em>${b.d}% ${baseTxt}</em></dd>`).join('');
}

/* ---------- cálculo ---------- */
function score(){
  const tot=BLOCKS.reduce((s,b)=>s+W[b.k],0)||1;
  const out=P.map((p,i)=>({i,p,v:BLOCKS.reduce((s,b)=>s+(W[b.k]/tot)*get(p,b.k),0)}));
  let lo=Infinity,hi=-Infinity;
  for(const o of out){if(o.v<lo)lo=o.v;if(o.v>hi)hi=o.v;}
  for(const o of out) o.s=97*(o.v-lo)/((hi-lo)||1)+(useBonus?get(o.p,'bt'):0);
  out.sort((a,b)=>b.s-a.s);
  out.forEach((o,k)=>o.rk=k+1);
  return out;
}
function applyView(){
  const f=FILTERS[filter], q=norm(query.trim());
  view=scored.filter(o=>f(o.p)&&(!q||NAMES[o.i].includes(q)));
}

/* ---------- textos fijos de la página ---------- */
function applyStatic(){
  const t=T();
  document.documentElement.lang=LANG;
  document.title=t.title;
  document.querySelectorAll('[data-i18n]').forEach(el=>{const v=t[el.dataset.i18n]; if(typeof v==='string') el.innerHTML=v;});
  document.querySelectorAll('[data-i18n-ph]').forEach(el=>{el.placeholder=t[el.dataset.i18nPh];});
  document.querySelectorAll('.lang button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.lang===LANG));
  $('#n_players').textContent=P.length.toLocaleString(loc(),{useGrouping:true});
  $('#n_years').textContent=`1947–${SMAX}`;
  if(BI.player_seasons) $('#n_ps').textContent=Number(BI.player_seasons).toLocaleString(loc(),{useGrouping:true});
  else $('#ps_cell').hidden=true;
  let d=BI.built||'';
  if(BI.built_iso){
    try{d=new Date(BI.built_iso+'T12:00:00Z').toLocaleDateString(loc(),{year:'numeric',month:'long',day:'numeric'});}catch(e){}
  }
  $('#ts').textContent=t.footer(seasonLabel(SMAX),d);
  $('#glosario').innerHTML=t.gloss(P.length.toLocaleString(loc(),{useGrouping:true}));
}

/* ---------- controles ---------- */
function buildControls(){
  const t=T();
  $('#sliders').innerHTML=BLOCKS.map(b=>`<div class="sl">
    <label for="s_${b.k}" title="${t.tips[b.k]}"><span class="dot" style="background:${b.c}"></span>${bn(b.k)}</label>
    <input type="range" id="s_${b.k}" min="0" max="60" step="1" value="${W[b.k]}" aria-label="${bn(b.k)}">
    <output id="o_${b.k}"></output></div>`).join('');
  BLOCKS.forEach(b=>$('#s_'+b.k).addEventListener('input',e=>{W[b.k]=+e.target.value;syncP();recalc();}));

  $('#presets').innerHTML=Object.keys(PRESETS).map(id=>`<button data-p="${id}">${t.presets[id]}</button>`).join('');
  $('#presets').querySelectorAll('button').forEach(btn=>btn.onclick=()=>{
    W={...PRESETS[btn.dataset.p]};
    BLOCKS.forEach(b=>$('#s_'+b.k).value=W[b.k]); syncP(); recalc();});

  $('#filters').innerHTML=Object.keys(FILTERS).map(id=>
    `<button data-f="${id}" aria-pressed="${id===filter}">${t.filters[id]}</button>`).join('');
  $('#filters').querySelectorAll('button').forEach(btn=>btn.onclick=()=>{
    filter=btn.dataset.f;
    $('#filters').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.f===filter));
    shown=CHUNK; applyView(); renderTable();});
  syncP();
}
function bindOnce(){
  $('#q').addEventListener('input',e=>{query=e.target.value;shown=CHUNK;applyView();renderTable();});
  $('#bonus').addEventListener('change',e=>{useBonus=e.target.checked;recalc();});
  $('#more').onclick=()=>{shown+=CHUNK*3;renderTable();};
  document.querySelectorAll('.lang button').forEach(b=>b.onclick=()=>setLang(b.dataset.lang));
}
function syncP(){$('#presets').querySelectorAll('button').forEach(b=>{
  const p=PRESETS[b.dataset.p]; b.setAttribute('aria-pressed',BLOCKS.every(x=>p[x.k]===W[x.k]));});}

function setLang(l){
  if(!LANGS.includes(l)||l===LANG) return;
  LANG=l;
  try{localStorage.setItem('statgoat_lang',l);}catch(e){}
  try{const u=new URL(location.href); u.searchParams.set('lang',l); history.replaceState(null,'',u);}catch(e){}
  applyStatic(); buildControls(); recalc();
}

/* ---------- render ---------- */
function recalc(){scored=score();applyView();renderTop();renderTable();}

function renderTop(){
  const t=T(), tot=BLOCKS.reduce((s,b)=>s+W[b.k],0)||1;
  BLOCKS.forEach(b=>$('#o_'+b.k).textContent=Math.round(100*W[b.k]/tot)+'%');
  $('#wsum').textContent=BLOCKS.reduce((s,b)=>s+W[b.k],0)===0?t.noWeights:t.normalized;
  $('#live').innerHTML=scored.slice(0,8).map(o=>{
    const d=baseRank[get(o.p,'n')]-o.rk;
    const m=d>0?`<span class="delta up">▲${d}</span>`:d<0?`<span class="delta down">▼${-d}</span>`:'';
    return `<div class="lrow" data-go="${o.rk}"><span class="lr num">${o.rk}</span>
      <span class="ln">${get(o.p,'n')}${m}</span><span class="ls num">${o.s.toFixed(1)}</span></div>`;}).join('');
  $('#live').querySelectorAll('.lrow').forEach(el=>el.onclick=()=>{
    const o=scored[+el.dataset.go-1]; query=''; $('#q').value=''; filter='all';
    $('#filters').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.f==='all'));
    openRk=o.rk; shown=Math.max(shown,o.rk+5); applyView(); renderTable();
    document.querySelector('tr.open')?.scrollIntoView({block:'center'});});
  const moved=scored.slice(0,25).filter(o=>Math.abs(baseRank[get(o.p,'n')]-o.rk)>=3).length;
  $('#movers').textContent=moved?t.movers(moved):t.baseOrder;
}

function renderTable(){
  const t=T(), tot=BLOCKS.reduce((s,b)=>s+W[b.k],0)||1;
  const maxS=scored.length?scored[0].s:1;
  const slice=view.slice(0,shown);
  $('#count').textContent=t.count(view.length.toLocaleString(loc()),P.length.toLocaleString(loc()));
  $('#tb').innerHTML=slice.map(o=>{
    const p=o.p, parts=BLOCKS.map(b=>({c:b.c,n:bn(b.k),v:(W[b.k]/tot)*(get(p,b.k)-MINS[b.k])}));
    const sum=parts.reduce((s,x)=>s+x.v,0)||1;
    const bar=`<div class="stack" style="width:${Math.max(4,100*o.s/maxS)}%">`+
      parts.map(x=>`<i style="width:${100*x.v/sum}%;background:${x.c}" title="${x.n}"></i>`).join('')+'</div>';
    const fl=(get(p,'rec')?`<span class="flag">${t.record} ${get(p,'rec')}</span>`:'')+
      (get(p,'cov')<0.75?`<span class="flag warn">${t.partial}</span>`:'');
    const op=openRk===o.rk;
    return `<tr class="main${op?' open':''}" data-rk="${o.rk}">
      <td class="rk num">${o.rk}</td>
      <td class="nm">${get(p,'n')}${fl}<small>${get(p,'y0')}–${get(p,'y1')} · ${get(p,'sea')} ${t.seasonsShort}${get(p,'lg')==='ABA'?' · ABA':''}</small></td>
      <td class="bar">${bar}</td><td class="sc num">${o.s.toFixed(1)}</td></tr>`+(op?detail(p,o):'');
  }).join('');
  $('#tb').querySelectorAll('tr.main').forEach(tr=>tr.onclick=()=>{
    const rk=+tr.dataset.rk; openRk=openRk===rk?null:rk; renderTable();});
  $('#more').hidden=view.length<=shown;
  $('#more').textContent=t.more((view.length-shown).toLocaleString(loc()));
}

/* ---------- ficha completa ---------- */
function detail(p,o){
  const g=k=>get(p,k), c=T().card, n=P.length.toLocaleString(loc());
  const blocks=BLOCKS.map(b=>{
    const v=g(b.k), w=Math.min(50,Math.abs(v)/7*50);
    return `<div class="blk"><span class="bl">${bn(b.k)}</span>
      <span class="bb"><i style="background:${b.c};${v>=0?`left:50%;width:${w}%`:`right:50%;width:${w}%`}"></i></span>
      <span class="bv">${v>=0?'+':''}${v.toFixed(2)}</span></div>`;}).join('');

  const seas=(g('seas')||[]).map(s=>`<tr><td>${s[0]}</td><td>${s[1]}</td><td>${nf(s[2])}</td>
    <td>${nf(s[3])}</td><td>${nf(s[4])}</td><td>${nf(s[5])}</td><td>${s[6]==null?'—':s[6].toFixed(3)}</td>
    <td>${nf(s[7])}</td></tr>`).join('');

  const poTxt = g('poe')
    ? `<dt>PLAYOFFS</dt><dd><small>${c.poEst}</small></dd>`
    : `<dt>${c.poPts}</dt><dd>${nf(g('po'))} <small>(${(g('po')-g('ppg'))>=0?'+':''}${nf(g('po')-g('ppg'))} ${c.vsReg})</small></dd>`;

  return `<tr class="det"><td colspan="4"><div class="dgrid">

    <div class="card"><h4>${c.career}</h4><dl class="kv">
      <dt>${c.active}</dt><dd>${g('y0')}–${g('y1')} · ${g('sea')} ${c.seasons}</dd>
      <dt>${c.games}</dt><dd>${mil(g('g'))}</dd>
      <dt>${c.minutes}</dt><dd>${mil(g('mp'))} <small>(${nf(g('mpg'))}/${c.perGame})</small></dd>
      <dt>${c.teams}</dt><dd>${(g('tm')||[]).join(' · ')||'—'}</dd>
      <dt>${c.league}</dt><dd>${g('lg')}</dd>
    </dl></div>

    <div class="card"><h4>${c.pg}</h4><dl class="kv">
      <dt>${c.pts}</dt><dd>${nf(g('ppg'))}</dd>
      <dt>${c.reb}</dt><dd>${nf(g('rpg'))}</dd>
      <dt>${c.ast}</dt><dd>${nf(g('apg'))}</dd>
      <dt>${c.stl}</dt><dd>${nf(g('spg'))}</dd>
      <dt>${c.blk}</dt><dd>${nf(g('bpg'))}</dd>
      <dt>${c.tov}</dt><dd>${nf(g('topg'))}</dd>
      ${poTxt}
    </dl></div>

    <div class="card"><h4>${c.effImp}</h4><dl class="kv">
      <dt>TS%</dt><dd>${pc(g('ts'))}</dd>
      <dt>USG%</dt><dd>${nf(g('usg'))}%</dd>
      <dt>TOV%</dt><dd>${nf(g('tovp'))}%</dd>
      <dt>PER</dt><dd>${nf(g('per'))} <small>(${c.perAvg})</small></dd>
      <dt>WS</dt><dd>${nf(g('ws'))}</dd>
      <dt>WS/48</dt><dd>${g('ws48')==null?'—':g('ws48').toFixed(3)} <small>(${c.wsAvg})</small></dd>
      <dt>BPM</dt><dd>${nf(g('bpm'))} <small>(${c.off} ${nf(g('obpm'))} · ${c.def} ${nf(g('dbpm'))})</small></dd>
      <dt>VORP</dt><dd>${nf(g('vorp'))}</dd>
    </dl></div>

    <div class="card"><h4>${c.pct}</h4><dl class="kv">
      <dt>${c.stlP}</dt><dd>${nf(g('stlp'))}%</dd>
      <dt>${c.blkP}</dt><dd>${nf(g('blkp'))}%</dd>
      <dt>${c.drbP}</dt><dd>${nf(g('drbp'))}%</dd>
      <dt>${c.orbP}</dt><dd>${nf(g('orbp'))}%</dd>
      <dt>${c.astP}</dt><dd>${nf(g('astp'))}%</dd>
    </dl>
    <h4 style="margin-top:14px">${c.totals}</h4><dl class="kv">
      <dt>${c.pts}</dt><dd>${mil(g('tpts'))}</dd>
      <dt>${c.reb}</dt><dd>${mil(g('trb'))}</dd>
      <dt>${c.ast}</dt><dd>${mil(g('tast'))}</dd>
      <dt>${c.stl}</dt><dd>${mil(g('tstl'))}</dd>
      <dt>${c.blk}</dt><dd>${mil(g('tblk'))}</dd>
    </dl></div>

    <div class="card"><h4>${c.honors}</h4><dl class="kv">
      <dt>${c.rings}</dt><dd>${g('ring')}${g('best')?` <small>(${g('best')} ${c.asBest})</small>`:''}</dd>
      <dt>FINALS MVP</dt><dd>${g('fmvp')}</dd>
      <dt>MVP</dt><dd>${g('mvp')} <small>(${nf(g('mvps_v'),2)} ${c.mvpShare})</small></dd>
      <dt>DPOY</dt><dd>${g('dpoy')}</dd>
      <dt>ALL-NBA</dt><dd>${nf(g('anba'))} pts <small>(${c.anbaScale})</small></dd>
      <dt>ALL-DEF.</dt><dd>${nf(g('adef'))} pts <small>(${c.adefScale})</small></dd>
      <dt>ALL-STAR</dt><dd>${g('ast')}</dd>
    </dl></div>

    <div class="card"><h4>${c.strength}</h4>${blocks}
      <p class="pnote">${c.strengthNote(n)}
      ${g('cov')<0.75?'<br>'+c.partialNote:''}</p>
    </div>

    <div class="card" style="grid-column:1/-1"><h4>${c.best3}</h4>
      <table class="seas"><thead><tr>${c.cols.map(x=>`<th>${x}</th>`).join('')}</tr></thead>
      <tbody>${seas||'<tr><td colspan="8">—</td></tr>'}</tbody></table>
      <p class="pnote">${c.best3Note}</p>
    </div>

  </div></td></tr>`;
}

/* ---------- arranque ---------- */
bindOnce();
applyStatic();
buildControls();
scored=score(); scored.forEach(o=>baseRank[get(o.p,'n')]=o.rk);
syncP(); recalc();
