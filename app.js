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
  st_players:'JUGADORES', st_years:'TEMPORADAS', st_ps:'TEMPORADAS INDIVIDUALES', st_blocks:'BLOQUES PONDERABLES', st_po:'TEMPORADAS DE PLAYOFFS',
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
  bonus:'Sumar bonus por estar en el top 5 histórico de una estadística (máx. 3 pts)',
  search:'Buscar jugador…', th_player:'Jugador', th_bar:'De dónde sale la puntuación', th_score:'Punt.',
  tab_players:'Jugadores', tab_seasons:'Mejores temporadas', th_season:'Temporada',
  sfilters:{all:'Todas',ring:'Con anillo',noring:'Sin anillo',mvp:'Con MVP',pre80:'Antes de 1980',from2000:'Desde 2000'},
  pos:{all:'Todas las posiciones',PG:'Bases',SG:'Escoltas',SF:'Aleros',PF:'Ala-pívots',C:'Pívots'},
  posOne:{PG:'Base',SG:'Escolta',SF:'Alero',PF:'Ala-pívot',C:'Pívot'},posLab:'POSICIÓN',
  share:'Copiar enlace a esta vista',
  howto:'Cómo funciona',
  wl_h:'Bienvenido a STATGOAT',
  wl_1:'Un índice de los mejores jugadores de la historia de la NBA, la ABA y la BAA. Cada estadística se mide contra los rivales de su propia temporada, así que se pueden comparar épocas distintas.',
  wl_2:'El orden lo deciden los pesos: cuánto vale cada bloque (producción, defensa, títulos…). Los datos son los mismos para todos; los pesos los eliges tú.',
  wl_3:'¿Te sorprende ver a tu jugador favorito más abajo de lo que esperabas? Prueba a bajar Defensa y subir Producción o Premios, y mira cómo cambia el ranking.',
  wl_btn:'Empezar',copied:'Enlace copiado ✓',margin:'MARGEN DE PUESTO',
  marginNote:'con pesos parecidos a los de base',top1:n=>`n.º 1 en el ${n} % de las ponderaciones`,
  scount:(a,b)=>`${a} de ${b} temporadas`, smore:n=>`Ver más temporadas (${n} restantes)`,
  tag:{mvp:'MVP',dpoy:'DPOY',ring:'Anillo',fmvp:'MVP Finales'},
  sd:{rs:'LIGA REGULAR',po:'PLAYOFFS',aw:'PREMIOS',none:'No jugó playoffs ese año.',games:'PARTIDOS',ppg:'PUNTOS',mvpv:'de los votos',anba:'ALL-NBA',as:'ALL-STAR',ring:'ANILLO',fmvp:'MVP FINALES',yes:'Sí',no:'No',
      note:n=>`Desviaciones típicas frente a las ${n} temporadas medibles desde 1951-52, con los pesos que tengas puestos.`},
  cr_h:'Fuentes y atribución',
  cr_br_h:'Basketball-Reference · temporada regular',
  cr_br:`Box score completo, métricas avanzadas, votaciones de premios, All-NBA, All-Defensivo y All-Star, 1947–${SMAX}, a través del volcado público de Sumitro Datta. La liga regular de la temporada en curso se lee directamente de Basketball-Reference cada lunes.`,
  cr_po_h:'Basketball-Reference · playoffs y premios',
  cr_po:`Estadísticas de playoffs de cada temporada (totales y avanzadas), campeones, Finals MVP y las votaciones de premios más recientes, descargadas directamente cada lunes. Playoffs hasta ${BI.playoff_max||'—'}.`,
  cr_sg_h:'Índice STATGOAT',
  cr_sg1:'La transformación es propia: z-scores intra-temporada, compresión logarítmica de colas, anillos según la aportación real en cada playoff y composición de los siete bloques.',
  cr_sg2:'La ponderación es una opinión formalizada, y por eso se puede cambiar arriba.',
  lg_attr:'<b>Atribución.</b> Los datos originales conservan sus licencias de origen. Si reutilizas este índice, cita Basketball-Reference.',
  lg_aff:'<b>Sin afiliación.</b> STATGOAT no está afiliado ni respaldado por la NBA, la NBPA ni Basketball-Reference.',
  lg_war:'<b>Sin garantía.</b> Esto es un análisis histórico bajo una ponderación concreta. No es una predicción, ni una recomendación de apuestas, ni una verdad establecida.',
  blocks:{PROD:'Producción',EFIC:'Eficiencia',IMPACTO:'Impacto',DEF:'Defensa',PLAYOFFS:'Playoffs',TITULOS:'Títulos',PREMIOS:'Premios'},
  tips:{PROD:'Pts, reb, as, robos y tapones por partido en z-score de su temporada',
    EFIC:'Puntos añadidos por anotar por encima del TS% de su liga (eficiencia × volumen) y control de pérdidas',
    IMPACTO:'PER, Win Shares por 48 y Box Plus/Minus',
    DEF:'DBPM, DWS/48, %robo, %tapón, %rebote defensivo, All-Defensivo y DPOY',
    PLAYOFFS:'Nivel en sus mejores 4.000 minutos de playoffs frente a los demás jugadores de esos playoffs, y aportación acumulada',
    TITULOS:'Anillos según la aportación real en cada carrera al título, y Finals MVP',
    PREMIOS:'Votos al MVP, All-NBA por nivel y All-Star'},
  presets:{base:'Base',imp:'Solo impacto',notit:'Sin títulos',po2:'Playoffs ×2',def2:'Defensa ×2',reg:'Solo temp. regular',hon:'Solo palmarés'},
  filters:{all:'Todos',g400:'≥ 400 partidos',ring:'Con anillo',noring:'Sin anillo',mvp:'Con MVP',pre80:'Antes de 1980',active:'En activo'},
  noWeights:'sin pesos', normalized:'normalizado a 100%',
  movers:n=>`${n} cambios de 3+ puestos en el top 25`,smovers:n=>`${n} temporadas del top 25 se mueven 3+ puestos`, baseOrder:'orden base', overall:'general',
  count:(a,b)=>`${a} de ${b} jugadores`,
  more:n=>`Ver más jugadores (${n} restantes)`,
  record:'RÉCORD', partial:'DATOS PARCIALES', seasonsShort:'temp.',
  card:{career:'CARRERA',active:'ACTIVO',seasons:'temporadas',games:'PARTIDOS',minutes:'MINUTOS',perGame:'partido',
    teams:'EQUIPOS',league:'LIGA',pg:'POR PARTIDO',pts:'PUNTOS',reb:'REBOTES',ast:'ASISTENCIAS',stl:'ROBOS',blk:'TAPONES',tov:'PÉRDIDAS',tpm:'TRIPLES',top5:'TOP 5 HISTÓRICO',withBonus:'con el bonus',
    cat:{pts:'puntos',trb:'rebotes',ast:'asistencias',stl:'robos',blk:'tapones',x3p:'triples'},
    po:'PLAYOFFS',poNone:'Nunca jugó playoffs.',poRuns:'temporadas',vsReg:'vs. liga regular',poPlus:'PLUS',plusUp:'crece en playoffs',plusDown:'baja en playoffs',plusEq:'rinde igual',
    effImp:'EFICIENCIA E IMPACTO',perAvg:'media liga 15,0',wsAvg:'media 0,100',off:'of.',def:'def.',
    pct:'PORCENTAJES EN PISTA',stlP:'ROBO %',blkP:'TAPÓN %',drbP:'REB. DEF. %',orbP:'REB. OF. %',astP:'ASIST. %',
    totals:'TOTALES DE CARRERA',honors:'PALMARÉS',rings:'ANILLOS',asBest:'como mejor de su equipo',
    mvpShare:'en cuota de votos acumulada',anbaScale:'1º=5 · 2º=3 · 3º=1,5',adefScale:'1º=3 · 2º=1,5',
  dx:{title:'DE DÓNDE SALE LA NOTA',hint:'Toca un bloque para ver de dónde sale. A la derecha, los puntos que aporta con tus pesos.',
    base:'Punto de partida (todos los bloques en 0, la media del índice)',bonus:'Bonus por totales',total:'Nota con tus pesos',
    rankIn:(r,n)=>`n.º ${r} de ${n} en este bloque`,loading:'Cargando…',fail:'No se ha podido cargar el detalle.',
    career:(pk,pr,su,ca)=>`Carrera = 40 % media de sus 3 mejores temporadas (${pk}) + 40 % media de sus 7 mejores (${pr}) + 20 % acumulado, llevado a la misma escala (${su}) = ${ca}. Después se pasa a la escala del índice.`,
    seasonsNote:n=>`Sus ${n} temporadas computables (1.000+ minutos; antes de 1952, por partidos), ordenadas por este bloque. Las 3 primeras en negrita. Si tiene menos de 7, las que faltan cuentan como 0.`,
    value:'Valor',season:'Temp.',team:'Equipo',
    cols:{PROD:['PTS','REB','AST','ROB','TAP'],EFIC:['TS%','Pts añad.','Pérd. %'],IMPACTO:['PER','WS/48','BPM'],DEF:['DBPM','DWS/48','Rob. %','Tap. %','Reb. d. %']},
    defRec:(a1,a2,dw,dv)=>`El 25 % del bloque es reconocimiento: All-Defense (${a1} en el primer equipo, ${a2} en el segundo) y votos al DPOY (${dw} ${dw===1?'ganado':'ganados'}${dv?', votado '+dv+' años':''}). El 75 %, estas estadísticas.`,
    poSum:(q,pr,fin,wp,ws)=>`Nivel en sus mejores ${wp} minutos de playoffs: ${q}. Previsión por su liga regular: ${pr}. Nivel que cuenta, más cerca del real cuanto más jugó: ${fin} (80 % del bloque). Win Shares acumuladas en playoffs: ${ws} (20 %).`,
    poCols:['Año','Equipo','PJ','MIN','PTS','REB','AST','BPM','WS','Nivel'],poMark:'En negrita, las eliminatorias que entran en sus mejores 4.000 minutos.',
    poNone:'No jugó playoffs: cuenta la previsión por su liga regular.',more:n=>`y ${n} más`,
    rCols:['Año','Equipo','% WS del equipo','Valor del anillo'],rSum:(n,c,f)=>`${n} ${n===1?'anillo':'anillos'}, que suman ${c}. MVP de las Finales: ${f}. (70 % anillos, 30 % MVP de las Finales.)`,
    rNone:'Sin anillos.',rNote:'Cada anillo vale según su parte de las Win Shares de su equipo en esos playoffs: el mejor jugador típico de un campeón vale 1,6; en la plantilla sin jugar esos playoffs, 0,05.',
    noShare:'sin jugar',fmvpLoss:y=>`MVP de las Finales sin anillo: ${y}.`,best:'mejor del equipo',
    aCols:['Año','MVP','All-NBA','All-Star'],aSum:(m,a,s)=>`Votos al MVP: ${m} (45 %) · All-NBA: ${a} (35 %) · All-Star: ${s} (20 %)`,
    aNone:'Sin premios individuales.',mvpWin:'MVP',tier:['','1.er equipo','2.º equipo','3.er equipo'],place:r=>`${r}.º`},
    strength:'FUERZA POR BLOQUE',
    strengthNote:n=>`Desviaciones típicas sobre la media de los ${n} jugadores medibles. 0 = jugador medio del grupo · +2 = mejor que el 97,7%.`,
    partialNote:'<b>Datos parciales:</b> su época no registraba parte de las métricas del modelo, así que estos bloques descansan sobre menos indicadores.',
    best3:'SUS TRES MEJORES TEMPORADAS',cols:['AÑO','EQUIPO','PTS','REB','AST','PER','WS/48','BPM'],
    best3Note:'Ordenadas por un compuesto de producción, eficiencia, impacto y defensa medido en z-score de su propio año, no por puntos.'},
  footer:(s,d)=>`Datos hasta la temporada ${s}, playoffs hasta ${BI.playoff_max||'—'}. Se actualiza cada lunes; última vez: ${d}.`,
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
</dl>
<h3>LO QUE CALCULA ESTE ÍNDICE Y NO VIENE DE NINGUNA FUENTE</h3><dl class="gl">
<dt>Puntuación</dt><dd>Suma de los siete bloques por sus pesos, reescalada de 0 a 100 dentro del grupo: el primero marca 100. Si activas el bonus por totales, la escala pasa a 0-97 más hasta 3 puntos de bonus. Es una escala relativa: dice quién está por delante y por cuánto, no un valor absoluto.</dd>
<dt>Carrera</dt><dd>Cada bloque se resume como <code>40% media de las 3 mejores temporadas + 40% media de las 7 mejores + 20% acumulado</code>. Antes de sumarlo, el acumulado se pasa a la misma escala que el pico a partir de su percentil histórico, para que cada porcentaje pese exactamente lo que dice: la longevidad cuenta un 20%, no más. Si un jugador tiene menos de 3 o de 7 temporadas computables, las que le faltan cuentan como 0 (un jugador medio de la liga): tres temporadas buenas no son un prime de siete. Prioriza el rendimiento por partido: nadie sube por acumular temporadas mediocres. Solo cuentan las temporadas de 1.000+ minutos.</dd>
<dt>Puntos añadidos por eficiencia</dt><dd>Base del bloque de Eficiencia, en liga regular y en playoffs: <code>(TS% propio − TS% de su liga) × intentos</code>, o sea, cuántos puntos por partido suma un jugador por anotar mejor que la media de su liga ese año. Mide eficiencia y volumen a la vez: un pívot que tira 5 veces al 65% aporta menos que un anotador que tira 20 al 63%. Se completa con el control de pérdidas (30%).</dd>
<dt>Bloque de Playoffs</dt><dd>Cada temporada de playoffs se mide contra los demás jugadores de esos mismos playoffs: producción, eficiencia (puntos añadidos por eficiencia y pérdidas) e impacto (PER, WS/48 y BPM). La nota combina dos cosas: el nivel en sus mejores 4.000 minutos de playoffs (80%), igual que en liga regular cuentan las mejores temporadas, y las Win Shares acumuladas en playoffs (20%), igual que el acumulado en liga regular.</dd>
<dt>Plus de playoffs</dt><dd>Si un jugador crece o se encoge en playoffs. Cada postemporada se compara con lo que cabía esperar de su propia liga regular de ese mismo año. +0,30 es crecer mucho (Kawhi, Hakeem, LeBron); por debajo de −0,10, baja. Con pocos minutos se acerca a 0. Se muestra en la ficha pero no suma ni resta: el nivel en playoffs ya recoge lo que rindió de verdad, y contar aparte la diferencia con lo esperado restaba nota a quien hacía una gran liga regular y premiaba a quien partía de una floja.</dd>
<dt>Pocos minutos en playoffs</dt><dd>Una sola eliminatoria es una muestra pequeña. Por eso, cuantos menos minutos de playoffs tiene un jugador, más se acerca su nota a lo que predice su carrera en liga regular; con muchos minutos manda lo que hizo de verdad. Quien nunca jugó playoffs se queda en esa previsión de nivel y sin volumen acumulado.</dd>
<dt>Crédito de anillo</dt><dd>Un anillo no vale igual para todos. Cada jugador se lleva la parte de las Win Shares de su equipo en esos playoffs que generó él: el mejor jugador de un campeón suele aportar entre un 20% y un 35%; un suplente, casi nada. Sin esto, un suplente con seis anillos superaría a Jerry West. Quien estaba en la plantilla pero no jugó esos playoffs se lleva un crédito mínimo; quien fue traspasado antes, ninguno.</dd>
<dt>De dónde sale la nota</dt><dd>En la ficha de cada jugador, cada bloque se despliega: las temporadas que cuentan y sus estadísticas, el cálculo de carrera (40 % mejores 3, 40 % mejores 7, 20 % acumulado), sus playoffs eliminatoria a eliminatoria, cada anillo con su valor y los premios año a año. A la derecha de cada bloque, los puntos que aporta a su nota con los pesos que tengas puestos: el punto de partida (todos los bloques en 0) más esos aportes da su nota.</dd>
<dt>Margen de puesto</dt><dd>Entre qué puestos se mueve un jugador si los pesos por defecto cambian un poco. Se sortean 2.000 combinaciones de pesos parecidas a las de base (un peso del 15 % se mueve unos ±5 puntos) y se muestra el rango donde cae su puesto en 8 de cada 10. Si los márgenes de dos jugadores se solapan, quién va delante depende de cómo se pondere, no de los datos: por ejemplo, Jordan es n.º 1 en un 79 % de las combinaciones y LeBron en un 15 %. Se calcula sobre los pesos por defecto, no sobre los que tengas puestos.</dd>
<dt>Compartir</dt><dd>El botón «Copiar enlace a esta vista» copia una dirección con tus pesos, el bonus, la pestaña, los filtros y la ficha abierta: quien la abra verá exactamente lo mismo.</dd>
<dt>Posición</dt><dd>La que más minutos jugó en su carrera según Basketball-Reference (en Mejores temporadas, la de ese año). Muchos cambian con los años: LeBron sale como alero y Duncan como ala-pívot porque es donde más minutos jugaron. Es solo un filtro: no cambia la nota. Con cualquier filtro activo, la lista y el top de la derecha numeran dentro del filtro y muestran al lado el puesto general. Los jugadores de 1947 a 1951 casi no tienen posición registrada y solo aparecen con «Todas las posiciones».</dd>
<dt>Bonus por totales</dt><dd>Opcional y desactivado por defecto. Si lo activas, suma puntos a quien esté en el top 5 histórico de una estadística de carrera: puntos, rebotes, asistencias, robos, tapones o triples (NBA, ABA y BAA juntas). El 1.º se lleva 3 puntos, el 2.º 2,4, el 3.º 1,8, el 4.º 1,2 y el 5.º 0,6. Cuenta solo su mejor categoría: dos terceros puestos no valen lo mismo que un récord. No va en la nota por defecto porque compara totales en bruto entre épocas (los robos y tapones se cuentan desde 1974, los triples desde 1980 y antes las temporadas eran más cortas) y porque la longevidad ya cuenta un 20% en cada bloque. Los puestos se actualizan cada lunes.</dd>
<dt>Mejores temporadas</dt><dd>La misma fórmula del índice aplicada a un solo año: liga regular (producción, eficiencia, impacto y defensa), los playoffs de ese año, el anillo según su aportación y los premios de esa temporada (MVP, DPOY, All-NBA, All-Star). Cada bloque se compara con todas las temporadas medibles y se pondera con los pesos que tengas puestos. Títulos y premios se pasan a la misma escala que la estadística a partir de su percentil: en un solo año casi todo son ceros, y sin esto un anillo pesaba más que la mejor temporada estadística de la historia. Solo entran temporadas desde 1951-52, cuando empiezan los minutos: antes no se pueden medir ni el impacto ni la defensa.</dd>
<dt>Escala de los bloques</dt><dd>Para que cada peso signifique lo que dice, todos los bloques tienen que estar en la misma escala. Los estadísticos ya lo están (z-score, con las colas comprimidas por encima de 2 desviaciones). Títulos y premios no: tres de cada cuatro jugadores tienen 0 y unos pocos se disparan, y en la cima pesaban un 34% de la nota en vez de su 25%. Por eso se pasan a la escala de la estadística a partir de su percentil: tener más anillos que nadie vale lo mismo que ser el mejor de la historia en producción, no el doble. La escala es continua: quien no tiene nada queda en el centro de su grupo y los demás suben desde ahí, así que un anillo testimonial o un solo All-Star valen casi lo mismo que nada, sin saltos de varios puntos.</dd>
<dt>Datos parciales</dt><dd>Marca a los jugadores cuya época no registraba parte de las métricas. Se les puntúa solo con lo disponible, renormalizando los pesos presentes.</dd>
<dt>Quién entra</dt><dd>Los ${n} jugadores con al menos una temporada de 1.000+ minutos. Por debajo de eso el modelo no tiene nada que medir.</dd>
</dl>`
},
en:{
  locale:'en-US', dec:'.',
  title:`STATGOAT · all-time NBA player index 1947–${SMAX}`,
  sub:'A composite index of BAA, NBA and ABA players. No stat is compared raw across eras: everything is converted into standard deviations within its own season. <b>The order isn’t set by the data. It’s set by the weights.</b>',
  st_players:'PLAYERS', st_years:'SEASONS', st_ps:'PLAYER-SEASONS', st_blocks:'ADJUSTABLE BLOCKS', st_po:'PLAYOFF SEASONS',
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
  bonus:'Add a bonus for being in the all-time top 5 of a stat (max. 3 pts)',
  search:'Search player…', th_player:'Player', th_bar:'Where the score comes from', th_score:'Score',
  tab_players:'Players', tab_seasons:'Best seasons', th_season:'Season',
  sfilters:{all:'All',ring:'Title seasons',noring:'No title',mvp:'MVP seasons',pre80:'Before 1980',from2000:'Since 2000'},
  pos:{all:'All positions',PG:'Point guards',SG:'Shooting guards',SF:'Small forwards',PF:'Power forwards',C:'Centers'},
  posOne:{PG:'Point guard',SG:'Shooting guard',SF:'Small forward',PF:'Power forward',C:'Center'},posLab:'POSITION',
  share:'Copy link to this view',
  howto:'How it works',
  wl_h:'Welcome to STATGOAT',
  wl_1:'An index of the best players in NBA, ABA and BAA history. Every stat is measured against the rivals of its own season, so different eras can be compared.',
  wl_2:'The order is set by the weights: how much each block counts (production, defense, titles…). The data is the same for everyone; you choose the weights.',
  wl_3:'Surprised to see your favourite player lower than expected? Try lowering Defense and raising Production or Awards, and watch the ranking change.',
  wl_btn:'Start',copied:'Link copied ✓',margin:'RANK RANGE',
  marginNote:'with weights close to the default',top1:n=>`#1 in ${n}% of weightings`,
  scount:(a,b)=>`${a} of ${b} seasons`, smore:n=>`Show more seasons (${n} left)`,
  tag:{mvp:'MVP',dpoy:'DPOY',ring:'Title',fmvp:'Finals MVP'},
  sd:{rs:'REGULAR SEASON',po:'PLAYOFFS',aw:'AWARDS',none:'No playoffs that year.',games:'GAMES',ppg:'POINTS',mvpv:'vote share',anba:'ALL-NBA',as:'ALL-STAR',ring:'TITLE',fmvp:'FINALS MVP',yes:'Yes',no:'No',
      note:n=>`Standard deviations against the ${n} measurable seasons since 1951-52, with the weights you have set.`},
  cr_h:'Sources and attribution',
  cr_br_h:'Basketball-Reference · regular season',
  cr_br:`Full box score, advanced metrics, award voting, All-NBA, All-Defensive and All-Star selections, 1947–${SMAX}, through Sumitro Datta’s public data dump. The current regular season is read straight from Basketball-Reference every Monday.`,
  cr_po_h:'Basketball-Reference · playoffs and awards',
  cr_po:`Playoff stats for every season (totals and advanced), champions, Finals MVPs and the latest award voting, downloaded directly every Monday. Playoffs through ${BI.playoff_max||'—'}.`,
  cr_sg_h:'STATGOAT index',
  cr_sg1:'The transformation is our own: within-season z-scores, logarithmic tail compression, rings weighted by real contribution in each playoff run and the composition of the seven blocks.',
  cr_sg2:'The weighting is a formalized opinion, which is why you can change it above.',
  lg_attr:'<b>Attribution.</b> The original data keeps its source licenses. If you reuse this index, credit Basketball-Reference.',
  lg_aff:'<b>No affiliation.</b> STATGOAT is not affiliated with or endorsed by the NBA, the NBPA or Basketball-Reference.',
  lg_war:'<b>No warranty.</b> This is a historical analysis under one specific weighting. It is not a prediction, betting advice or settled truth.',
  blocks:{PROD:'Production',EFIC:'Efficiency',IMPACTO:'Impact',DEF:'Defense',PLAYOFFS:'Playoffs',TITULOS:'Titles',PREMIOS:'Awards'},
  tips:{PROD:'Points, rebounds, assists, steals and blocks per game, as a z-score within their season',
    EFIC:'Points added by scoring above his league’s True Shooting (efficiency × volume), plus ball security',
    IMPACTO:'PER, Win Shares per 48 and Box Plus/Minus',
    DEF:'DBPM, DWS/48, steal %, block %, defensive rebound %, All-Defensive teams and DPOY votes',
    PLAYOFFS:'Level over his best 4,000 playoff minutes against the other players in those playoffs, and total contribution',
    TITULOS:'Rings weighted by real contribution to each title run, plus Finals MVPs',
    PREMIOS:'MVP votes, All-NBA selections by tier and All-Star nods'},
  presets:{base:'Default',imp:'Impact only',notit:'No titles',po2:'Playoffs ×2',def2:'Defense ×2',reg:'Regular season only',hon:'Honors only'},
  filters:{all:'All',g400:'≥ 400 games',ring:'Champions',noring:'No ring',mvp:'MVP winners',pre80:'Before 1980',active:'Active'},
  noWeights:'no weights', normalized:'normalized to 100%',
  movers:n=>`${n} moves of 3+ spots in the top 25`,smovers:n=>`${n} seasons in the top 25 move 3+ spots`, baseOrder:'default order', overall:'overall',
  count:(a,b)=>`${a} of ${b} players`,
  more:n=>`Show more players (${n} left)`,
  record:'RECORD', partial:'PARTIAL DATA', seasonsShort:'seasons',
  card:{career:'CAREER',active:'ACTIVE',seasons:'seasons',games:'GAMES',minutes:'MINUTES',perGame:'game',
    teams:'TEAMS',league:'LEAGUE',pg:'PER GAME',pts:'POINTS',reb:'REBOUNDS',ast:'ASSISTS',stl:'STEALS',blk:'BLOCKS',tov:'TURNOVERS',tpm:'3-POINTERS',top5:'ALL-TIME TOP 5',withBonus:'with the bonus',
    cat:{pts:'points',trb:'rebounds',ast:'assists',stl:'steals',blk:'blocks',x3p:'threes'},
    po:'PLAYOFFS',poNone:'Never played in the playoffs.',poRuns:'seasons',vsReg:'vs. regular season',poPlus:'PLUS',plusUp:'rises in the playoffs',plusDown:'drops in the playoffs',plusEq:'holds steady',
    effImp:'EFFICIENCY & IMPACT',perAvg:'league avg 15.0',wsAvg:'avg 0.100',off:'off.',def:'def.',
    pct:'ON-COURT PERCENTAGES',stlP:'STEAL %',blkP:'BLOCK %',drbP:'DEF. REB. %',orbP:'OFF. REB. %',astP:'ASSIST %',
    totals:'CAREER TOTALS',honors:'HONORS',rings:'RINGS',asBest:'as his team’s best player',
    mvpShare:'cumulative vote share',anbaScale:'1st=5 · 2nd=3 · 3rd=1.5',adefScale:'1st=3 · 2nd=1.5',
  dx:{title:'WHERE THE SCORE COMES FROM',hint:'Tap a block to see where it comes from. On the right, the points it adds with your weights.',
    base:'Starting point (every block at 0, the index average)',bonus:'Totals bonus',total:'Score with your weights',
    rankIn:(r,n)=>`#${r} of ${n} in this block`,loading:'Loading…',fail:'Couldn’t load the detail.',
    career:(pk,pr,su,ca)=>`Career = 40% average of his 3 best seasons (${pk}) + 40% average of his 7 best (${pr}) + 20% cumulative, put on the same scale (${su}) = ${ca}. Then it’s put on the index scale.`,
    seasonsNote:n=>`His ${n} countable seasons (1,000+ minutes; before 1952, by games), sorted by this block. Top 3 in bold. If he has fewer than 7, the missing ones count as 0.`,
    value:'Value',season:'Season',team:'Team',
    cols:{PROD:['PTS','REB','AST','STL','BLK'],EFIC:['TS%','Pts added','TOV%'],IMPACTO:['PER','WS/48','BPM'],DEF:['DBPM','DWS/48','STL%','BLK%','DRB%']},
    defRec:(a1,a2,dw,dv)=>`25% of the block is recognition: All-Defense (${a1} first team, ${a2} second team) and DPOY votes (${dw} won${dv?', received votes in '+dv+' seasons':''}). The other 75%, these stats.`,
    poSum:(q,pr,fin,wp,ws)=>`Level over his best ${wp} playoff minutes: ${q}. Prediction from his regular season: ${pr}. Level that counts, closer to the real one the more he played: ${fin} (80% of the block). Total playoff Win Shares: ${ws} (20%).`,
    poCols:['Year','Team','G','MIN','PTS','REB','AST','BPM','WS','Level'],poMark:'In bold, the runs that make up his best 4,000 minutes.',
    poNone:'No playoff games: his regular-season prediction counts.',more:n=>`and ${n} more`,
    rCols:['Year','Team','Share of team WS','Ring value'],rSum:(n,c,f)=>`${n} ${n===1?'ring':'rings'}, adding up to ${c}. Finals MVP: ${f}. (70% rings, 30% Finals MVP.)`,
    rNone:'No rings.',rNote:'Each ring is worth his share of his team’s Win Shares in those playoffs: the typical best player on a champion is worth 1.6; on the roster without playing those playoffs, 0.05.',
    noShare:'didn’t play',fmvpLoss:y=>`Finals MVP without the ring: ${y}.`,best:'best on the team',
    aCols:['Year','MVP','All-NBA','All-Star'],aSum:(m,a,s)=>`MVP votes: ${m} (45%) · All-NBA: ${a} (35%) · All-Star: ${s} (20%)`,
    aNone:'No individual awards.',mvpWin:'MVP',tier:['','1st team','2nd team','3rd team'],place:r=>ord(r)},
    strength:'STRENGTH BY BLOCK',
    strengthNote:n=>`Standard deviations above the average of the ${n} measurable players. 0 = average player in the group · +2 = better than 97.7%.`,
    partialNote:'<b>Partial data:</b> his era didn’t record some of the model’s metrics, so these blocks rest on fewer indicators.',
    best3:'HIS THREE BEST SEASONS',cols:['YEAR','TEAM','PTS','REB','AST','PER','WS/48','BPM'],
    best3Note:'Ranked by a composite of production, efficiency, impact and defense measured as a z-score within his own year, not by points.'},
  footer:(s,d)=>`Data through the ${s} season, playoffs through ${BI.playoff_max||'—'}. Updated every Monday; last update: ${d}.`,
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
</dl>
<h3>WHAT THIS INDEX CALCULATES ON ITS OWN</h3><dl class="gl">
<dt>Score</dt><dd>The sum of the seven blocks times their weights, rescaled from 0 to 100 within the group: the leader scores 100. If you switch on the totals bonus, the scale becomes 0-97 plus up to 3 bonus points. It’s a relative scale: it tells you who’s ahead and by how much, not an absolute value.</dd>
<dt>Career</dt><dd>Each block is summarized as <code>40% average of the 3 best seasons + 40% average of the 7 best + 20% cumulative</code>. Before it’s added, the cumulative part is converted to the same scale as the peak through its all-time percentile, so each percentage weighs exactly what it says: longevity counts for 20%, no more. If a player has fewer than 3 or 7 qualifying seasons, the missing ones count as 0 (a league-average player): three good seasons are not a seven-year prime. Per-game performance comes first: nobody climbs by piling up mediocre seasons. Only seasons with 1,000+ minutes count.</dd>
<dt>Points added by efficiency</dt><dd>The core of the Efficiency block, in the regular season and the playoffs: <code>(his TS% − his league’s TS%) × attempts</code>, i.e. how many points per game a player adds by scoring better than his league’s average that year. It captures efficiency and volume together: a center shooting 5 times at 65% adds less than a scorer shooting 20 times at 63%. Ball security (30%) completes the block.</dd>
<dt>Playoffs block</dt><dd>Each postseason is measured against the other players in those same playoffs: production, efficiency (points added by efficiency and turnovers) and impact (PER, WS/48 and BPM). The mark combines two things: level over his best 4,000 playoff minutes (80%), just as the regular season counts his best seasons, and total playoff Win Shares (20%), just like the regular-season cumulative part.</dd>
<dt>Playoff plus</dt><dd>Whether a player rises or shrinks in the playoffs. Each postseason is compared with what his own regular season that same year predicted. +0.30 means rising a lot (Kawhi, Hakeem, LeBron); below −0.10, he drops. With few minutes it stays near 0. It’s shown on the player card but doesn’t add or subtract: playoff level already reflects what he really did, and counting the gap to expectations on top of it took points away from players with a great regular season and rewarded those starting from a weak one.</dd>
<dt>Few playoff minutes</dt><dd>A single series is a small sample. So the fewer playoff minutes a player has, the closer his mark sits to what his regular-season career predicts; with plenty of minutes, what he actually did takes over. Players who never reached the playoffs stay at that predicted level, with no accumulated volume.</dd>
<dt>Ring credit</dt><dd>Not every ring is worth the same. Each player gets the share of his team’s Win Shares in that postseason that he produced: a champion’s best player usually accounts for 20% to 35%; a bench player, almost nothing. Without this, a bench player with six rings would outrank Jerry West. A player on the roster who didn’t play in those playoffs gets a minimal credit; one traded away earlier, none.</dd>
<dt>Where the score comes from</dt><dd>On each player card, every block expands: the seasons that count and their stats, the career calculation (40% best 3, 40% best 7, 20% cumulative), his playoff runs one by one, every ring with its value and his awards year by year. Next to each block, the points it adds to his score with your current weights: the starting point (every block at 0) plus those points makes his score.</dd>
<dt>Rank range</dt><dd>The ranks a player moves between if the default weights change a little. 2,000 weight combinations close to the default are drawn (a 15% weight moves about ±5 points) and the range shown is where his rank falls in 8 out of 10. If two players’ ranges overlap, who comes first depends on how you weigh things, not on the data: for example, Jordan is #1 in 79% of the combinations and LeBron in 15%. It’s computed on the default weights, not on the ones you’ve set.</dd>
<dt>Sharing</dt><dd>The “Copy link to this view” button copies an address with your weights, the bonus, the tab, the filters and the open player card: whoever opens it sees exactly the same.</dd>
<dt>Position</dt><dd>The one he played the most minutes at in his career, according to Basketball-Reference (in Best seasons, the one from that year). Many players change over the years: LeBron is listed as a small forward and Duncan as a power forward because that’s where they played the most minutes. It’s only a filter: it doesn’t change the score. With any filter on, the list and the top on the right are numbered within the filter and show the overall rank next to it. Players from 1947 to 1951 mostly have no recorded position and only show up under “All positions”.</dd>
<dt>Totals bonus</dt><dd>Optional and off by default. If you switch it on, it adds points for anyone in the all-time top 5 of a career stat: points, rebounds, assists, steals, blocks or threes (NBA, ABA and BAA combined). 1st place gets 3 points, 2nd 2.4, 3rd 1.8, 4th 1.2 and 5th 0.6. Only his best category counts: two third places aren’t worth a record. It isn’t in the default score because it compares raw totals across eras (steals and blocks have been counted since 1974, threes since 1980, and seasons used to be shorter) and because longevity already counts for 20% in every block. Rankings update every Monday.</dd>
<dt>Best seasons</dt><dd>The index formula applied to a single year: regular season (production, efficiency, impact and defense), that year’s playoffs, the ring weighted by contribution and that season’s awards (MVP, DPOY, All-NBA, All-Star). Each block is compared with every measurable season and weighted with the weights you have set. Titles and awards are put on the same scale as the stats through their percentile: in a single year almost everything is zero, and without this a ring outweighed the best statistical season ever. Only seasons from 1951-52 on are included, when minutes start being recorded: before that, impact and defense can’t be measured.</dd>
<dt>Block scale</dt><dd>For each weight to mean what it says, every block has to be on the same scale. The statistical blocks already are (z-scores, with the tails compressed above 2 standard deviations). Titles and awards aren’t: three in four players have 0 and a few shoot off the chart, so at the top they made up 34% of the score instead of their 25%. That’s why they’re put on the stats scale through their percentile: having more rings than anyone is worth the same as being the best ever in production, not twice as much. The scale is continuous: players with nothing sit in the middle of their group and everyone else climbs from there, so a token ring or a single All-Star selection is worth almost the same as nothing, with no jumps of several points.</dd>
<dt>Partial data</dt><dd>Flags players whose era didn’t record some of the metrics. They’re scored only on what exists, re-weighting the blocks that are available.</dd>
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
const ICON={
 PROD:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3v18M5.6 5.6c2.6 2.6 2.6 10.2 0 12.8M18.4 5.6c-2.6 2.6-2.6 10.2 0 12.8"/>',
 EFIC:'<path d="M3 7h18"/><path d="M5 7l2.2 11h9.6L19 7"/><path d="M8 11h8M8.6 14.5h6.8"/>',
 IMPACTO:'<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
 DEF:'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
 PLAYOFFS:'<path d="M3 6h5v4h4M3 18h5v-4"/><path d="M12 10v4"/><circle cx="19" cy="12" r="2"/><path d="M14 12h3"/>',
 TITULOS:'<path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4"/><path d="M12 13v4M8 20h8M9 17h6"/>',
 PREMIOS:'<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>'
};
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
 noring:p=>!(get(p,'ring')>0),
 mvp:p=>get(p,'mvp')>0,
 pre80:p=>get(p,'y1')<1980,
 active:p=>get(p,'y1')>=MAXY
};

