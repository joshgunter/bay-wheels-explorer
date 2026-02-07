"""
Build the complete Bay Wheels dashboard HTML with embedded data.

Usage:
    python scripts/build_dashboard.py
    python scripts/build_dashboard.py --input ./dashboard_data.json --output ./index.html
"""
import json
import argparse

parser = argparse.ArgumentParser(description='Build Bay Wheels dashboard HTML')
parser.add_argument('--input', default='./dashboard_data.json', help='Input JSON data path')
parser.add_argument('--output', default='./index.html', help='Output HTML path')
args = parser.parse_args()

with open(args.input) as f:
    data = json.load(f)

data_json = json.dumps(data, separators=(',', ':'))

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bay Wheels Explorer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#0a0e1a;--card:#111827;--card2:#1a2236;--border:#1e293b;--text:#e2e8f0;--text2:#94a3b8;--accent:#0077C8;--accent2:#00BFA5;--red:#ef4444;--green:#22c55e;--yellow:#eab308}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden}}
.hero{{background:linear-gradient(135deg,#0a0e1a 0%,#0f172a 50%,#1e1b4b 100%);padding:40px 24px 24px;text-align:center;border-bottom:1px solid var(--border)}}
.hero h1{{font-size:2.4rem;font-weight:800;background:linear-gradient(135deg,#60a5fa,#00BFA5);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:6px;display:flex;align-items:center;justify-content:center;gap:12px}}
.hero h1 .icon{{font-size:2rem;-webkit-text-fill-color:#60a5fa}}
.hero .sub{{color:var(--text2);font-size:.95rem;margin-bottom:20px;font-weight:300}}
.stats-row{{display:flex;justify-content:center;gap:16px;flex-wrap:wrap}}
.stat-badge{{background:rgba(255,255,255,.05);border:1px solid var(--border);border-radius:12px;padding:12px 20px;text-align:center;min-width:130px}}
.stat-badge .val{{font-size:1.3rem;font-weight:700;color:#60a5fa}}
.stat-badge .lbl{{font-size:.7rem;color:var(--text2);text-transform:uppercase;letter-spacing:.5px;margin-top:2px}}
.tabs{{display:flex;justify-content:center;gap:4px;padding:12px 24px;background:var(--card);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:1000}}
.tab{{padding:10px 20px;border-radius:8px;cursor:pointer;font-size:.85rem;font-weight:500;color:var(--text2);transition:all .2s;border:none;background:none}}
.tab:hover{{color:var(--text);background:rgba(255,255,255,.05)}}
.tab.active{{background:var(--accent);color:#fff}}
.content{{max-width:1400px;margin:0 auto;padding:24px}}
.panel{{display:none}}.panel.active{{display:block}}
.grid{{display:grid;gap:20px}}.grid-2{{grid-template-columns:1fr 1fr}}.grid-3{{grid-template-columns:1fr 1fr 1fr}}
@media(max-width:900px){{.grid-2,.grid-3{{grid-template-columns:1fr}}.stats-row{{gap:8px}}.stat-badge{{min-width:100px;padding:8px 12px}}.hero h1{{font-size:1.6rem}}.tabs{{overflow-x:auto;justify-content:flex-start}}}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px;position:relative;overflow:hidden}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(96,165,250,.3),transparent)}}
.card h3{{font-size:.85rem;color:var(--text2);text-transform:uppercase;letter-spacing:.5px;margin-bottom:16px;font-weight:600}}
.chart-container{{position:relative;width:100%;height:300px}}
.chart-container.tall{{height:400px}}
.toggle-row{{display:flex;gap:6px;margin-bottom:12px}}
.toggle-btn{{padding:4px 12px;border-radius:6px;font-size:.75rem;cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--text2);transition:all .15s}}
.toggle-btn.active{{background:var(--accent);border-color:var(--accent);color:#fff}}
.insight-card{{background:linear-gradient(135deg,rgba(96,165,250,.08),rgba(0,191,165,.05));border:1px solid rgba(96,165,250,.15);border-radius:12px;padding:16px;margin-bottom:12px}}
.insight-card .num{{font-size:1.4rem;font-weight:700;color:#60a5fa}}.insight-card .desc{{font-size:.85rem;color:var(--text2);margin-top:4px}}
#map{{width:100%;height:600px;border-radius:12px;border:1px solid var(--border)}}
.map-controls{{display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap;align-items:center}}
.map-controls input,.map-controls select{{background:var(--card2);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:.85rem;font-family:inherit}}
.map-controls input{{flex:1;min-width:200px}}.map-controls select{{min-width:160px}}
.map-legend{{display:flex;gap:16px;margin-top:12px;justify-content:center;font-size:.75rem;color:var(--text2)}}
.map-legend span{{display:flex;align-items:center;gap:4px}}
.map-legend .dot{{width:10px;height:10px;border-radius:50%;display:inline-block}}
table{{width:100%;border-collapse:collapse;font-size:.82rem}}
th{{text-align:left;padding:10px 12px;border-bottom:2px solid var(--border);color:var(--text2);font-weight:600;cursor:pointer;white-space:nowrap;text-transform:uppercase;font-size:.7rem;letter-spacing:.5px;user-select:none}}
th:hover{{color:var(--text)}}
td{{padding:8px 12px;border-bottom:1px solid rgba(255,255,255,.04)}}
tr:hover td{{background:rgba(255,255,255,.02)}}
.search-box{{width:100%;background:var(--card2);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:10px 14px;font-size:.85rem;margin-bottom:16px;font-family:inherit}}
.page-controls{{display:flex;justify-content:center;gap:8px;margin-top:16px;align-items:center}}
.page-btn{{padding:6px 14px;border-radius:6px;border:1px solid var(--border);background:var(--card2);color:var(--text);cursor:pointer;font-size:.8rem;font-family:inherit}}
.page-btn.active{{background:var(--accent);border-color:var(--accent)}}
.page-btn:disabled{{opacity:.3;cursor:not-allowed}}
.mini-bar{{height:6px;border-radius:3px;background:var(--card2);overflow:hidden;min-width:80px}}
.mini-bar-fill{{height:100%;border-radius:3px}}
.flow-indicator{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.75rem;font-weight:600}}
.flow-pos{{background:rgba(34,197,94,.15);color:#22c55e}}
.flow-neg{{background:rgba(239,68,68,.15);color:#ef4444}}
.flow-neutral{{background:rgba(255,255,255,.05);color:var(--text2)}}
.station-detail{{background:var(--card2);border:1px solid var(--border);border-radius:12px;padding:20px;margin-top:16px}}
.station-detail h4{{color:#60a5fa;font-size:1rem;margin-bottom:12px}}
.route-arrow{{color:var(--accent2);font-weight:700;padding:0 8px}}
.sort-icon{{opacity:.3;font-size:.7rem;margin-left:4px}}
th.sorted .sort-icon{{opacity:1;color:var(--accent)}}
.loading{{display:flex;justify-content:center;align-items:center;height:200px;color:var(--text2)}}
</style>
</head>
<body>
<div class="hero">
<h1><span class="icon">\U0001F6B2</span> Bay Wheels Explorer</h1>
<p class="sub" id="heroSub"></p>
<div class="stats-row" id="heroStats"></div>
</div>
<nav class="tabs" id="tabs">
<button class="tab active" data-tab="overview">Overview</button>
<button class="tab" data-tab="map">Station Map</button>
<button class="tab" data-tab="rankings">Station Rankings</button>
<button class="tab" data-tab="routes">Top Routes</button>
<button class="tab" data-tab="time">Time Patterns</button>
</nav>
<div class="content">

<!-- OVERVIEW -->
<div class="panel active" id="panel-overview">
<div class="grid grid-2" style="margin-bottom:20px">
<div class="card"><h3>Yearly Growth</h3><div class="chart-container"><canvas id="yearlyChart"></canvas></div></div>
<div class="card"><h3>Bike Type Breakdown</h3><div class="chart-container"><canvas id="bikeChart"></canvas></div></div>
</div>
<div class="card" style="margin-bottom:20px">
<h3>Monthly Trip Volume</h3>
<div class="toggle-row" id="monthlyToggles">
<button class="toggle-btn active" data-mode="total">Total</button>
<button class="toggle-btn" data-mode="members">Members</button>
<button class="toggle-btn" data-mode="casual">Casual</button>
<button class="toggle-btn" data-mode="split">Members vs Casual</button>
</div>
<div class="chart-container tall"><canvas id="monthlyChart"></canvas></div>
</div>
<div class="grid grid-3" id="insights"></div>
</div>

<!-- MAP -->
<div class="panel" id="panel-map">
<div class="card">
<h3>Station Network Map</h3>
<div class="map-controls">
<input type="text" id="mapSearch" placeholder="Search stations...">
<select id="mapColor">
<option value="flow">Color by Net Flow</option>
<option value="activity">Color by Total Activity</option>
<option value="member">Color by Member %</option>
</select>
</div>
<div id="map"></div>
<div class="map-legend" id="mapLegend"></div>
</div>
</div>

<!-- RANKINGS -->
<div class="panel" id="panel-rankings">
<div class="card">
<h3>All Stations \u2014 Performance Rankings</h3>
<input type="text" class="search-box" id="stationSearch" placeholder="Search stations by name...">
<div style="overflow-x:auto"><table id="stationTable"><thead><tr>
<th data-col="rank"># <span class="sort-icon">\u25B2</span></th>
<th data-col="station_name">Station <span class="sort-icon">\u25B2</span></th>
<th data-col="total_activity">Activity <span class="sort-icon">\u25B2</span></th>
<th data-col="total_departures">Depart <span class="sort-icon">\u25B2</span></th>
<th data-col="total_arrivals">Arrive <span class="sort-icon">\u25B2</span></th>
<th data-col="net_flow">Net Flow <span class="sort-icon">\u25B2</span></th>
<th data-col="avg_duration_depart">Avg Duration <span class="sort-icon">\u25B2</span></th>
<th data-col="subscriber_pct">Member % <span class="sort-icon">\u25B2</span></th>
</tr></thead><tbody id="stationBody"></tbody></table></div>
<div class="page-controls" id="stationPages"></div>
</div>
<div id="stationDetail"></div>
</div>

<!-- ROUTES -->
<div class="panel" id="panel-routes">
<div class="card">
<h3>Top 100 Most Popular Routes</h3>
<input type="text" class="search-box" id="routeSearch" placeholder="Search routes by station name...">
<div style="overflow-x:auto"><table id="routeTable"><thead><tr>
<th data-col="rank"># <span class="sort-icon">\u25B2</span></th>
<th data-col="start">From <span class="sort-icon">\u25B2</span></th>
<th data-col="end">To <span class="sort-icon">\u25B2</span></th>
<th data-col="count">Trips <span class="sort-icon">\u25B2</span></th>
<th data-col="dur">Avg Duration <span class="sort-icon">\u25B2</span></th>
</tr></thead><tbody id="routeBody"></tbody></table></div>
</div>
</div>

<!-- TIME PATTERNS -->
<div class="panel" id="panel-time">
<div class="grid grid-2">
<div class="card">
<h3>Hourly Distribution</h3>
<div class="toggle-row" id="hourlyToggles">
<button class="toggle-btn active" data-mode="count">Trip Count</button>
<button class="toggle-btn" data-mode="duration">Avg Duration</button>
</div>
<div class="chart-container tall"><canvas id="hourlyChart"></canvas></div>
</div>
<div class="card">
<h3>Day of Week</h3>
<div class="toggle-row" id="dowToggles">
<button class="toggle-btn active" data-mode="count">Trip Count</button>
<button class="toggle-btn" data-mode="duration">Avg Duration</button>
</div>
<div class="chart-container tall"><canvas id="dowChart"></canvas></div>
</div>
</div>
</div>

</div>

<div style="text-align:center;padding:40px;color:var(--text2);font-size:.75rem;border-top:1px solid var(--border);margin-top:40px">
Data source: Lyft Bay Wheels open data \u2022 {data['summary']['total_trips']:,} trips analyzed \u2022 {data['summary']['date_range_start']} to {data['summary']['date_range_end']}
</div>

<script>
const DATA = {data_json};

// ===================== UTILITIES =====================
const fmt = n => n == null ? '\u2014' : n.toLocaleString();
const fmtDur = s => {{ const m = Math.floor(s/60); const sec = Math.round(s%60); return m + 'm ' + sec + 's'; }};
const fmtPct = p => p.toFixed(1) + '%';

// ===================== HERO STATS =====================
(function(){{
const s = DATA.summary;
const tripM = (s.total_trips / 1e6).toFixed(1);
document.getElementById('heroSub').textContent = 'Interactive analysis of ' + tripM + 'M+ rides across the San Francisco Bay Area \u2022 ' + s.date_range_start.slice(0,7).replace('-',' ') + ' \u2013 ' + s.date_range_end.slice(0,7).replace('-',' ');
const el = document.getElementById('heroStats');
const items = [
  ['Total Trips', fmt(s.total_trips)],
  ['Date Range', s.date_range_start.slice(0,7) + ' \u2013 ' + s.date_range_end.slice(0,7)],
  ['Active Stations', fmt(s.total_stations)],
  ['Member Rides', fmtPct(s.subscriber_pct)],
];
el.innerHTML = items.map(([l,v]) => `<div class="stat-badge"><div class="val">${{v}}</div><div class="lbl">${{l}}</div></div>`).join('');
}})();

// ===================== TAB SWITCHING =====================
let map = null, mapInitialized = false;
document.querySelectorAll('.tab').forEach(t => {{
  t.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById('panel-' + t.dataset.tab).classList.add('active');
    if (t.dataset.tab === 'map' && !mapInitialized) {{ initMap(); mapInitialized = true; }}
  }});
}});

// ===================== CHART DEFAULTS =====================
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = 'Inter';
Chart.defaults.plugins.tooltip.backgroundColor = '#1e293b';
Chart.defaults.plugins.tooltip.borderColor = '#334155';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.padding = 12;

// ===================== YEARLY CHART =====================
(function(){{
const y = DATA.yearly.filter(d => d.year >= 2017 && d.year <= 2025);
new Chart(document.getElementById('yearlyChart'), {{
  type: 'bar',
  data: {{
    labels: y.map(d => d.year),
    datasets: [{{
      label: 'Total Trips',
      data: y.map(d => d.total_trips),
      backgroundColor: y.map((_,i) => {{
        const t = i / (y.length - 1);
        return `rgba(${{Math.round(96 - t*40)}}, ${{Math.round(165 + t*30)}}, ${{Math.round(250 - t*80)}}, 0.8)`;
      }}),
      borderRadius: 6,
      borderSkipped: false,
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: c => fmt(c.raw) + ' trips' }} }}
    }},
    scales: {{
      y: {{ ticks: {{ callback: v => (v/1e6).toFixed(1) + 'M' }}, grid: {{ color: 'rgba(255,255,255,0.04)' }} }},
      x: {{ grid: {{ display: false }} }}
    }}
  }}
}});
}})();

// ===================== BIKE TYPE CHART =====================
(function(){{
const bt = DATA.bike_type.filter(d => d.total_trips > 100);
const colors = ['#60a5fa','#00BFA5','#f59e0b','#ef4444'];
new Chart(document.getElementById('bikeChart'), {{
  type: 'doughnut',
  data: {{
    labels: bt.map(d => d.rideable_type.replace('_',' ').replace(/\\b\\w/g,l=>l.toUpperCase())),
    datasets: [{{ data: bt.map(d => d.total_trips), backgroundColor: colors.slice(0, bt.length), borderWidth: 0, borderRadius: 4 }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    cutout: '65%',
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ padding: 16, usePointStyle: true, pointStyle: 'circle' }} }},
      tooltip: {{ callbacks: {{ label: c => c.label + ': ' + fmt(c.raw) + ' (' + ((c.raw / bt.reduce((a,b)=>a+b.total_trips,0))*100).toFixed(1) + '%)' }} }}
    }}
  }}
}});
}})();

// ===================== MONTHLY CHART =====================
let monthlyChart;
(function(){{
const m = DATA.monthly;
const labels = m.map(d => d.year_month);
monthlyChart = new Chart(document.getElementById('monthlyChart'), {{
  type: 'line',
  data: {{
    labels,
    datasets: [{{
      label: 'Total Trips',
      data: m.map(d => d.total_trips),
      borderColor: '#60a5fa',
      backgroundColor: 'rgba(96,165,250,0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 0,
      pointHoverRadius: 4,
      borderWidth: 2,
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    interaction: {{ intersect: false, mode: 'index' }},
    plugins: {{ legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: c => c.dataset.label + ': ' + fmt(c.raw) }} }}
    }},
    scales: {{
      y: {{ ticks: {{ callback: v => (v/1000).toFixed(0) + 'K' }}, grid: {{ color: 'rgba(255,255,255,0.04)' }} }},
      x: {{ ticks: {{ maxTicksLimit: 12, maxRotation: 45 }}, grid: {{ display: false }} }}
    }}
  }}
}});

document.querySelectorAll('#monthlyToggles .toggle-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#monthlyToggles .toggle-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const mode = btn.dataset.mode;
    const ch = monthlyChart;
    if (mode === 'total') {{
      ch.data.datasets = [{{
        label: 'Total Trips', data: m.map(d => d.total_trips),
        borderColor: '#60a5fa', backgroundColor: 'rgba(96,165,250,0.1)',
        fill: true, tension: 0.3, pointRadius: 0, pointHoverRadius: 4, borderWidth: 2
      }}];
    }} else if (mode === 'members') {{
      ch.data.datasets = [{{
        label: 'Member Trips', data: m.map(d => d.trips_Subscriber),
        borderColor: '#60a5fa', backgroundColor: 'rgba(96,165,250,0.1)',
        fill: true, tension: 0.3, pointRadius: 0, pointHoverRadius: 4, borderWidth: 2
      }}];
    }} else if (mode === 'casual') {{
      ch.data.datasets = [{{
        label: 'Casual Trips', data: m.map(d => d.trips_Customer),
        borderColor: '#00BFA5', backgroundColor: 'rgba(0,191,165,0.1)',
        fill: true, tension: 0.3, pointRadius: 0, pointHoverRadius: 4, borderWidth: 2
      }}];
    }} else {{
      ch.data.datasets = [
        {{ label: 'Members', data: m.map(d => d.trips_Subscriber),
          borderColor: '#60a5fa', backgroundColor: 'rgba(96,165,250,0.15)',
          fill: true, tension: 0.3, pointRadius: 0, pointHoverRadius: 4, borderWidth: 2 }},
        {{ label: 'Casual', data: m.map(d => d.trips_Customer),
          borderColor: '#00BFA5', backgroundColor: 'rgba(0,191,165,0.15)',
          fill: true, tension: 0.3, pointRadius: 0, pointHoverRadius: 4, borderWidth: 2 }}
      ];
      ch.options.plugins.legend.display = true;
    }}
    if (mode !== 'split') ch.options.plugins.legend.display = false;
    ch.update();
  }});
}});
}})();

// ===================== INSIGHTS =====================
(function(){{
const el = document.getElementById('insights');
const m = DATA.monthly;
const peakMonth = m.reduce((a,b) => b.total_trips > a.total_trips ? b : a);
const y = DATA.yearly;
const latestFull = y.filter(d => d.year <= 2025);
const growth = latestFull.length >= 2 ? ((latestFull[latestFull.length-1].total_trips / latestFull[latestFull.length-2].total_trips - 1)*100).toFixed(0) : 0;
const elec = DATA.bike_type.find(d => d.rideable_type === 'electric_bike');
const totalBikeTrips = DATA.bike_type.reduce((a,b)=>a+b.total_trips,0);
const elecPct = elec ? ((elec.total_trips/totalBikeTrips)*100).toFixed(0) : 0;
const stationGrowth = y.length >= 2 ? y[0].unique_stations + ' \u2192 ' + y[y.length-2].unique_stations : '';

const insights = [
  ['\U0001F4C8 ' + fmt(peakMonth.total_trips), 'Peak month: ' + peakMonth.year_month + ' with the highest single-month ridership on record'],
  ['\u26A1 ' + elecPct + '%', 'of all rides use electric bikes, reflecting a major shift toward e-bike adoption across the network'],
  ['\U0001F4CA ' + growth + '% YoY', '2025 vs 2024 trip growth, showing accelerating demand for Bay Wheels'],
  ['\U0001F5FA\uFE0F ' + stationGrowth, 'stations \u2014 the network has grown steadily from its 2017 launch to a dense Bay Area-wide system'],
];
el.innerHTML = insights.map(([n,d]) => `<div class="insight-card"><div class="num">${{n}}</div><div class="desc">${{d}}</div></div>`).join('');
}})();

// ===================== MAP =====================
let mapMarkers = [], mapLayer;
function initMap() {{
  map = L.map('map', {{ zoomControl: true }}).setView([37.77, -122.42], 13);
  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution: '&copy; OSM &copy; CARTO',
    maxZoom: 19
  }}).addTo(map);

  renderMarkers('flow');

  document.getElementById('mapColor').addEventListener('change', e => {{
    renderMarkers(e.target.value);
  }});

  document.getElementById('mapSearch').addEventListener('input', e => {{
    const q = e.target.value.toLowerCase();
    mapMarkers.forEach(m => {{
      if (!q || m._stationName.toLowerCase().includes(q)) {{
        m.setStyle({{ opacity: 1, fillOpacity: 0.7 }});
      }} else {{
        m.setStyle({{ opacity: 0.1, fillOpacity: 0.05 }});
      }}
    }});
  }});

  updateLegend('flow');
}}

