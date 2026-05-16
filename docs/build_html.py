import json, os

with open(r'C:\temp\velvet-sojourner\repos\_SCAN_ALL_RESULTS.json', 'r') as f:
    data = json.load(f)

repos = data['repos']

out = []
for r in repos:
    out.append({
        'n': r['name'],
        'd': (r.get('description') or '')[:200],
        's': r.get('size_mb', 0),
        'f': r.get('file_count', 0),
        'sc': r.get('score', 0),
        'l': r.get('languages', []),
        't': r.get('tier', 'C'),
        'hr': r.get('has_readme', False),
        'rl': r.get('readme_length', 0),
        'ht': r.get('has_tests', False),
        'hd': r.get('has_dockerfile', False) or r.get('has_docker_compose', False),
        'hl': r.get('has_license', False),
        'ic': r.get('is_likely_clone', False),
        'ct': r.get('clone_type', ''),
        'ex': dict(sorted(r.get('extensions', {}).items(), key=lambda x: -x[1])[:15]),
        'tf': r.get('top_files', [])[:20]
    })

js = json.dumps(out, separators=(',', ':'))

# Build the complete HTML
html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AgentForge Repo Browser</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d1b2a;--bg2:#1b2d45;--bg3:#243b55;--fg:#e0e6ed;--fg2:#8899aa;--accent:#00d4aa;--accent2:#00a887;--border:#2a4060;--card:#152238;--radius:8px;--shadow:0 2px 12px rgba(0,0,0,.3)}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,Ubuntu,sans-serif;background:var(--bg);color:var(--fg);min-height:100vh;padding:20px}
.container{max-width:1400px;margin:0 auto}
h1{font-size:1.5rem;font-weight:700;color:var(--accent);margin-bottom:4px;display:flex;align-items:center;gap:10px}
h1 span{font-size:.9rem;font-weight:400;color:var(--fg2)}
.subtitle{color:var(--fg2);font-size:.85rem;margin-bottom:20px}
.controls{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:16px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.controls .search-wrap{flex:1 1 280px;position:relative}
.controls .search-wrap input{width:100%;padding:10px 14px 10px 36px;border:1px solid var(--border);border-radius:6px;background:var(--bg2);color:var(--fg);font-size:.9rem;outline:none;transition:border-color .2s}
.controls .search-wrap input:focus{border-color:var(--accent)}
.controls .search-wrap::before{content:'\1F50D';position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:.85rem;opacity:.5}
.controls select{padding:8px 10px;border:1px solid var(--border);border-radius:6px;background:var(--bg2);color:var(--fg);font-size:.82rem;outline:none;cursor:pointer;min-width:110px}
.controls select:focus{border-color:var(--accent)}
.controls .count{color:var(--fg2);font-size:.85rem;white-space:nowrap;margin-left:auto;padding:0 8px}
.controls .count strong{color:var(--accent)}
.stats{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.stat{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:10px 16px;font-size:.82rem;flex:1;min-width:100px}
.stat .num{font-size:1.2rem;font-weight:700;color:var(--accent);display:block}
.stat .lbl{color:var(--fg2);font-size:.75rem;text-transform:uppercase;letter-spacing:.5px}
.table-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:var(--radius);background:var(--card)}
table{width:100%;border-collapse:collapse;font-size:.82rem;min-width:800px}
thead{background:var(--bg2);position:sticky;top:0}
th{padding:10px 12px;text-align:left;font-weight:600;color:var(--fg2);font-size:.75rem;text-transform:uppercase;letter-spacing:.5px;cursor:pointer;white-space:nowrap;user-select:none;border-bottom:2px solid var(--border)}
th:hover{color:var(--accent)}
th .sort-icon{opacity:.4;margin-left:4px}
th.sorted .sort-icon{opacity:1;color:var(--accent)}
td{padding:8px 12px;border-bottom:1px solid var(--border);vertical-align:middle;color:var(--fg)}
tr:hover td{background:rgba(0,212,170,.04)}
tr:last-child td{border-bottom:none}
td.name{font-weight:600;color:var(--accent);cursor:pointer;white-space:nowrap}
td.name:hover{text-decoration:underline}
td.desc{max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--fg2);font-size:.78rem}
td.lang{font-size:.78rem}
td.size,td.files,td.score{white-space:nowrap;text-align:right;font-variant-numeric:tabular-nums}
td.score{font-weight:600}
td.tier{text-align:center}
.tier-A{color:#00d4aa;font-weight:700}
.tier-B{color:#ffb347;font-weight:600}
.tier-C{color:#8899aa}
.badge{display:inline-block;padding:1px 7px;border-radius:4px;font-size:.7rem;font-weight:600;white-space:nowrap}
.badge-yes{background:rgba(0,212,170,.15);color:var(--accent)}
.badge-no{background:rgba(255,255,255,.06);color:var(--fg2)}
.badge-readme{font-size:.7rem;padding:1px 6px;border-radius:4px}
.r-excellent{background:rgba(0,212,170,.2);color:var(--accent)}
.r-good{background:rgba(0,200,255,.15);color:#4fc3f7}
.r-poor{background:rgba(255,183,71,.15);color:#ffb347}
.r-none{background:rgba(255,255,255,.06);color:var(--fg2)}
.detail-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:100;justify-content:center;align-items:flex-start;padding:40px 20px;overflow-y:auto}
.detail-overlay.open{display:flex}
.detail-panel{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);max-width:700px;width:100%;padding:28px;position:relative;margin:auto 0;box-shadow:0 8px 40px rgba(0,0,0,.5)}
.detail-panel .close{position:absolute;top:12px;right:16px;background:none;border:none;color:var(--fg2);font-size:1.5rem;cursor:pointer;line-height:1}
.detail-panel .close:hover{color:var(--fg)}
.detail-panel h2{font-size:1.2rem;margin-bottom:16px;color:var(--accent);word-break:break-all}
.detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px 24px}
.detail-grid .field{margin-bottom:4px}
.detail-grid .field .label{font-size:.72rem;text-transform:uppercase;letter-spacing:.5px;color:var(--fg2);margin-bottom:2px}
.detail-grid .field .value{font-size:.9rem;color:var(--fg);word-break:break-word}
.detail-grid .full{grid-column:1/-1}
.detail-grid .field .value.lang-list{display:flex;flex-wrap:wrap;gap:4px}
.detail-grid .field .value .lang-tag{background:var(--bg2);padding:2px 8px;border-radius:4px;font-size:.78rem;color:var(--accent)}
.ext-list{background:var(--bg2);padding:8px 12px;border-radius:6px;font-size:.8rem;max-height:120px;overflow-y:auto}
.ext-list span{display:inline-block;margin:2px 6px 2px 0;color:var(--fg2)}
.top-files{background:var(--bg2);padding:8px 12px;border-radius:6px;font-size:.8rem;max-height:120px;overflow-y:auto;color:var(--fg2)}
.no-results{text-align:center;padding:40px 20px;color:var(--fg2);font-size:.9rem}
@media(max-width:768px){
body{padding:12px}
.controls{gap:8px}
.controls select{min-width:90px;font-size:.75rem;flex:1}
.detail-grid{grid-template-columns:1fr}
.detail-panel{padding:20px}
th,td{font-size:.75rem;padding:6px 8px}
td.desc{max-width:120px}
}
</style>
</head>
<body>
<div class="container">
<h1>AgentForge Repo Browser <span id="totalLabel"></span></h1>
<div class="subtitle">Browse and search all 843 repositories in the collection</div>

<div class="stats" id="statsBar"></div>

<div class="controls">
<div class="search-wrap"><input type="text" id="searchInput" placeholder="Search repos..." autofocus></div>
<select id="filterTier"><option value="">All Tiers</option></select>
<select id="filterLang"><option value="">All Languages</option></select>
<select id="filterTests"><option value="">Tests: Any</option><option value="1">Has Tests</option><option value="0">No Tests</option></select>
<select id="filterDocker"><option value="">Docker: Any</option><option value="1">Has Docker</option><option value="0">No Docker</option></select>
<select id="filterLicense"><option value="">License: Any</option><option value="1">Has License</option><option value="0">No License</option></select>
<select id="filterReadme"><option value="">README: Any</option><option value="excellent">Excellent</option><option value="good">Good</option><option value="poor">Poor</option><option value="none">None</option></select>
<div class="count" id="resultCount">0 repos</div>
</div>

<div class="table-wrap">
<table><thead><tr id="headerRow"></tr></thead><tbody id="tableBody"></tbody></table>
</div>
<div class="no-results" id="noResults" style="display:none">No repos match your filters.</div>
</div>

<div class="detail-overlay" id="detailOverlay"><div class="detail-panel"><button class="close" id="detailClose">&times;</button><h2 id="detailName"></h2><div class="detail-grid" id="detailGrid"></div></div></div>

<script>
const REPOS = ''' + js + ''';

const ALL = REPOS;

function $(id){return document.getElementById(id)}
function qs(s){return document.querySelector(s)}
function qsa(s){return document.querySelectorAll(s)}
function ce(t){return document.createElement(t)}

const allLangs = new Set();
ALL.forEach(function(r){(r.l||[]).forEach(function(l){allLangs.add(l)})});
const sortedLangs = Array.from(allLangs).sort();
const tiers = ['A','B','C'];

var tierSel = $('filterTier');
tiers.forEach(function(t){var o=ce('option');o.value=t;o.textContent='Tier '+t;tierSel.appendChild(o)});
var langSel = $('filterLang');
sortedLangs.forEach(function(l){var o=ce('option');o.value=l;o.textContent=l;langSel.appendChild(o)});

function readmeQuality(r){
  if(!r.hr) return 'none';
  if(r.rl > 5000) return 'excellent';
  if(r.rl > 500) return 'good';
  return 'poor';
}

function formatSize(mb){
  if(mb < 0.1) return '<0.1';
  if(mb < 10) return mb.toFixed(1);
  return Math.round(mb)+'';
}

function escapeHtml(s){
  if(!s) return '';
  var d = ce('div');
  d.textContent = String(s).slice(0,200);
  return d.innerHTML;
}

var currentSort = {col:'sc', dir:-1};
var currentData = [];

function filterData(){
  var q = $('searchInput').value.toLowerCase().trim();
  var tier = $('filterTier').value;
  var lang = $('filterLang').value;
  var tests = $('filterTests').value;
  var docker = $('filterDocker').value;
  var lic = $('filterLicense').value;
  var rq = $('filterReadme').value;

  currentData = [];
  for(var i=0;i<ALL.length;i++){
    var r = ALL[i];
    if(q){
      var inName = r.n.toLowerCase().indexOf(q) !== -1;
      var inDesc = (r.d||'').toLowerCase().indexOf(q) !== -1;
      var inLang = false;
      for(var j=0;j<(r.l||[]).length;j++){if(r.l[j].toLowerCase().indexOf(q)!==-1){inLang=true;break}}
      var inTier = r.t.toLowerCase().indexOf(q) !== -1;
      if(!inName && !inDesc && !inLang && !inTier) continue;
    }
    if(tier && r.t !== tier) continue;
    if(lang && (r.l||[]).indexOf(lang) === -1) continue;
    if(tests === '1' && !r.ht) continue;
    if(tests === '0' && r.ht) continue;
    if(docker === '1' && !r.hd) continue;
    if(docker === '0' && r.hd) continue;
    if(lic === '1' && !r.hl) continue;
    if(lic === '0' && r.hl) continue;
    if(rq && readmeQuality(r) !== rq) continue;
    currentData.push(r);
  }
  sortData();
}

function sortData(){
  var col = currentSort.col;
  var dir = currentSort.dir;
  currentData.sort(function(a,b){
    var va, vb;
    switch(col){
      case 'n': va=a.n.toLowerCase(); vb=b.n.toLowerCase(); return dir * (va < vb ? -1 : va > vb ? 1 : 0);
      case 's': return dir * (a.s - b.s);
      case 'f': return dir * (a.f - b.f);
      case 'sc': return dir * (a.sc - b.sc);
      case 't': return dir * (a.t < b.t ? -1 : a.t > b.t ? 1 : 0);
      default: return dir * (a.sc - b.sc);
    }
  });
  renderTable();
}

function renderTable(){
  var tbody = $('tableBody');
  var noRes = $('noResults');
  var countEl = $('resultCount');
  tbody.innerHTML = '';

  if(!currentData.length){
    noRes.style.display = 'block';
    countEl.textContent = '0 repos';
    return;
  }
  noRes.style.display = 'none';
  countEl.textContent = currentData.length + ' repo' + (currentData.length===1?'':'s');

  var html = '';
  for(var i=0;i<currentData.length;i++){
    var r = currentData[i];
    var rq = readmeQuality(r);
    var safeName = escapeHtml(r.n);
    var safeDesc = escapeHtml(r.d);
    var langStr = escapeHtml((r.l||[]).join(', '));
    var rqLabel = rq.charAt(0).toUpperCase() + rq.slice(1);
    html += '<tr>' +
      '<td class="name" onclick="showDetail(\'' + r.n.replace(/'/g,"\\'") + '\')">' + safeName + '</td>' +
      '<td class="desc">' + safeDesc + '</td>' +
      '<td class="size">' + formatSize(r.s) + ' MB</td>' +
      '<td class="files">' + r.f + '</td>' +
      '<td class="score">' + r.sc + '</td>' +
      '<td class="lang">' + langStr + '</td>' +
      '<td class="tier"><span class="tier-' + r.t + '">' + r.t + '</span></td>' +
      '<td><span class="badge-readme r-' + rq + '">' + rqLabel + '</span></td>' +
      '<td><span class="badge ' + (r.ht?'badge-yes':'badge-no') + '">' + (r.ht?'Yes':'No') + '</span></td>' +
      '<td><span class="badge ' + (r.hd?'badge-yes':'badge-no') + '">' + (r.hd?'Yes':'No') + '</span></td>' +
      '<td><span class="badge ' + (r.hl?'badge-yes':'badge-no') + '">' + (r.hl?'Yes':'No') + '</span></td>' +
      '</tr>';
  }
  tbody.innerHTML = html;
  updateSortIcons();
}

function updateSortIcons(){
  var ths = qsa('th');
  for(var i=0;i<ths.length;i++) ths[i].classList.remove('sorted');
  var col = currentSort.col;
  var colMap = {n:0, s:1, f:2, sc:3, t:4};
  var idx = colMap[col];
  if(idx !== undefined && ths[idx]) ths[idx].classList.add('sorted');
}

function setSort(col){
  if(currentSort.col === col) currentSort.dir *= -1;
  else { currentSort.col = col; currentSort.dir = -1; }
  sortData();
}

function showDetail(name){
  var r = null;
  for(var i=0;i<ALL.length;i++){if(ALL[i].n===name){r=ALL[i];break}}
  if(!r) return;

  $('detailName').textContent = r.n;
  var grid = $('detailGrid');
  var rq = readmeQuality(r);
  var rqLabel = rq.charAt(0).toUpperCase() + rq.slice(1);

  var exts = r.ex || {};
  var extHtml = '';
  var extKeys = Object.keys(exts);
  for(var i=0;i<extKeys.length;i++){
    extHtml += '<span>' + escapeHtml(extKeys[i]) + ': ' + exts[extKeys[i]] + '</span>';
  }

  var tfHtml = '';
  var tfs = r.tf || [];
  for(var i=0;i<tfs.length;i++){
    tfHtml += '<div>' + escapeHtml(tfs[i]) + '</div>';
  }

  var langHtml = '';
  var langs = r.l || [];
  for(var i=0;i<langs.length;i++){
    langHtml += '<span class="lang-tag">' + escapeHtml(langs[i]) + '</span>';
  }

  var cloneInfo = r.ic ? 'Yes (' + escapeHtml(r.ct) + ')' : 'No';

  grid.innerHTML =
    '<div class="field"><div class="label">Tier</div><div class="value"><span class="tier-' + r.t + '">' + r.t + '</span></div></div>' +
    '<div class="field"><div class="label">Score</div><div class="value">' + r.sc + '</div></div>' +
    '<div class="field"><div class="label">Size</div><div class="value">' + r.s.toFixed(1) + ' MB</div></div>' +
    '<div class="field"><div class="label">Files</div><div class="value">' + r.f + '</div></div>' +
    '<div class="field"><div class="label">README</div><div class="value"><span class="badge-readme r-' + rq + '">' + rqLabel + '</span> (' + r.rl + ' chars)</div></div>' +
    '<div class="field"><div class="label">Tests</div><div class="value"><span class="badge ' + (r.ht?'badge-yes':'badge-no') + '">' + (r.ht?'Yes':'No') + '</span></div></div>' +
    '<div class="field"><div class="label">Docker</div><div class="value"><span class="badge ' + (r.hd?'badge-yes':'badge-no') + '">' + (r.hd?'Yes':'No') + '</span></div></div>' +
    '<div class="field"><div class="label">License</div><div class="value"><span class="badge ' + (r.hl?'badge-yes':'badge-no') + '">' + (r.hl?'Yes':'No') + '</span></div></div>' +
    '<div class="field"><div class="label">Clone</div><div class="value"><span class="badge ' + (r.ic?'badge-yes':'badge-no') + '">' + cloneInfo + '</span></div></div>' +
    (langs.length ? '<div class="field full"><div class="label">Languages</div><div class="value lang-list">' + langHtml + '</div></div>' : '') +
    (r.d ? '<div class="field full"><div class="label">Description</div><div class="value">' + escapeHtml(r.d) + '</div></div>' : '') +
    (extHtml ? '<div class="field full"><div class="label">Extensions (top 15)</div><div class="ext-list">' + extHtml + '</div></div>' : '') +
    (tfHtml ? '<div class="field full"><div class="label">Top Files</div><div class="top-files">' + tfHtml + '</div></div>' : '');

  $('detailOverlay').classList.add('open');
}

function buildStats(){
  var total = ALL.length;
  var aTier = 0, bTier = 0, withTests = 0, withDocker = 0, withLicense = 0, clones = 0;
  var totalSize = 0;
  for(var i=0;i<ALL.length;i++){
    var r = ALL[i];
    if(r.t === 'A') aTier++;
    if(r.t === 'B') bTier++;
    if(r.ht) withTests++;
    if(r.hd) withDocker++;
    if(r.hl) withLicense++;
    if(r.ic) clones++;
    totalSize += r.s;
  }
  $('statsBar').innerHTML =
    '<div class="stat"><span class="num">' + total + '</span><span class="lbl">Total Repos</span></div>' +
    '<div class="stat"><span class="num">' + aTier + '</span><span class="lbl">A Tier</span></div>' +
    '<div class="stat"><span class="num">' + bTier + '</span><span class="lbl">B Tier</span></div>' +
    '<div class="stat"><span class="num">' + withTests + '</span><span class="lbl">With Tests</span></div>' +
    '<div class="stat"><span class="num">' + withDocker + '</span><span class="lbl">With Docker</span></div>' +
    '<div class="stat"><span class="num">' + withLicense + '</span><span class="lbl">With License</span></div>' +
    '<div class="stat"><span class="num">' + clones + '</span><span class="lbl">Clones</span></div>' +
    '<div class="stat"><span class="num">' + Math.round(totalSize) + '</span><span class="lbl">Total MB</span></div>';
  $('totalLabel').textContent = '(' + total + ' repos, ' + (aTier+bTier) + ' active)';
}

function initTable(){
  var labels = ['Name','Description','Size','Files','Score','Languages','Tier','README','Tests','Docker','License'];
  var sortCols = ['n', null, 's', 'f', 'sc', null, 't', null, null, null, null];
  var header = $('headerRow');
  for(var i=0;i<labels.length;i++){
    var th = ce('th');
    if(sortCols[i]){
      th.innerHTML = labels[i] + ' <span class="sort-icon">\u25B2</span>';
      th.onclick = (function(col){return function(){setSort(col)}})(sortCols[i]);
      if(sortCols[i] === 'sc') th.classList.add('sorted');
    } else {
      th.textContent = labels[i];
    }
    header.appendChild(th);
  }
}

$('searchInput').addEventListener('input', filterData);
$('filterTier').addEventListener('change', filterData);
$('filterLang').addEventListener('change', filterData);
$('filterTests').addEventListener('change', filterData);
$('filterDocker').addEventListener('change', filterData);
$('filterLicense').addEventListener('change', filterData);
$('filterReadme').addEventListener('change', filterData);

$('detailClose').addEventListener('click', function(){ $('detailOverlay').classList.remove('open') });
$('detailOverlay').addEventListener('click', function(e){ if(e.target === this) this.classList.remove('open') });
document.addEventListener('keydown', function(e){ if(e.key === 'Escape') $('detailOverlay').classList.remove('open') });

buildStats();
initTable();
filterData();
</script></body></html>'''

with open(r'C:\temp\velvet-sojourner\docs\repo-browser.html', 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(r'C:\temp\velvet-sojourner\docs\repo-browser.html')
print('Done. File size: %d bytes (%.1f KB)' % (size, size/1024))
