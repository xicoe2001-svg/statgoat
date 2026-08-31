/* ---------- descompresión columnar ---------- */
const F={}; RAW.f.forEach((k,i)=>F[k]=i);
const P=RAW.d;
const get=(p,k)=>p[F[k]];

const BLOCKS=[
 {k:'PROD',n:'Producción',c:'var(--w-prod)',d:15},
 {k:'EFIC',n:'Eficiencia',c:'var(--w-efic)',d:7},
 {k:'IMPACTO',n:'Impacto',c:'var(--w-imp)',d:20},
 {k:'DEF',n:'Defensa',c:'var(--w-def)',d:13},
 {k:'PLAYOFFS',n:'Playoffs',c:'var(--w-po)',d:20},
 {k:'TITULOS',n:'Títulos',c:'var(--w-tit)',d:15},
 {k:'PREMIOS',n:'Premios',c:'var(--w-pre)',d:10}
];
const TIP={PROD:'Pts, reb, as, robos y tapones por partido en z-score de su temporada',
 EFIC:'True Shooting relativo a la liga y control de pérdidas',
 IMPACTO:'PER, Win Shares por 48 y Box Plus/Minus',
 DEF:'DBPM, DWS/48, %robo, %tapón, %rebote defensivo, All-Defensivo y DPOY',
 PLAYOFFS:'Anotación de playoffs ajustada a la época, diferencia vs. su liga regular y RAPTOR de postemporada',
 TITULOS:'Anillos ponderados por rol real y Finals MVP',
 PREMIOS:'Votos al MVP, All-NBA por nivel y All-Star'};
const PRESETS={
 'Base':{PROD:15,EFIC:7,IMPACTO:20,DEF:13,PLAYOFFS:20,TITULOS:15,PREMIOS:10},
 'Solo impacto':{PROD:0,EFIC:0,IMPACTO:100,DEF:0,PLAYOFFS:0,TITULOS:0,PREMIOS:0},
 'Sin títulos':{PROD:18,EFIC:8,IMPACTO:24,DEF:15,PLAYOFFS:23,TITULOS:0,PREMIOS:12},
 'Playoffs ×2':{PROD:12,EFIC:5,IMPACTO:16,DEF:10,PLAYOFFS:40,TITULOS:11,PREMIOS:6},
 'Defensa ×2':{PROD:12,EFIC:5,IMPACTO:16,DEF:26,PLAYOFFS:17,TITULOS:14,PREMIOS:10},
 'Solo temp. regular':{PROD:30,EFIC:15,IMPACTO:35,DEF:20,PLAYOFFS:0,TITULOS:0,PREMIOS:0},
 'Solo palmarés':{PROD:0,EFIC:0,IMPACTO:0,DEF:0,PLAYOFFS:0,TITULOS:60,PREMIOS:40}
};
const FILTERS={
 'Todos':()=>true,
 '≥ 400 partidos':p=>get(p,'g')>=400,
 'Con anillo':p=>get(p,'ring')>0,
 'Con MVP':p=>get(p,'mvp')>0,
 'Antes de 1980':p=>get(p,'y1')<1980,
 'En activo 2026':p=>get(p,'y1')>=2026
};

const $=s=>document.querySelector(s);
const CHUNK=60;
let W={...PRESETS['Base']}, useBonus=true, openRk=null, shown=CHUNK,
    query='', filter='Todos', baseRank={}, scored=[], view=[];

const nf=(v,d=1)=>v==null?'—':Number(v).toFixed(d);
const mil=v=>v==null?'—':Number(v).toLocaleString('es-ES');
const pc=v=>v==null?'—':(Number(v)*100).toFixed(1)+'%';
const norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const NAMES=P.map(p=>norm(get(p,'n')));
const MINS={}; BLOCKS.forEach(b=>MINS[b.k]=Math.min(...P.map(p=>get(p,b.k))));

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