function getFlowColor(nf) {{
  if (nf > 5000) return '#22c55e';
  if (nf > 1000) return '#4ade80';
  if (nf > 0) return '#86efac';
  if (nf > -1000) return '#fca5a5';
  if (nf > -5000) return '#f87171';
  return '#ef4444';
}}
function getActivityColor(act, max) {{
  const t = Math.min(act / max, 1);
  const r = Math.round(96 + t * 160);
  const g = Math.round(165 - t * 100);
  const b = Math.round(250 - t * 50);
  return `rgb(${{r}},${{g}},${{b}})`;
}}
function getMemberColor(pct) {{
  if (pct > 80) return '#3b82f6';
  if (pct > 60) return '#60a5fa';
  if (pct > 40) return '#a78bfa';
  if (pct > 20) return '#f59e0b';
  return '#ef4444';
}}

function renderMarkers(mode) {{
  mapMarkers.forEach(m => map.removeLayer(m));
  mapMarkers = [];
  const stations = DATA.stations;
  const maxAct = Math.max(...stations.map(s => s.total_activity));

  stations.forEach(s => {{
    let color;
    if (mode === 'flow') color = getFlowColor(s.net_flow);
    else if (mode === 'activity') color = getActivityColor(s.total_activity, maxAct);
    else color = getMemberColor(s.subscriber_pct);

    const r = Math.max(3, Math.min(14, Math.sqrt(s.total_activity / maxAct) * 14));
    const marker = L.circleMarker([s.lat, s.lng], {{
      radius: r, fillColor: color, color: 'rgba(255,255,255,0.3)',
      weight: 1, opacity: 1, fillOpacity: 0.7
    }}).addTo(map);
    marker._stationName = s.station_name;

    const flowClass = s.net_flow > 0 ? 'flow-pos' : s.net_flow < 0 ? 'flow-neg' : 'flow-neutral';
    const flowLabel = s.net_flow > 0 ? '+' + fmt(s.net_flow) : fmt(s.net_flow);
    marker.bindPopup(`
      <div style="font-family:Inter,sans-serif;min-width:220px">
        <div style="font-weight:700;font-size:.95rem;margin-bottom:8px">${{s.station_name}}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:.8rem">
          <div>Departures:</div><div style="font-weight:600">${{fmt(s.total_departures)}}</div>
          <div>Arrivals:</div><div style="font-weight:600">${{fmt(s.total_arrivals)}}</div>
          <div>Net Flow:</div><div><span class="${{flowClass}}" style="padding:1px 6px;border-radius:3px;font-size:.75rem">${{flowLabel}}</span></div>
          <div>Avg Duration:</div><div style="font-weight:600">${{fmtDur(s.avg_duration_depart)}}</div>
          <div>Member %:</div><div style="font-weight:600">${{fmtPct(s.subscriber_pct)}}</div>
          <div>Total Activity:</div><div style="font-weight:600">${{fmt(s.total_activity)}}</div>
        </div>
      </div>
    `, {{ className: '' }});
    mapMarkers.push(marker);
  }});
  updateLegend(mode);
}}