const $=s=>document.querySelector(s);
const CHUNK=60;
let W={...PRESETS.base}, useBonus=false, openRk=null, shown=CHUNK, mode='players',
    sFilter='all', sShown=CHUNK, openS=null, sscored=[], sview=[], posF='all',
    query='', filter='all', scored=[], view=[];
// orden con los pesos base: sirve de referencia para las flechas ▲▼ del top en vivo
let BASE_ORDER=[]; const BASE_POS={};
// filtro activo combinado con la posición (PG, SG, SF, PF, C o todas)
const POSK=['PG','SG','SF','PF','C'];
const okPos=v=>posF==='all'||v===posF;
const pFilt=()=>{const f=FILTERS[filter];return p=>f(p)&&okPos(get(p,'pos'));};
function basePos(){
  const key=filter+'|'+posF;
  if(!BASE_POS[key]){
    const f=pFilt(), m=new Map(); let k=0;
    for(const i of BASE_ORDER) if(f(P[i])) m.set(i,++k);
    BASE_POS[key]=m;
  }
  return BASE_POS[key];
}
// etiqueta del filtro activo para el top en vivo
const filtTag=seas=>{const t=T(), a=[];
  if(seas? sFilter!=='all' : filter!=='all') a.push((seas?t.sfilters[sFilter]:t.filters[filter]).toUpperCase());
  if(posF!=='all') a.push(t.pos[posF].toUpperCase());
  return a.length?' · '+a.join(' · '):'';};