/* ---------- controles ---------- */
function buildControls(){
  $('#sliders').innerHTML=BLOCKS.map(b=>`<div class="sl">
    <label for="s_${b.k}" title="${TIP[b.k]}"><span class="dot" style="background:${b.c}"></span>${b.n}</label>
    <input type="range" id="s_${b.k}" min="0" max="60" step="1" value="${W[b.k]}" aria-label="${b.n}">
    <output id="o_${b.k}"></output></div>`).join('');
  BLOCKS.forEach(b=>$('#s_'+b.k).addEventListener('input',e=>{W[b.k]=+e.target.value;syncP();recalc();}));

  $('#presets').innerHTML=Object.keys(PRESETS).map(n=>`<button data-p="${n}">${n}</button>`).join('');
  $('#presets').querySelectorAll('button').forEach(btn=>btn.onclick=()=>{
    W={...PRESETS[btn.dataset.p]};
    BLOCKS.forEach(b=>$('#s_'+b.k).value=W[b.k]); syncP(); recalc();});

  $('#filters').innerHTML=Object.keys(FILTERS).map(n=>
    `<button data-f="${n}" aria-pressed="${n===filter}">${n}</button>`).join('');
  $('#filters').querySelectorAll('button').forEach(btn=>btn.onclick=()=>{
    filter=btn.dataset.f;
    $('#filters').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.f===filter));
    shown=CHUNK; applyView(); renderTable();});

  $('#q').addEventListener('input',e=>{query=e.target.value;shown=CHUNK;applyView();renderTable();});
  $('#bonus').addEventListener('change',e=>{useBonus=e.target.checked;recalc();});
  $('#more').onclick=()=>{shown+=CHUNK*3;renderTable();};
}
function syncP(){$('#presets').querySelectorAll('button').forEach(b=>{
  const p=PRESETS[b.dataset.p]; b.setAttribute('aria-pressed',BLOCKS.every(x=>p[x.k]===W[x.k]));});}

/* ---------- render ---------- */
function recalc(){scored=score();applyView();renderTop();renderTable();}

function renderTop(){
  const tot=BLOCKS.reduce((s,b)=>s+W[b.k],0)||1;
  BLOCKS.forEach(b=>$('#o_'+b.k).textContent=Math.round(100*W[b.k]/tot)+'%');
  $('#wsum').textContent=tot===0?'sin pesos':'normalizado a 100%';
  $('#live').innerHTML=scored.slice(0,8).map(o=>{
    const d=baseRank[get(o.p,'n')]-o.rk;
    const t=d>0?`<span class="delta up">▲${d}</span>`:d<0?`<span class="delta down">▼${-d}</span>`:'';
    return `<div class="lrow" data-go="${o.rk}"><span class="lr num">${o.rk}</span>
      <span class="ln">${get(o.p,'n')}${t}</span><span class="ls num">${o.s.toFixed(1)}</span></div>`;}).join('');
  $('#live').querySelectorAll('.lrow').forEach(el=>el.onclick=()=>{
    const o=scored[+el.dataset.go-1]; query=''; $('#q').value=''; filter='Todos';
    $('#filters').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.f==='Todos'));
    openRk=o.rk; shown=Math.max(shown,o.rk+5); applyView(); renderTable();
    document.querySelector('tr.open')?.scrollIntoView({block:'center'});});
  const moved=scored.slice(0,25).filter(o=>Math.abs(baseRank[get(o.p,'n')]-o.rk)>=3).length;
  $('#movers').textContent=moved?`${moved} cambios de 3+ puestos en el top 25`:'orden base';
}

function renderTable(){
  const tot=BLOCKS.reduce((s,b)=>s+W[b.k],0)||1;
  const maxS=scored.length?scored[0].s:1;
  const slice=view.slice(0,shown);
  $('#count').textContent=`${view.length.toLocaleString('es-ES')} de ${P.length.toLocaleString('es-ES')} jugadores`;
  $('#tb').innerHTML=slice.map(o=>{
    const p=o.p, parts=BLOCKS.map(b=>({c:b.c,n:b.n,v:(W[b.k]/tot)*(get(p,b.k)-MINS[b.k])}));
    const sum=parts.reduce((s,x)=>s+x.v,0)||1;
    const bar=`<div class="stack" style="width:${Math.max(4,100*o.s/maxS)}%">`+
      parts.map(x=>`<i style="width:${100*x.v/sum}%;background:${x.c}" title="${x.n}"></i>`).join('')+'</div>';
    const fl=(get(p,'rec')?`<span class="flag">RÉCORD ${get(p,'rec')}</span>`:'')+
      (get(p,'cov')<0.75?'<span class="flag warn">DATOS PARCIALES</span>':'');
    const op=openRk===o.rk;
    return `<tr class="main${op?' open':''}" data-rk="${o.rk}">
      <td class="rk num">${o.rk}</td>
      <td class="nm">${get(p,'n')}${fl}<small>${get(p,'y0')}–${get(p,'y1')} · ${get(p,'sea')} temp.${get(p,'lg')==='ABA'?' · ABA':''}</small></td>
      <td class="bar">${bar}</td><td class="sc num">${o.s.toFixed(1)}</td></tr>`+(op?detail(p,o):'');
  }).join('');
  $('#tb').querySelectorAll('tr.main').forEach(tr=>tr.onclick=()=>{
    const rk=+tr.dataset.rk; openRk=openRk===rk?null:rk; renderTable();});
  $('#more').hidden=view.length<=shown;
  $('#more').textContent=`Ver más jugadores (${(view.length-shown).toLocaleString('es-ES')} restantes)`;
}