function updateLegend(mode) {{
  const el = document.getElementById('mapLegend');
  if (mode === 'flow') {{
    el.innerHTML = '<span><span class="dot" style="background:#22c55e"></span> Net arrivals</span><span><span class="dot" style="background:#86efac"></span> Slight net arrivals</span><span><span class="dot" style="background:#fca5a5"></span> Slight net departures</span><span><span class="dot" style="background:#ef4444"></span> Net departures</span>';
  }} else if (mode === 'activity') {{
    el.innerHTML = '<span><span class="dot" style="background:rgb(96,165,250)"></span> Low activity</span><span><span class="dot" style="background:rgb(200,100,210)"></span> Medium</span><span><span class="dot" style="background:rgb(256,65,200)"></span> High activity</span>';
  }} else {{
    el.innerHTML = '<span><span class="dot" style="background:#3b82f6"></span> 80%+ members</span><span><span class="dot" style="background:#60a5fa"></span> 60-80%</span><span><span class="dot" style="background:#a78bfa"></span> 40-60%</span><span><span class="dot" style="background:#f59e0b"></span> 20-40%</span><span><span class="dot" style="background:#ef4444"></span> <20%</span>';
  }}
}}

// ===================== STATION TABLE =====================
let stationData = DATA.stations.map((s,i) => ({{...s, rank: i+1}}));
let stationSort = {{ col: 'total_activity', asc: false }};
let stationPage = 0;
const ROWS_PER_PAGE = 25;