const nf=(v,d=1)=>v==null?'—':Number(v).toFixed(d);
let SCN={lo:0,hi:1,tot:1};
const mil=v=>v==null?'—':Number(v).toLocaleString(loc());
const recs=p=>String(get(p,'rec')||'').split(',').filter(x=>x.includes(':')).map(x=>{const [k,r]=x.split(':');return {k,r:+r};});
const ord=r=>LANG==='en'?r+(['th','st','nd','rd'][r]||'th'):r+'.º';
const pc=v=>v==null?'—':(Number(v)*100).toFixed(1)+'%';
const norm=s=>s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
const NAMES=P.map(p=>norm(get(p,'n')));
/* ---------- temporadas completas ---------- */
const SF={}; (RAW.sf||[]).forEach((k,i)=>SF[k]=i);
const S=RAW.sd||[], SMIN=RAW.smin||{}, SN=RAW.sn||S.length;
const sg=(r,k)=>r[SF[k]];
const SNAMES=S.map(r=>norm(sg(r,'n')));
const SFILTERS={all:()=>true, ring:r=>sg(r,'champ')>0, noring:r=>!(sg(r,'champ')>0), mvp:r=>sg(r,'mvp')>0,
  pre80:r=>sg(r,'y')<1980, from2000:r=>sg(r,'y')>=2000};