/* ---------- ficha completa ---------- */
function detail(p,o){
  const g=k=>get(p,k);
  const blocks=BLOCKS.map(b=>{
    const v=g(b.k), w=Math.min(50,Math.abs(v)/7*50);
    return `<div class="blk"><span class="bl">${b.n}</span>
      <span class="bb"><i style="background:${b.c};${v>=0?`left:50%;width:${w}%`:`right:50%;width:${w}%`}"></i></span>
      <span class="bv">${v>=0?'+':''}${v.toFixed(2)}</span></div>`;}).join('');

  const seas=(g('seas')||[]).map(s=>`<tr><td>${s[0]}</td><td>${s[1]}</td><td>${nf(s[2])}</td>
    <td>${nf(s[3])}</td><td>${nf(s[4])}</td><td>${nf(s[5])}</td><td>${s[6]==null?'—':s[6].toFixed(3)}</td>
    <td>${nf(s[7])}</td></tr>`).join('');

  const poTxt = g('poe')
    ? `<dt>PLAYOFFS</dt><dd><small>fuera del top 250 anotador; estimado con su liga regular</small></dd>`
    : `<dt>PTS PLAYOFFS</dt><dd>${nf(g('po'))} <small>(${(g('po')-g('ppg'))>=0?'+':''}${nf(g('po')-g('ppg'))} vs. liga regular)</small></dd>`;

  return `<tr class="det"><td colspan="4"><div class="dgrid">

    <div class="card"><h4>CARRERA</h4><dl class="kv">
      <dt>ACTIVO</dt><dd>${g('y0')}–${g('y1')} · ${g('sea')} temporadas</dd>
      <dt>PARTIDOS</dt><dd>${mil(g('g'))}</dd>
      <dt>MINUTOS</dt><dd>${mil(g('mp'))} <small>(${nf(g('mpg'))}/partido)</small></dd>
      <dt>EQUIPOS</dt><dd>${(g('tm')||[]).join(' · ')||'—'}</dd>
      <dt>LIGA</dt><dd>${g('lg')}</dd>
    </dl></div>

    <div class="card"><h4>POR PARTIDO</h4><dl class="kv">
      <dt>PUNTOS</dt><dd>${nf(g('ppg'))}</dd>
      <dt>REBOTES</dt><dd>${nf(g('rpg'))}</dd>
      <dt>ASISTENCIAS</dt><dd>${nf(g('apg'))}</dd>
      <dt>ROBOS</dt><dd>${nf(g('spg'))}</dd>
      <dt>TAPONES</dt><dd>${nf(g('bpg'))}</dd>
      <dt>PÉRDIDAS</dt><dd>${nf(g('topg'))}</dd>
      ${poTxt}
    </dl></div>

    <div class="card"><h4>EFICIENCIA E IMPACTO</h4><dl class="kv">
      <dt>TS%</dt><dd>${pc(g('ts'))}</dd>
      <dt>USG%</dt><dd>${nf(g('usg'))}%</dd>
      <dt>TOV%</dt><dd>${nf(g('tovp'))}%</dd>
      <dt>PER</dt><dd>${nf(g('per'))} <small>(media liga 15,0)</small></dd>
      <dt>WS</dt><dd>${nf(g('ws'))}</dd>
      <dt>WS/48</dt><dd>${g('ws48')==null?'—':g('ws48').toFixed(3)} <small>(media 0,100)</small></dd>
      <dt>BPM</dt><dd>${nf(g('bpm'))} <small>(of. ${nf(g('obpm'))} · def. ${nf(g('dbpm'))})</small></dd>
      <dt>VORP</dt><dd>${nf(g('vorp'))}</dd>
    </dl></div>

    <div class="card"><h4>PORCENTAJES EN PISTA</h4><dl class="kv">
      <dt>ROBO %</dt><dd>${nf(g('stlp'))}%</dd>
      <dt>TAPÓN %</dt><dd>${nf(g('blkp'))}%</dd>
      <dt>REB. DEF. %</dt><dd>${nf(g('drbp'))}%</dd>
      <dt>REB. OF. %</dt><dd>${nf(g('orbp'))}%</dd>
      <dt>ASIST. %</dt><dd>${nf(g('astp'))}%</dd>
    </dl>
    <h4 style="margin-top:14px">TOTALES DE CARRERA</h4><dl class="kv">
      <dt>PUNTOS</dt><dd>${mil(g('tpts'))}</dd>
      <dt>REBOTES</dt><dd>${mil(g('trb'))}</dd>
      <dt>ASISTENCIAS</dt><dd>${mil(g('tast'))}</dd>
      <dt>ROBOS</dt><dd>${mil(g('tstl'))}</dd>
      <dt>TAPONES</dt><dd>${mil(g('tblk'))}</dd>
    </dl></div>

    <div class="card"><h4>PALMARÉS</h4><dl class="kv">
      <dt>ANILLOS</dt><dd>${g('ring')}${g('best')?` <small>(${g('best')} como mejor de su equipo)</small>`:''}</dd>
      <dt>FINALS MVP</dt><dd>${g('fmvp')}</dd>
      <dt>MVP</dt><dd>${g('mvp')} <small>(${nf(g('mvps_v'),2)} en cuota de votos acumulada)</small></dd>
      <dt>DPOY</dt><dd>${g('dpoy')}</dd>
      <dt>ALL-NBA</dt><dd>${nf(g('anba'))} pts <small>(1º=5 · 2º=3 · 3º=1,5)</small></dd>
      <dt>ALL-DEF.</dt><dd>${nf(g('adef'))} pts <small>(1º=3 · 2º=1,5)</small></dd>
      <dt>ALL-STAR</dt><dd>${g('ast')}</dd>
    </dl></div>

    <div class="card"><h4>FUERZA POR BLOQUE</h4>${blocks}
      <p class="pnote">Desviaciones típicas sobre la media de los ${P.length.toLocaleString('es-ES')} jugadores medibles. 0 = jugador medio del grupo · +2 = mejor que el 97,7%.
      ${g('cov')<0.75?'<br><b>Datos parciales:</b> su época no registraba parte de las métricas del modelo, así que estos bloques descansan sobre menos indicadores.':''}</p>
    </div>

    <div class="card" style="grid-column:1/-1"><h4>SUS TRES MEJORES TEMPORADAS</h4>
      <table class="seas"><thead><tr><th>AÑO</th><th>EQUIPO</th><th>PTS</th><th>REB</th><th>AST</th><th>PER</th><th>WS/48</th><th>BPM</th></tr></thead>
      <tbody>${seas||'<tr><td colspan="8">—</td></tr>'}</tbody></table>
      <p class="pnote">Ordenadas por un compuesto de producción, eficiencia, impacto y defensa medido en z-score de su propio año, no por puntos.</p>
    </div>

  </div></td></tr>`;
}