function renderStationTable() {{
  let filtered = stationData;
  const q = document.getElementById('stationSearch').value.toLowerCase();
  if (q) filtered = filtered.filter(s => s.station_name.toLowerCase().includes(q));

  // Sort
  filtered.sort((a,b) => {{
    let va = a[stationSort.col], vb = b[stationSort.col];
    if (typeof va === 'string') {{ va = va.toLowerCase(); vb = vb.toLowerCase(); }}
    return stationSort.asc ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1);
  }});

  // Re-rank
  filtered.forEach((s,i) => s._displayRank = i + 1);

  const total = filtered.length;
  const pages = Math.ceil(total / ROWS_PER_PAGE);
  stationPage = Math.min(stationPage, pages - 1);
  const start = stationPage * ROWS_PER_PAGE;
  const pageData = filtered.slice(start, start + ROWS_PER_PAGE);
  const maxAct = Math.max(...DATA.stations.map(s => s.total_activity));

  const body = document.getElementById('stationBody');
  body.innerHTML = pageData.map(s => {{
    const flowClass = s.net_flow > 0 ? 'flow-pos' : s.net_flow < 0 ? 'flow-neg' : 'flow-neutral';
    const flowLabel = s.net_flow > 0 ? '+' + fmt(s.net_flow) : fmt(s.net_flow);
    const depPct = (s.total_departures / s.total_activity * 100).toFixed(0);
    const arrPct = (s.total_arrivals / s.total_activity * 100).toFixed(0);
    return `<tr data-station="${{s.station_name}}" style="cursor:pointer">
      <td>${{s._displayRank}}</td>
      <td style="font-weight:500;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{s.station_name}}</td>
      <td>${{fmt(s.total_activity)}}</td>
      <td>${{fmt(s.total_departures)}}</td>
      <td>${{fmt(s.total_arrivals)}}</td>
      <td><span class="flow-indicator ${{flowClass}}">${{flowLabel}}</span></td>
      <td>${{fmtDur(s.avg_duration_depart)}}</td>
      <td>
        <div style="display:flex;align-items:center;gap:6px">
          <div class="mini-bar" style="width:60px">
            <div class="mini-bar-fill" style="width:${{s.subscriber_pct}}%;background:linear-gradient(90deg,#3b82f6,#60a5fa)"></div>
          </div>
          ${{fmtPct(s.subscriber_pct)}}
        </div>
      </td>
    </tr>`;
  }}).join('');

  // Page controls
  const pc = document.getElementById('stationPages');
  let pcHTML = `<button class="page-btn" onclick="stationPage=0;renderStationTable()" ${{stationPage===0?'disabled':''}}>\u00AB</button>`;
  pcHTML += `<button class="page-btn" onclick="stationPage--;renderStationTable()" ${{stationPage===0?'disabled':''}}>Prev</button>`;
  pcHTML += `<span style="font-size:.8rem;color:var(--text2);padding:0 8px">${{start+1}}\u2013${{Math.min(start+ROWS_PER_PAGE,total)}} of ${{total}}</span>`;
  pcHTML += `<button class="page-btn" onclick="stationPage++;renderStationTable()" ${{stationPage>=pages-1?'disabled':''}}>Next</button>`;
  pcHTML += `<button class="page-btn" onclick="stationPage=${{pages-1}};renderStationTable()" ${{stationPage>=pages-1?'disabled':''}}>\u00BB</button>`;
  pc.innerHTML = pcHTML;

  // Row click handlers
  body.querySelectorAll('tr').forEach(tr => {{
    tr.addEventListener('click', () => showStationDetail(tr.dataset.station));
  }});
}}