const sFilt=()=>{const f=SFILTERS[sFilter];return r=>f(r)&&okPos(sg(r,'pos'));};
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
  SCN={lo,hi,tot};
  for(const o of out) o.s=useBonus ? 97*(o.v-lo)/((hi-lo)||1)+get(o.p,'bt') : 100*(o.v-lo)/((hi-lo)||1);
  out.sort((a,b)=>b.s-a.s);
  out.forEach((o,k)=>o.rk=k+1);
  return out;
}
function scoreSeasons(){
  const tot=BLOCKS.reduce((s,b)=>s+W[b.k],0)||1;
  const lo=BLOCKS.reduce((s,b)=>s+(W[b.k]/tot)*(SMIN[b.k]||0),0);
  const out=S.map((r,i)=>({i,r,v:BLOCKS.reduce((s,b)=>s+(W[b.k]/tot)*sg(r,b.k),0)}));
  let hi=-Infinity; for(const o of out) if(o.v>hi) hi=o.v;
  for(const o of out) o.s=100*(o.v-lo)/((hi-lo)||1);
  out.sort((a,b)=>b.s-a.s); out.forEach((o,k)=>o.rk=k+1);
  return out;
}
function applyView(){
  const f=pFilt(), q=norm(query.trim());
  view=scored.filter(o=>f(o.p)&&(!q||NAMES[o.i].includes(q)));
  const sf=sFilt();
  sview=sscored.filter(o=>sf(o.r)&&(!q||SNAMES[o.i].includes(q)));
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
  if(BI.playoff_seasons) $('#n_po').textContent=Number(BI.playoff_seasons).toLocaleString(loc(),{useGrouping:true});
  else $('#po_cell').hidden=true;
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
    <label for="s_${b.k}" title="${t.tips[b.k]}"><svg class="ico" style="color:${b.c}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON[b.k]}</svg>${bn(b.k)}</label>
    <input type="range" id="s_${b.k}" min="0" max="60" step="1" value="${W[b.k]}" aria-label="${bn(b.k)}">
    <output id="o_${b.k}"></output></div>`).join('');
  BLOCKS.forEach(b=>$('#s_'+b.k).addEventListener('input',e=>{W[b.k]=+e.target.value;syncP();recalc();}));

  $('#presets').innerHTML=Object.keys(PRESETS).map(id=>`<button data-p="${id}">${t.presets[id]}</button>`).join('');
  $('#presets').querySelectorAll('button').forEach(btn=>btn.onclick=()=>{
    W={...PRESETS[btn.dataset.p]};
    BLOCKS.forEach(b=>$('#s_'+b.k).value=W[b.k]); syncP(); recalc();});

  buildFilters();
  syncP();
}
function buildFilters(){
  const t=T(), seas=mode==='seasons', FS=seas?SFILTERS:FILTERS, cur=seas?sFilter:filter, lab=seas?t.sfilters:t.filters;
  $('#filters').innerHTML=Object.keys(FS).map(id=>`<button data-f="${id}" aria-pressed="${id===cur}">${lab[id]}</button>`).join('');
  $('#filters').querySelectorAll('button').forEach(btn=>btn.onclick=()=>{
    if(seas){ sFilter=btn.dataset.f; sShown=CHUNK; openS=null; }
    else { filter=btn.dataset.f; shown=CHUNK; openRk=null; }
    $('#filters').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.f===btn.dataset.f));
    applyView(); renderTop(); renderTable();});
  $('#posf').innerHTML=['all',...POSK].map(k=>`<button data-p="${k}" aria-pressed="${k===posF}">${t.pos[k]}</button>`).join('');
  $('#posf').querySelectorAll('button').forEach(btn=>btn.onclick=()=>{
    posF=btn.dataset.p; shown=CHUNK; sShown=CHUNK; openRk=null; openS=null;
    $('#posf').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.p===posF));
    applyView(); renderTop(); renderTable();});
}
function setMode(m){
  if(m===mode) return;
  mode=m; query=''; $('#q').value='';
  document.querySelectorAll('#tabs button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.m===mode));
  buildFilters(); applyView(); renderTop(); renderTable();
}
function bindOnce(){
  document.querySelectorAll('#tabs button').forEach(b=>b.onclick=()=>setMode(b.dataset.m));
  $('#q').addEventListener('input',e=>{query=e.target.value;shown=CHUNK;sShown=CHUNK;applyView();renderTable();});
  $('#bonus').addEventListener('change',e=>{useBonus=e.target.checked;recalc();});
  $('#share').onclick=share;
  $('#tb').addEventListener('click',e=>{const x=e.target.closest('.xr'); if(x){e.stopPropagation(); toggleX(x);}});
  $('#more').onclick=()=>{ if(mode==='seasons') sShown+=CHUNK*3; else shown+=CHUNK*3; renderTable();};
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
function recalc(){
  const oi=openRk?scored[openRk-1]?.i:null;            // misma ficha abierta aunque cambie su puesto
  scored=score(); sscored=scoreSeasons();
  if(oi!=null) openRk=scored.find(o=>o.i===oi)?.rk||null;
  applyView(); renderTop(); renderTable();
}
/* ---------- enlace: la dirección guarda pesos, filtros, pestaña y ficha abierta ---------- */
function stateURL(){
  const u=new URL(location.href), sp=u.searchParams;
  const set=(k,v)=>{ if(v==null) sp.delete(k); else sp.set(k,v); };
  set('w', BLOCKS.every(b=>W[b.k]===PRESETS.base[b.k])?null:BLOCKS.map(b=>W[b.k]).join('.'));
  set('b', useBonus?'1':null);
  set('t', mode==='seasons'?'s':null);
  set('f', filter==='all'?null:filter);
  set('sf', sFilter==='all'?null:sFilter);
  set('pos', posF==='all'?null:posF);
  const op=mode==='players'&&openRk?scored[openRk-1]:null;
  set('p', op?get(op.p,'id'):null);
  const os=mode==='seasons'&&openS!=null?S[openS]:null;
  set('s', os?sg(os,'id')+'-'+sg(os,'y'):null);
  sp.set('lang',LANG);
  return u;
}
function syncURL(){ try{history.replaceState(null,'',stateURL());}catch(e){} }
function readURL(){
  let sp; try{sp=new URLSearchParams(location.search);}catch(e){return {};}
  const w=(sp.get('w')||'').split('.').map(Number);
  if(w.length===BLOCKS.length&&w.every(x=>Number.isFinite(x)&&x>=0&&x<=60)) BLOCKS.forEach((b,i)=>W[b.k]=w[i]);
  if(sp.get('b')==='1'){ useBonus=true; $('#bonus').checked=true; }
  if(FILTERS[sp.get('f')]) filter=sp.get('f');
  if(SFILTERS[sp.get('sf')]) sFilter=sp.get('sf');
  if(POSK.includes(sp.get('pos'))) posF=sp.get('pos');
  return {seasons:sp.get('t')==='s', p:sp.get('p'), s:sp.get('s')};
}
function openFromURL(st){
  if(st.p&&mode==='players'){
    const o=scored.find(o=>get(o.p,'id')===st.p), idx=o?view.indexOf(o):-1;
    if(idx>=0){ openRk=o.rk; shown=Math.max(shown,idx+5); renderTable(); }
  }
  const m=st.s&&mode==='seasons'?st.s.match(/^(.+)-(\d{4})$/):null;
  if(m){
    const i=S.findIndex(r=>sg(r,'id')===m[1]&&sg(r,'y')===+m[2]), idx=sview.findIndex(o=>o.i===i);
    if(idx>=0){ openS=i; sShown=Math.max(sShown,idx+5); renderTable(); }
  }
  setTimeout(()=>document.querySelector('tr.open')?.scrollIntoView({block:'center'}),50);
}
async function share(){
  syncURL();
  const url=location.href, t=T(), lab=$('#share span');
  if(navigator.share&&matchMedia('(pointer:coarse)').matches){
    try{ await navigator.share({title:document.title,url}); }catch(e){}
    return;
  }
  try{ await navigator.clipboard.writeText(url); }
  catch(e){ const i=document.createElement('input'); i.value=url; document.body.appendChild(i); i.select();
    try{document.execCommand('copy');}catch(_){} i.remove(); }
  lab.textContent=t.copied; setTimeout(()=>{lab.textContent=T().share;},1800);
}

function renderTopSeasons(){
  const t=T(), sf=sFilt(), pool=sscored.filter(o=>sf(o.r)), all=sFilter==='all'&&posF==='all';
  // posición con los pesos por defecto (dentro del filtro activo) para las flechas
  const base=new Map(); S.map((r,i)=>[sg(r,'srk'),i]).filter(([,i])=>sf(S[i])).sort((a,b)=>a[0]-b[0]).forEach(([,i],k)=>base.set(i,k+1));
  const lab=document.querySelector('[data-i18n="c_live"]');
  if(lab) lab.textContent=t.c_live+' · '+t.tab_seasons.toUpperCase()+filtTag(true);
  $('#live').innerHTML=pool.slice(0,10).map((o,k)=>{
    const pos=k+1, d=(base.get(o.i)||pos)-pos;
    const m=d>0?`<span class="delta up">▲${d}</span>`:d<0?`<span class="delta down">▼${-d}</span>`:'';
    return `<div class="lrow" data-si="${o.i}"><span class="lr num">${pos}</span>
      <span class="ln">${sg(o.r,'n')} <span style="font-family:Archivo;font-size:11px;font-weight:600;color:var(--ink-soft)">${seasonLabel(sg(o.r,'y'))}</span>${m}</span><span class="ls num">${o.s.toFixed(1)}</span></div>`;}).join('');
  $('#live').querySelectorAll('.lrow').forEach(el=>el.onclick=()=>{
    const i=+el.dataset.si; query=''; $('#q').value=''; applyView();
    const idx=sview.findIndex(o=>o.i===i); openS=i; sShown=Math.max(sShown,idx+5); renderTable();
    document.querySelector('tr.open')?.scrollIntoView({block:'center'});});
  const moved=pool.slice(0,25).filter((o,k)=>Math.abs((base.get(o.i)||k+1)-(k+1))>=3).length;
  $('#movers').textContent=moved?t.smovers(moved):t.baseOrder;
}
function renderTop(){
  const t=T(), tot=BLOCKS.reduce((s,b)=>s+W[b.k],0)||1;
  BLOCKS.forEach(b=>$('#o_'+b.k).textContent=Math.round(100*W[b.k]/tot)+'%');
  $('#wsum').textContent=BLOCKS.reduce((s,b)=>s+W[b.k],0)===0?t.noWeights:t.normalized;
  if(mode==='seasons') return renderTopSeasons();
  // el top en vivo respeta el filtro activo (no la búsqueda por nombre)
  const f=pFilt(), pool=scored.filter(o=>f(o.p)), bp=basePos(), all=filter==='all'&&posF==='all';
  const lab=document.querySelector('[data-i18n="c_live"]');
  if(lab) lab.textContent=t.c_live+filtTag(false);
  $('#live').innerHTML=pool.slice(0,10).map((o,k)=>{
    const pos=k+1, d=(bp.get(o.i)||pos)-pos;
    const m=d>0?`<span class="delta up">▲${d}</span>`:d<0?`<span class="delta down">▼${-d}</span>`:'';
    const gr=all?'':`<span style="font-family:Archivo;font-size:10.5px;font-weight:600;color:var(--ink-soft);margin-left:6px">#${o.rk} ${t.overall}</span>`;
    return `<div class="lrow" data-go="${o.rk}"><span class="lr num">${pos}</span>
      <span class="ln">${get(o.p,'n')}${m}${gr}</span><span class="ls num">${o.s.toFixed(1)}</span></div>`;}).join('');
  $('#live').querySelectorAll('.lrow').forEach(el=>el.onclick=()=>{
    const o=scored[+el.dataset.go-1];
    query=''; $('#q').value=''; applyView();
    const idx=view.indexOf(o);
    openRk=o.rk; shown=Math.max(shown,idx+5); renderTable();
    document.querySelector('tr.open')?.scrollIntoView({block:'center'});});
  const moved=pool.slice(0,25).filter((o,k)=>Math.abs((bp.get(o.i)||k+1)-(k+1))>=3).length;
  $('#movers').textContent=moved?t.movers(moved):t.baseOrder;
}