/* ---------- glosario ---------- */
$('#glosario').innerHTML=`<h2>Qué es exactamente cada cosa</h2>
<p class="lead">Los colores son los mismos en los cuadraditos de los pesos y en la barra de cada jugador, así que la barra se lee directamente como el reparto de su puntuación.</p>
<h3>LOS SIETE BLOQUES</h3><dl class="gl">
${BLOCKS.map(b=>`<dt><span class="dot" style="background:${b.c}"></span>${b.n}</dt><dd>${TIP[b.k]}.<em>${b.d}% en la ponderación base</em></dd>`).join('')}
</dl>
<h3>LAS MÉTRICAS QUE HAY DENTRO</h3><dl class="gl">
<dt>z-score</dt><dd>Cuántas desviaciones típicas por encima o por debajo está el jugador respecto a la media de los jugadores cualificados <b>de esa misma temporada</b>. 0 es un jugador medio de su año; +2 significa mejor que el 97,7% de sus contemporáneos. Es el mecanismo que permite comparar 1962 con 2026. Se recorta a ±4.</dd>
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
<dt>Quién entra</dt><dd>Los ${P.length.toLocaleString('es-ES')} jugadores con al menos una temporada de 1.000+ minutos. Por debajo de eso el modelo no tiene nada que medir.</dd>
</dl>`;

/* ---------- arranque ---------- */
buildControls();
scored=score(); scored.forEach(o=>baseRank[get(o.p,'n')]=o.rk);
syncP(); recalc();
$('#ts').textContent='Índice generado a partir de datos hasta la temporada 2025-26. Última compilación: '+new Date().toLocaleDateString('es-ES',{year:'numeric',month:'long',day:'numeric'})+'.';