let stationDetailChart = null;
function showStationDetail(name) {{
  const s = DATA.stations.find(x => x.station_name === name);
  if (!s) return;
  const smData = DATA.station_monthly.filter(x => x.station_name === name).sort((a,b) => a.year_month.localeCompare(b.year_month));
  const el = document.getElementById('stationDetail');

  if (smData.length === 0) {{
    el.innerHTML = `<div class="station-detail"><h4>${{name}}</h4><p style="color:var(--text2)">No monthly trend data available for this station (not in top 50 by activity).</p></div>`;
    return;
  }}

  el.innerHTML = `<div class="station-detail"><h4>${{name}}</h4><div class="chart-container" style="height:250px"><canvas id="stationDetailCanvas"></canvas></div></div>`;

  if (stationDetailChart) stationDetailChart.destroy();
  stationDetailChart = new Chart(document.getElementById('stationDetailCanvas'), {{
    type: 'bar',
    data: {{
      labels: smData.map(d => d.year_month),
      datasets: [{{ label: 'Monthly Trips', data: smData.map(d => d.trips),
        backgroundColor: 'rgba(96,165,250,0.5)', borderRadius: 3, borderSkipped: false }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: c => fmt(c.raw) + ' trips' }} }} }},
      scales: {{
        y: {{ ticks: {{ callback: v => v >= 1000 ? (v/1000).toFixed(0)+'K' : v }}, grid: {{ color: 'rgba(255,255,255,0.04)' }} }},
        x: {{ ticks: {{ maxTicksLimit: 10, maxRotation: 45 }}, grid: {{ display: false }} }}
      }}
    }}
  }});
}}