function setHead(){
  const t=T(), th=document.querySelectorAll('table:not(.seas) thead th');
  if(th.length>=4){ th[1].textContent=mode==='seasons'?t.th_season:t.th_player; }
}
function renderSeasons(){
  const t=T(), tot=BLOCKS.reduce((s,b)=>s+W[b.k],0)||1;
  const maxS=sscored.length?sscored[0].s:1;
  const slice=sview.slice(0,sShown);
  const isF=sFilter!=='all'||posF!=='all', fpos=new Map();
  if(isF){const f=sFilt(); let k=0; for(const o of sscored) if(f(o.r)) fpos.set(o.i,++k);}
  $('#count').textContent=t.scount(sview.length.toLocaleString(loc()),SN.toLocaleString(loc()));
  $('#tb').innerHTML=slice.map(o=>{
    const r=o.r, parts=BLOCKS.map(b=>({c:b.c,n:bn(b.k),v:(W[b.k]/tot)*(sg(r,b.k)-(SMIN[b.k]||0))}));
    const sum=parts.reduce((s,x)=>s+x.v,0)||1;
    const bar=`<div class="stack" style="width:${Math.max(4,100*o.s/maxS)}%">`+
      parts.map(x=>`<i style="width:${100*x.v/sum}%;background:${x.c}" title="${x.n}"></i>`).join('')+'</div>';
    const tg=[sg(r,'mvp')&&t.tag.mvp, sg(r,'dpoy')&&t.tag.dpoy, sg(r,'champ')&&t.tag.ring, sg(r,'fmvp')&&t.tag.fmvp]
      .filter(Boolean).map(x=>`<span class="flag aw">${x}</span>`).join('');
    const op=openS===o.i;
    return `<tr class="main${op?' open':''}" data-si="${o.i}">
      <td class="rk num">${isF?fpos.get(o.i):o.rk}</td>
      <td class="nm">${sg(r,'n')}${tg}<small>${seasonLabel(sg(r,'y'))} · ${sg(r,'tm')}${sg(r,'lg')==='ABA'?' · ABA':''}${isF?` · #${o.rk} ${t.overall}`:''}</small></td>
      <td class="bar">${bar}</td><td class="sc num">${o.s.toFixed(1)}</td></tr>`+(op?sdetail(r):'');
  }).join('');
  $('#tb').querySelectorAll('tr.main').forEach(tr=>tr.onclick=()=>{
    const i=+tr.dataset.si; openS=openS===i?null:i; renderTable();});
  $('#more').hidden=sview.length<=sShown;
  $('#more').textContent=t.smore((sview.length-sShown).toLocaleString(loc()));
}
function sdetail(r){
  const t=T(), d=t.sd, c=t.card, g=k=>sg(r,k);
  const blocks=BLOCKS.map(b=>{
    const v=g(b.k), w=Math.min(50,Math.abs(v)/7*50);
    return `<div class="blk"><span class="bl">${bn(b.k)}</span>
      <span class="bb"><i style="background:${b.c};${v>=0?`left:50%;width:${w}%`:`right:50%;width:${w}%`}"></i></span>
      <span class="bv">${v>=0?'+':''}${v.toFixed(2)}</span></div>`;}).join('');
  const yn=v=>v?d.yes:d.no;
  const po=g('pog')?`<dl class="kv"><dt>${d.games}</dt><dd>${g('pog')}</dd><dt>${d.ppg}</dt><dd>${nf(g('popg'))}</dd></dl>`
                   :`<p class="pnote" style="margin-top:0">${d.none}</p>`;
  return `<tr class="det"><td colspan="4"><div class="dgrid">
    <div class="card"><h4>${d.rs}</h4><dl class="kv">
      <dt>${T().posLab}</dt><dd>${T().posOne[g('pos')]||'—'}</dd>
      <dt>${c.pts}</dt><dd>${nf(g('ppg'))}</dd><dt>${c.reb}</dt><dd>${nf(g('rpg'))}</dd><dt>${c.ast}</dt><dd>${nf(g('apg'))}</dd>
      <dt>TS%</dt><dd>${pc(g('ts'))}</dd><dt>PER</dt><dd>${nf(g('per'))}</dd><dt>BPM</dt><dd>${nf(g('bpm'))}</dd></dl></div>
    <div class="card"><h4>${d.po}</h4>${po}</div>
    <div class="card"><h4>${d.aw}</h4><dl class="kv">
      <dt>MVP</dt><dd>${yn(g('mvp'))} <small>(${nf(g('mvps'),2)} ${d.mvpv})</small></dd>
      <dt>DPOY</dt><dd>${yn(g('dpoy'))}</dd><dt>${d.anba}</dt><dd>${g('anba')||'—'}</dd><dt>${d.as}</dt><dd>${yn(g('as'))}</dd>
      <dt>${d.ring}</dt><dd>${yn(g('champ'))}</dd><dt>${d.fmvp}</dt><dd>${yn(g('fmvp'))}</dd></dl></div>
    <div class="card"><h4>${c.strength}</h4>${blocks}<p class="pnote">${d.note(SN.toLocaleString(loc()))}</p></div>
  </div></td></tr>`;
}
function renderTable(){
  setHead(); syncURL();
  if(mode==='seasons') return renderSeasons();
  const t=T(), tot=BLOCKS.reduce((s,b)=>s+W[b.k],0)||1;
  const maxS=scored.length?scored[0].s:1;
  const slice=view.slice(0,shown);
  // con un filtro activo se numera dentro del filtro, igual que el top de la derecha
  const isF=filter!=='all'||posF!=='all', fpos=new Map();
  if(isF){const f=pFilt(); let k=0; for(const o of scored) if(f(o.p)) fpos.set(o.i,++k);}
  $('#count').textContent=t.count(view.length.toLocaleString(loc()),P.length.toLocaleString(loc()));
  $('#tb').innerHTML=slice.map(o=>{
    const p=o.p, parts=BLOCKS.map(b=>({c:b.c,n:bn(b.k),v:(W[b.k]/tot)*(get(p,b.k)-MINS[b.k])}));
    const sum=parts.reduce((s,x)=>s+x.v,0)||1;
    const bar=`<div class="stack" style="width:${Math.max(4,100*o.s/maxS)}%">`+
      parts.map(x=>`<i style="width:${100*x.v/sum}%;background:${x.c}" title="${x.n}"></i>`).join('')+'</div>';
    const rec1=recs(p).filter(x=>x.r===1).map(x=>t.card.cat[x.k].toUpperCase()).join(', ');
    const fl=(rec1?`<span class="flag">${t.record} ${rec1}</span>`:'')+
      (get(p,'cov')<0.75?`<span class="flag warn">${t.partial}</span>`:'');
    const op=openRk===o.rk;
    return `<tr class="main${op?' open':''}" data-rk="${o.rk}">
      <td class="rk num">${isF?fpos.get(o.i):o.rk}</td>
      <td class="nm">${get(p,'n')}${fl}<small>${get(p,'y0')}–${get(p,'y1')} · ${get(p,'sea')} ${t.seasonsShort}${get(p,'lg')==='ABA'?' · ABA':''}${isF?` · #${o.rk} ${t.overall}`:''}</small></td>
      <td class="bar">${bar}</td><td class="sc num">${o.s.toFixed(1)}</td></tr>`+(op?detail(p,o):'');
  }).join('');
  $('#tb').querySelectorAll('tr.main').forEach(tr=>tr.onclick=()=>{
    const rk=+tr.dataset.rk; openRk=openRk===rk?null:rk; renderTable();});
  $('#more').hidden=view.length<=shown;
  $('#more').textContent=t.more((view.length-shown).toLocaleString(loc()));
}

/* ---------- ficha completa ---------- */
/* ---------- de dónde sale la nota: bloques desplegables con su detalle ---------- */
const DETC=new Map(), OPENX=new Set(); let OPENX_ID=null;
function loadDet(id){
  if(!id) return Promise.resolve(null);
  if(!DETC.has(id)) DETC.set(id, fetch(`det/${id}.json`).then(r=>r.ok?r.json():null).catch(()=>null));
  return DETC.get(id);
}
const zf=v=>v==null?'—':(v>=0?'+':'−')+Math.abs(v).toFixed(2);
const th=v=>v==null?'—':String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, LANG==='en'?',':'.');
const pf=v=>v==null?'—':(v*100).toFixed(1);
function contrib(p,k){ const sc=useBonus?97:100; return sc*(W[k]/SCN.tot)*get(p,k)/((SCN.hi-SCN.lo)||1); }
function blockRank(p,k){ const v=get(p,k); let r=1; for(const q of P) if(get(q,k)>v) r++; return r; }
function xblocks(p,o){
  const c=T().card, d=c.dx, id=get(p,'id');
  if(OPENX_ID!==id){ OPENX.clear(); OPENX_ID=id; }
  loadDet(id);
  const sc=useBonus?97:100, base=sc*(0-SCN.lo)/((SCN.hi-SCN.lo)||1);
  const rows=BLOCKS.map(b=>{
    const v=get(p,b.k), w=Math.min(50,Math.abs(v)/7*50), ct=contrib(p,b.k), op=OPENX.has(b.k);
    return `<button type="button" class="xr" data-k="${b.k}" data-id="${id}" aria-expanded="${op}">
      <span class="bl">${bn(b.k)}</span>
      <span class="bb"><i style="background:${b.c};${v>=0?`left:50%;width:${w}%`:`right:50%;width:${w}%`}"></i></span>
      <span class="bv">${v>=0?'+':''}${v.toFixed(2)}</span>
      <span class="xc">${ct>=0?'+':'−'}${Math.abs(ct).toFixed(1)}</span></button>
      <div class="xp" data-k="${b.k}"${op?'':' hidden'}>${op?'<p class="pnote">'+d.loading+'</p>':''}</div>`;}).join('');
  if(OPENX.size) loadDet(id).then(det=>{ for(const k of OPENX) fillX(id,k,det); });
  const bt=useBonus?get(p,'bt'):0;
  return `<div class="card xb" style="grid-column:1/-1"><h4>${d.title}</h4>
    <p class="pnote" style="margin:0 0 10px">${d.hint}</p>${rows}
    <p class="pnote">${d.base}: ${base.toFixed(1)}${useBonus&&bt?` · ${d.bonus}: +${bt.toFixed(1)}`:''} · <b>${d.total}: ${o.s.toFixed(1)}</b></p>
    <p class="pnote">${c.strengthNote(P.length.toLocaleString(loc()))}${get(p,'cov')<0.75?'<br>'+c.partialNote:''}</p></div>`;
}
function fillX(id,k,det){
  const box=document.querySelector(`.xp[data-k="${k}"]`), btn=document.querySelector(`.xr[data-k="${k}"][data-id="${id}"]`);
  if(!box||!btn) return;
  const p=P.find(q=>get(q,'id')===id), d=T().card.dx;
  box.innerHTML=det? xpanel(p,k,det) : `<p class="pnote">${d.fail}</p>`;
}
function toggleX(btn){
  const k=btn.dataset.k, id=btn.dataset.id, box=btn.nextElementSibling, open=btn.getAttribute('aria-expanded')!=='true';
  btn.setAttribute('aria-expanded',open); box.hidden=!open;
  if(open){ OPENX.add(k); box.innerHTML=`<p class="pnote">${T().card.dx.loading}</p>`; loadDet(id).then(det=>fillX(id,k,det)); }
  else OPENX.delete(k);
}
function xtable(head,rows,bold){
  return `<div class="xt"><table class="seas"><thead><tr>${head.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${
    rows.map((r,i)=>`<tr${bold&&bold(i)?' class="xbold"':''}>${r.map(x=>`<td>${x}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
function xpanel(p,k,det){
  const d=T().card.dx, sl=y=>seasonLabel(y);
  const rk=`<p class="xrk">${d.rankIn(th(blockRank(p,k)),th(P.length))}</p>`;
  if(['PROD','EFIC','IMPACTO','DEF'].includes(k)){
    const bi={PROD:6,EFIC:7,IMPACTO:8,DEF:9}[k];
    const ss=(det.s||[]).filter(r=>r[5]&&r[bi]!=null).sort((a,b)=>b[bi]-a[bi]);
    const stat={PROD:r=>[nf(r[10]),nf(r[11]),nf(r[12]),nf(r[13]),nf(r[14])],
      EFIC:r=>[pf(r[15]),r[16]==null?'—':(r[16]>=0?'+':'')+nf(r[16]),nf(r[17])],
      IMPACTO:r=>[nf(r[18]),r[19]==null?'—':r[19].toFixed(3),nf(r[20])],
      DEF:r=>[nf(r[21]),r[22]==null?'—':r[22].toFixed(3),nf(r[23]),nf(r[24]),nf(r[25])]}[k];
    const cc=(det.c||{})[k]||[];
    let h=rk+`<p class="pnote">${d.career(zf(cc[0]),zf(cc[1]),zf(cc[2]),zf(cc[3]))}</p>`;
    if(k==='DEF'){
      const a=det.a||[]; const a1=a.filter(x=>x[5]===1).length, a2=a.filter(x=>x[5]===2).length;
      const dw=a.filter(x=>x[8]).length, dv=a.filter(x=>x[7]).length;
      h+=`<p class="pnote">${d.defRec(a1,a2,dw,dv)}</p>`;
    }
    h+=`<p class="pnote">${d.seasonsNote(ss.length)}</p>`;
    h+=xtable([d.season,d.team,d.value,...d.cols[k]], ss.slice(0,7).map(r=>[sl(r[0]),r[1]+(r[2]==='ABA'?' · ABA':''),zf(r[bi]),...stat(r)]), i=>i<3);
    if(ss.length>7) h+=`<p class="pnote">${d.more(ss.length-7)}</p>`;
    return h;
  }
  if(k==='PLAYOFFS'){
    const pq=det.pq, po=(det.po||[]).filter(r=>r[9]!=null).sort((a,b)=>b[9]-a[9]);
    if(!po.length) return rk+`<p class="pnote">${d.poNone}</p>`;
    let acc=0; const cnt=po.map(r=>{ const inb=acc<4000; acc+=(r[3]!=null?r[3]:(r[2]||0)*30); return inb; });
    let h=rk+`<p class="pnote">${d.poSum(zf(pq[0]),zf(pq[1]),zf(pq[2]),th(pq[3]),nf(pq[4]))}</p><p class="pnote">${d.poMark}</p>`;
    h+=xtable(d.poCols, po.slice(0,12).map(r=>[sl(r[0]),r[1],r[2]??'—',mil(r[3]),nf(r[4]),nf(r[5]),nf(r[6]),nf(r[7]),nf(r[8]),zf(r[9])]), i=>cnt[i]);
    if(po.length>12) h+=`<p class="pnote">${d.more(po.length-12)}</p>`;
    return h;
  }
  if(k==='TITULOS'){
    const r=det.r||[], fm=r.filter(x=>x[5]).length+(det.fm||[]).length;
    let h=rk;
    if(!r.length) h+=`<p class="pnote">${d.rNone}</p>`;
    else{
      const sum=r.reduce((s,x)=>s+(x[3]||0),0);
      h+=`<p class="pnote">${d.rSum(r.length,sum.toFixed(2),fm)}</p>`;
      h+=xtable(d.rCols, r.map(x=>[sl(x[0])+(x[5]?' ★':''),x[1],x[2]==null?d.noShare:pf(x[2])+'%'+(x[4]?` <small>(${d.best})</small>`:''),x[3].toFixed(2)]));
      h+=`<p class="pnote">${d.rNote}</p>`;
    }
    if((det.fm||[]).length) h+=`<p class="pnote">${d.fmvpLoss(det.fm.map(sl).join(', '))}</p>`;
    return h;
  }
  if(k==='PREMIOS'){
    const a=(det.a||[]).filter(x=>x[1]||x[4]||x[6]);
    if(!a.length) return rk+`<p class="pnote">${d.aNone}</p>`;
    const ms=a.reduce((s,x)=>s+(x[2]||0),0), an=a.filter(x=>x[4]).length, as=a.filter(x=>x[6]).length;
    return rk+`<p class="pnote">${d.aSum(ms.toFixed(2),an,as)}</p>`+
      xtable(d.aCols, a.map(x=>[sl(x[0]), x[1]?(x[3]?`<b>${d.mvpWin}</b> (${pf(x[2])}%)`:`${d.place(x[1])} (${pf(x[2])}%)`):'—', d.tier[x[4]]||'—', x[6]?'✓':'—']), i=>a[i][3]);
  }
  return '';
}
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

  const lift = g('po')!=null&&g('ppg')!=null ? g('po')-g('ppg') : null;
  const plus = g('poplus');
  const poCard = !g('pog')
    ? `<div class="card"><h4>${c.po}</h4><p class="pnote" style="margin-top:0">${c.poNone}</p></div>`
    : `<div class="card"><h4>${c.po}</h4><dl class="kv">
      <dt>${c.games}</dt><dd>${mil(g('pog'))} <small>(${g('poruns')} ${c.poRuns})</small></dd>
      <dt>${c.minutes}</dt><dd>${mil(g('pomp'))}</dd>
      <dt>${c.pts}</dt><dd>${nf(g('po'))}${lift==null?'':` <small>(${lift>=0?'+':''}${nf(lift)} ${c.vsReg})</small>`}</dd>
      <dt>${c.reb}</dt><dd>${nf(g('porpg'))}</dd>
      <dt>${c.ast}</dt><dd>${nf(g('poapg'))}</dd>
      <dt>TS%</dt><dd>${pc(g('pots'))}</dd>
      <dt>PER</dt><dd>${nf(g('poper'))}</dd>
      <dt>WS</dt><dd>${nf(g('pows'))}</dd>
      <dt>BPM</dt><dd>${nf(g('pobpm'))}</dd>
      ${plus==null?'':`<dt>${c.poPlus}</dt><dd>${plus>=0?'+':'−'}${Math.abs(plus).toFixed(2)} <small>(${plus>=.1?c.plusUp:plus<=-.1?c.plusDown:c.plusEq})</small></dd>`}
    </dl></div>`;

  return `<tr class="det"><td colspan="4"><div class="dgrid">

    <div class="card"><h4>${c.career}</h4><dl class="kv">
      <dt>${c.active}</dt><dd>${g('y0')}–${g('y1')} · ${g('sea')} ${c.seasons}</dd>
      <dt>${c.games}</dt><dd>${mil(g('g'))}</dd>
      <dt>${c.minutes}</dt><dd>${mil(g('mp'))} <small>(${nf(g('mpg'))}/${c.perGame})</small></dd>
      <dt>${c.teams}</dt><dd>${(g('tm')||[]).join(' · ')||'—'}</dd>
      <dt>${c.league}</dt><dd>${g('lg')}</dd>
      <dt>${T().posLab}</dt><dd>${T().posOne[g('pos')]||'—'}</dd>
      ${g('r10')?`<dt>${T().margin}</dt><dd>${g('r10')===g('r90')?ord(g('r10')):ord(g('r10'))+' – '+ord(g('r90'))} <small>(${T().marginNote}${g('t1')>0?' · '+T().top1(Math.round(g('t1')*100)):''})</small></dd>`:''}
    </dl></div>

    <div class="card"><h4>${c.pg}</h4><dl class="kv">
      <dt>${c.pts}</dt><dd>${nf(g('ppg'))}</dd>
      <dt>${c.reb}</dt><dd>${nf(g('rpg'))}</dd>
      <dt>${c.ast}</dt><dd>${nf(g('apg'))}</dd>
      <dt>${c.stl}</dt><dd>${nf(g('spg'))}</dd>
      <dt>${c.blk}</dt><dd>${nf(g('bpg'))}</dd>
      <dt>${c.tov}</dt><dd>${nf(g('topg'))}</dd>
    </dl></div>

    ${poCard}

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
      <dt>${c.tpm}</dt><dd>${mil(g('tx3p'))}</dd>
      ${recs(p).length?`<dt>${c.top5}</dt><dd>${recs(p).map(x=>`${c.cat[x.k]} ${ord(x.r)}`).join(' · ')} <small>(+${nf(g('bt'))} ${c.withBonus})</small></dd>`:''}
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

    ${xblocks(p,o)}

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
scored=score(); BASE_ORDER=scored.map(o=>o.i);   // orden base, antes de leer la dirección
const ST=readURL();
buildControls();
syncP(); recalc();
if(ST.seasons) setMode('seasons');
openFromURL(ST);

/* ---------- bienvenida: primera visita y enlace "Cómo funciona" ---------- */
function openWelcome(){ $('#welcome').hidden=false; $('#wl_btn').focus(); }
function closeWelcome(){
  if($('#welcome').hidden) return;
  $('#welcome').hidden=true;
  try{localStorage.setItem('statgoat_welcome','1');}catch(e){}
}
$('#howto').onclick=openWelcome;
$('#wl_btn').onclick=closeWelcome;
$('#welcome').addEventListener('click',e=>{if(e.target.id==='welcome') closeWelcome();});
document.addEventListener('keydown',e=>{if(e.key==='Escape') closeWelcome();});
// Si la dirección ya abre una vista concreta, no tapar la tabla; si es primera visita, mostrar la tarjeta
(function(){
  const sp=new URLSearchParams(location.search);
  const linked=['w','b','t','f','sf','pos','p','s'].some(k=>sp.has(k));
  let seen=false; try{seen=localStorage.getItem('statgoat_welcome')==='1';}catch(e){seen=true;}
  if(!linked && !seen) openWelcome();
})();