document.getElementById('stationSearch').addEventListener('input', () => {{ stationPage = 0; renderStationTable(); }});
document.querySelectorAll('#stationTable th').forEach(th => {{
  th.addEventListener('click', () => {{
    const col = th.dataset.col;
    if (stationSort.col === col) stationSort.asc = !stationSort.asc;
    else {{ stationSort.col = col; stationSort.asc = col === 'station_name'; }}
    document.querySelectorAll('#stationTable th').forEach(t => t.classList.remove('sorted'));
    th.classList.add('sorted');
    th.querySelector('.sort-icon').textContent = stationSort.asc ? '\\u25B2' : '\\u25BC';
    stationPage = 0;
    renderStationTable();
  }});
}});
renderStationTable();

// ===================== ROUTE TABLE =====================
let routeSort = {{ col: 'count', asc: false }};
function renderRouteTable() {{
  let routes = DATA.top_routes.map((r,i) => ({{...r, rank: i+1}}));
  const q = document.getElementById('routeSearch').value.toLowerCase();
  if (q) routes = routes.filter(r => r.start_station_name.toLowerCase().includes(q) || r.end_station_name.toLowerCase().includes(q));

  routes.sort((a,b) => {{
    const map = {{ rank: 'trip_count', start: 'start_station_name', end: 'end_station_name', count: 'trip_count', dur: 'avg_duration' }};
    const col = map[routeSort.col] || routeSort.col;
    let va = a[col], vb = b[col];
    if (typeof va === 'string') {{ va = va.toLowerCase(); vb = vb.toLowerCase(); }}
    return routeSort.asc ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1);
  }});

  routes.forEach((r,i) => r._rank = i + 1);
  const maxTrips = Math.max(...DATA.top_routes.map(r => r.trip_count));

  document.getElementById('routeBody').innerHTML = routes.map(r => {{
    const barW = (r.trip_count / maxTrips * 100).toFixed(0);
    return `<tr>
      <td>${{r._rank}}</td>
      <td style="max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{r.start_station_name}}</td>
      <td style="max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{r.end_station_name}}</td>
      <td>
        <div style="display:flex;align-items:center;gap:8px">
          <div class="mini-bar" style="width:100px">
            <div class="mini-bar-fill" style="width:${{barW}}%;background:linear-gradient(90deg,#60a5fa,#00BFA5)"></div>
          </div>
          ${{fmt(r.trip_count)}}
        </div>
      </td>
      <td>${{fmtDur(r.avg_duration)}}</td>
    </tr>`;
  }}).join('');
}}

document.getElementById('routeSearch').addEventListener('input', renderRouteTable);
document.querySelectorAll('#routeTable th').forEach(th => {{
  th.addEventListener('click', () => {{
    const col = th.dataset.col;
    if (routeSort.col === col) routeSort.asc = !routeSort.asc;
    else {{ routeSort.col = col; routeSort.asc = col === 'start' || col === 'end'; }}
    document.querySelectorAll('#routeTable th').forEach(t => t.classList.remove('sorted'));
    th.classList.add('sorted');
    th.querySelector('.sort-icon').textContent = routeSort.asc ? '\\u25B2' : '\\u25BC';
    renderRouteTable();
  }});
}});
renderRouteTable();

// ===================== HOURLY CHART =====================
let hourlyChart;
(function(){{
const h = DATA.hourly;
hourlyChart = new Chart(document.getElementById('hourlyChart'), {{
  type: 'bar',
  data: {{
    labels: h.map(d => d.hour + ':00'),
    datasets: [
      {{ label: 'Members', data: h.map(d => d.trips_Subscriber), backgroundColor: 'rgba(96,165,250,0.7)', borderRadius: 4, borderSkipped: false }},
      {{ label: 'Casual', data: h.map(d => d.trips_Customer), backgroundColor: 'rgba(0,191,165,0.7)', borderRadius: 4, borderSkipped: false }}
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'top', labels: {{ usePointStyle: true, pointStyle: 'circle' }} }},
      tooltip: {{ callbacks: {{ label: c => c.dataset.label + ': ' + fmt(c.raw) }} }}
    }},
    scales: {{
      x: {{ stacked: true, grid: {{ display: false }} }},
      y: {{ stacked: true, ticks: {{ callback: v => (v/1e6).toFixed(1) + 'M' }}, grid: {{ color: 'rgba(255,255,255,0.04)' }} }}
    }}
  }}
}});

document.querySelectorAll('#hourlyToggles .toggle-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#hourlyToggles .toggle-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const ch = hourlyChart;
    if (btn.dataset.mode === 'count') {{
      ch.data.datasets = [
        {{ label: 'Members', data: h.map(d => d.trips_Subscriber), backgroundColor: 'rgba(96,165,250,0.7)', borderRadius: 4, borderSkipped: false }},
        {{ label: 'Casual', data: h.map(d => d.trips_Customer), backgroundColor: 'rgba(0,191,165,0.7)', borderRadius: 4, borderSkipped: false }}
      ];
      ch.options.scales.x.stacked = true;
      ch.options.scales.y.stacked = true;
      ch.options.scales.y.ticks.callback = v => (v/1e6).toFixed(1) + 'M';
    }} else {{
      ch.data.datasets = [{{
        label: 'Avg Duration', data: h.map(d => d.avg_duration),
        backgroundColor: 'rgba(245,158,11,0.7)', borderRadius: 4, borderSkipped: false
      }}];
      ch.options.scales.x.stacked = false;
      ch.options.scales.y.stacked = false;
      ch.options.scales.y.ticks.callback = v => fmtDur(v);
    }}
    ch.update();
  }});
}});
}})();

// ===================== DAY OF WEEK CHART =====================
let dowChart;
(function(){{
const d = DATA.dow;
dowChart = new Chart(document.getElementById('dowChart'), {{
  type: 'bar',
  data: {{
    labels: d.map(x => x.day_name),
    datasets: [
      {{ label: 'Members', data: d.map(x => x.trips_Subscriber), backgroundColor: 'rgba(96,165,250,0.7)', borderRadius: 4, borderSkipped: false }},
      {{ label: 'Casual', data: d.map(x => x.trips_Customer), backgroundColor: 'rgba(0,191,165,0.7)', borderRadius: 4, borderSkipped: false }}
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'top', labels: {{ usePointStyle: true, pointStyle: 'circle' }} }},
      tooltip: {{ callbacks: {{ label: c => c.dataset.label + ': ' + fmt(c.raw) }} }}
    }},
    scales: {{
      x: {{ stacked: true, grid: {{ display: false }} }},
      y: {{ stacked: true, ticks: {{ callback: v => (v/1e6).toFixed(1) + 'M' }}, grid: {{ color: 'rgba(255,255,255,0.04)' }} }}
    }}
  }}
}});

document.querySelectorAll('#dowToggles .toggle-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#dowToggles .toggle-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const ch = dowChart;
    if (btn.dataset.mode === 'count') {{
      ch.data.datasets = [
        {{ label: 'Members', data: d.map(x => x.trips_Subscriber), backgroundColor: 'rgba(96,165,250,0.7)', borderRadius: 4, borderSkipped: false }},
        {{ label: 'Casual', data: d.map(x => x.trips_Customer), backgroundColor: 'rgba(0,191,165,0.7)', borderRadius: 4, borderSkipped: false }}
      ];
      ch.options.scales.x.stacked = true;
      ch.options.scales.y.stacked = true;
      ch.options.scales.y.ticks.callback = v => (v/1e6).toFixed(1) + 'M';
    }} else {{
      ch.data.datasets = [{{
        label: 'Avg Duration', data: d.map(x => x.avg_duration),
        backgroundColor: 'rgba(245,158,11,0.7)', borderRadius: 4, borderSkipped: false
      }}];
      ch.options.scales.x.stacked = false;
      ch.options.scales.y.stacked = false;
      ch.options.scales.y.ticks.callback = v => fmtDur(v);
    }}
    ch.update();
  }});
}});
}})();
</script>
</body>
</html>'''

with open(args.output, 'w') as f:
    f.write(html)

print(f"Dashboard written to: {args.output}")
print(f"File size: {len(html) / 1024 / 1024:.2f} MB")
