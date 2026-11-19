// KEEL indicator charts (Observable Plot). Each indicator page passes its chart spec, written by
// src/indicators/pages.py, plus Plot, d3 and Inputs from Quarto's OJS runtime, so this module
// loads nothing itself. Data URLs are relative to the page, so the site works under any base path.

export const TIMEFRAMES = [
  {label: "All", start: null},
  {label: "Since 2010", start: "2010-01-01"},
  {label: "Since 2019", start: "2019-01-01"},
  {label: "Since 2022 Q4", start: "2022-10-01"},
];

const FALLBACK_COLORS = ["#1f5fa8", "#c0501c", "#0f7a6c", "#7a3fb8", "#a3263b", "#4f7a12", "#8a6a00", "#50606f"];

function currentTheme() {
  return document.body.classList.contains("quarto-dark") ? "dark" : "light";
}

// Yields the theme now and again whenever the light/dark toggle changes it, so charts redraw.
export function* themeChanges() {
  let last = currentTheme();
  yield last;
  while (true) {
    yield new Promise(resolve => {
      const observer = new MutationObserver(() => {
        if (currentTheme() !== last) {
          observer.disconnect();
          last = currentTheme();
          resolve(last);
        }
      });
      observer.observe(document.body, {attributes: true, attributeFilter: ["class"]});
    });
  }
}

function palette() {
  const style = getComputedStyle(document.body);
  return FALLBACK_COLORS.map((c, i) => style.getPropertyValue(`--keel-c${i}`).trim() || c);
}

export async function loadData(d3, spec) {
  const out = {};
  await Promise.all(Object.entries(spec.series).map(async ([id, s]) => {
    if (!s.available) return;
    out[id] = await d3.csv(spec.dataBase + s.file, d3.autoType);
    if (s.trendFile) out[id + "__trend"] = await d3.csv(spec.dataBase + s.trendFile, d3.autoType);
  }));
  return out;
}

function hidden(value) {
  const el = document.createElement("div");
  el.style.display = "none";
  el.value = value;
  return el;
}

export function viewInput(Inputs, spec) {
  const labels = spec.views.map(v => v.label);
  if (labels.length === 1) return hidden(labels[0]);
  return Inputs.radio(labels, {label: "View", value: labels.includes(spec.defaultView) ? spec.defaultView : labels[0]});
}

function findView(spec, label) {
  return spec.views.find(v => v.label === label) || spec.views[0];
}

function seriesName(spec, id) {
  const s = spec.series[id];
  return s.label || s.title || id;
}

export function seriesInput(Inputs, spec, viewLabel) {
  const view = findView(spec, viewLabel);
  const choices = view.series.filter(id => spec.series[id].available);
  if (view.kind === "multi" || choices.length < 2) return hidden(choices[0] || view.series[0]);
  return Inputs.select(choices, {label: "Series", format: id => seriesName(spec, id), value: choices[0], width: 420});
}

// No timeframe choice when every view is a stacked-bar view (EA2: seven samples since December 2024).
export function timeframeInput(Inputs, spec) {
  if (spec.views.every(v => v.kind === "stacked")) return hidden("All");
  return Inputs.radio(TIMEFRAMES.map(t => t.label), {label: "Timeframe", value: "All"});
}

export function logInput(Inputs, spec, viewLabel) {
  const view = findView(spec, viewLabel);
  if (!view.log_option) return hidden(false);
  return Inputs.toggle({label: "Log scale", value: true});
}

function element(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text != null) el.textContent = text;
  return el;
}

function message(text) {
  const wrap = element("div", "keel-chart");
  wrap.append(element("p", "keel-chart-message", text));
  return wrap;
}

function legend(items) {
  const box = element("div", "keel-legend");
  for (const {label, color, dashed} of items) {
    const item = element("span");
    const swatch = element("span", "keel-legend-swatch");
    swatch.style.background = dashed ? "none" : color;
    if (dashed) swatch.style.borderTop = `2px dashed ${color}`;
    item.append(swatch, document.createTextNode(label));
    box.append(item);
  }
  return box;
}

function unitsLabel(units, deviation) {
  if (!deviation) return units;
  return units === "percent" ? "percentage points from the 2010–19 trend" : `${units}, difference from the 2010–19 trend`;
}

// Hover-tip wording: periods as on the page (pages.py fmt_period); percents as "%" (owner, 2026-11-19).
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
  "October", "November", "December"];
export function fmtPeriod(date, frequency) {
  const y = date.getUTCFullYear(), m = date.getUTCMonth();
  if (frequency === "quarterly") return `${y} Q${Math.floor(m / 3) + 1}`;
  if (frequency === "monthly") return `${MONTHS[m]} ${y}`;
  if (frequency === "annual") return String(y);
  return `${date.getUTCDate()} ${MONTHS[m]} ${y}`;
}
export function fmtValue(value, units, deviation = false) {
  const abs = Math.abs(value);
  const number = abs >= 1000 ? Math.round(abs).toLocaleString("en-US") : abs.toFixed(1);
  if (deviation) {
    const sign = value > 0 ? "+" : value < 0 ? "−" : "";
    return units === "percent" ? `${sign}${number} points from the trend` : `${sign}${number} ${units} from the trend`;
  }
  const signed = (value < 0 ? "−" : "") + number;
  if (units === "percent") return `${signed}%`;
  const index = /^index \((.*)\)$/.exec(units);
  return index ? `${signed} (index, ${index[1]})` : `${signed} ${units}`;
}

const TABLE_MAX_ROWS = 120;

// A text version of what the chart plots, for readers who cannot use the chart: the series and
// timeframe currently shown, formatted as in the hover tips. Long series show the latest rows.
function dataTable(spec, plotted, view, ids, singleLabel) {
  const deviation = view.kind === "deviation";
  const columns = [];
  const rows = new Map();
  for (const d of plotted) {
    const label = d.label || singleLabel;
    if (!columns.includes(label)) columns.push(label);
    const meta = spec.series[d.id || ids[0]];
    const key = +d.date;
    if (!rows.has(key)) rows.set(key, {date: d.date, frequency: meta.frequency, cells: new Map()});
    rows.get(key).cells.set(label, fmtValue(deviation ? d.deviation : d.value, meta.units, deviation));
  }
  const all = [...rows.values()].sort((a, b) => a.date - b.date);
  const shown = all.slice(-TABLE_MAX_ROWS);
  const details = element("details", "keel-datatable");
  details.append(element("summary", null, "Data table"));
  const scroller = element("div", "keel-datatable-scroll");
  const table = element("table");
  const caption = shown.length < all.length
    ? `Values plotted in this chart. Showing the latest ${shown.length} of ${all.length} rows; choose a shorter timeframe to see other periods.`
    : `Values plotted in this chart (${all.length} rows).`;
  table.append(element("caption", null, caption));
  const head = element("tr");
  for (const text of ["Period", ...columns]) {
    const th = element("th", null, text);
    th.scope = "col";
    head.append(th);
  }
  const thead = element("thead");
  thead.append(head);
  table.append(thead);
  const body = element("tbody");
  for (const r of shown) {
    const tr = element("tr");
    const th = element("th", null, fmtPeriod(r.date, r.frequency));
    th.scope = "row";
    tr.append(th);
    for (const c of columns) tr.append(element("td", null, r.cells.get(c) ?? "–"));
    body.append(tr);
  }
  table.append(body);
  scroller.append(table);
  details.append(scroller);
  return details;
}

const utc = s => new Date(s + "T00:00:00Z");
// The trend is fitted to 2010-19 and extended forward; it is not drawn before the fit window.
const TREND_START = utc("2010-01-01");

export function renderChart(Plot, d3, spec, data, opts) {
  void opts.theme; // redraw on theme change
  const view = findView(spec, opts.view);
  if (!view.available) {
    return message("Data still being collected. This view will appear once the download from the source is complete.");
  }
  if (view.kind === "stacked") return renderStacked(Plot, d3, spec, data, view, opts);
  const colors = palette();
  const tf = TIMEFRAMES.find(t => t.label === opts.timeframe) || TIMEFRAMES[0];
  const start = tf.start ? utc(tf.start) : null;
  const inRange = rows => (start ? rows.filter(d => d.date >= start) : rows);
  const marks = [];
  const notes = [];
  const legendItems = [];
  const fmtDate = d3.utcFormat("%-d %B %Y");
  let ids, plotted, yLabel, colorScale;

  if (view.kind === "multi") {
    ids = view.series;
    const labels = [];
    plotted = [];
    for (const id of ids) {
      for (const d of inRange(data[id])) {
        const label = d.group != null ? (spec.groupLabels[d.group] || String(d.group)) : seriesName(spec, id);
        if (!labels.includes(label)) labels.push(label);
        plotted.push({...d, label, id, key: `${label}|${d.segment ?? 0}`});
      }
    }
    const range = labels.map((_, i) => colors[i % colors.length]);
    colorScale = {domain: labels, range};
    labels.forEach((label, i) => legendItems.push({label, color: range[i]}));
    if (plotted.some(d => d.se != null)) {
      marks.push(Plot.areaY(plotted.filter(d => d.se != null), {
        x: "date", y1: d => d.value - 1.96 * d.se, y2: d => d.value + 1.96 * d.se, z: "key", fill: "label", fillOpacity: 0.12,
      }));
      notes.push(spec.seNote);
    }
    marks.push(Plot.lineY(plotted, {x: "date", y: "value", z: "key", stroke: "label", strokeWidth: 2}));
    if (plotted.length < 40) marks.push(Plot.dot(plotted, {x: "date", y: "value", fill: "label", r: 3}));
    yLabel = spec.series[ids[0]].units;
  } else {
    const id = view.series.includes(opts.series) ? opts.series : view.series[0];
    ids = [id];
    const meta = spec.series[id];
    const label = seriesName(spec, id);
    if (view.kind === "deviation") {
      plotted = inRange((data[id + "__trend"] || []).filter(d => d.deviation != null && d.date >= TREND_START));
      if (!plotted.length) {
        return message("There are not enough data from 2010 to 2019 to fit a trend for this series, so the deviation view is not available.");
      }
      marks.push(Plot.ruleY([0], {stroke: "currentColor", strokeOpacity: 0.6}));
      marks.push(Plot.lineY(plotted, {x: "date", y: "deviation", z: "segment", stroke: colors[0], strokeWidth: 2}));
      yLabel = unitsLabel(meta.units, true);
      notes.push("Zero is a straight-line trend fitted to 2010 to 2019 and extended. This is a chart view, not the threshold rule.");
      legendItems.push({label, color: colors[0]});
    } else {
      plotted = inRange(data[id]);
      if (view.kind === "band") {
        const lo = new Map(data[view.band[0]].map(d => [+d.date, d.value]));
        const hi = new Map(data[view.band[1]].map(d => [+d.date, d.value]));
        const band = plotted.filter(d => lo.has(+d.date) && hi.has(+d.date)).map(d => ({date: d.date, lo: lo.get(+d.date), hi: hi.get(+d.date)}));
        marks.push(Plot.areaY(band, {x: "date", y1: "lo", y2: "hi", fill: colors[0], fillOpacity: 0.2}));
        if (view.note) notes.push(view.note);
      }
      if (plotted.some(d => d.se != null)) {
        marks.push(Plot.areaY(plotted.filter(d => d.se != null), {
          x: "date", y1: d => d.value - 1.96 * d.se, y2: d => d.value + 1.96 * d.se, z: "segment", fill: colors[0], fillOpacity: 0.28,
        }));
        notes.push(spec.seNote);
      }
      if (view.rule != null) marks.push(Plot.ruleY([view.rule], {stroke: "currentColor", strokeOpacity: 0.5}));
      marks.push(Plot.lineY(plotted, {x: "date", y: "value", z: plotted.length && plotted[0].segment != null ? "segment" : undefined, stroke: colors[0], strokeWidth: 2}));
      if (plotted.length < 40) marks.push(Plot.dot(plotted, {x: "date", y: "value", fill: colors[0], r: 3}));
      legendItems.push({label, color: colors[0]});
      if (view.trend && data[id + "__trend"]) {
        const trend = inRange(data[id + "__trend"].filter(d => d.trend != null && d.date >= TREND_START));
        if (trend.length) {
          marks.push(Plot.lineY(trend, {x: "date", y: "trend", stroke: colors[1], strokeWidth: 1.5, strokeDasharray: "5,4"}));
          legendItems.push({label: "2010–19 trend, extended", color: colors[1], dashed: true});
        } else {
          notes.push("No 2010–19 trend is drawn: the series has too few data from 2010 to 2019.");
        }
      }
      yLabel = meta.units;
    }
  }

  if (!plotted.length) return message("No data in this timeframe. Choose a longer timeframe.");
  const [x0, x1] = d3.extent(plotted, d => d.date);
  const within = d => d.when >= x0 && d.when <= x1;

  const breaks = [];
  for (const id of ids) {
    for (const b of spec.series[id].breaks || []) {
      if (!breaks.some(x => x.date === b.date)) breaks.push({...b, when: utc(b.date)});
    }
  }
  const shownBreaks = breaks.filter(within);
  const shownMarkers = spec.markers.map(m => ({...m, when: utc(m.date)})).filter(within);
  if (shownBreaks.length) {
    marks.push(Plot.ruleX(shownBreaks, {x: "when", stroke: "currentColor", strokeWidth: 1.5, strokeDasharray: "2,3"}));
    marks.push(Plot.text(shownBreaks, {x: "when", text: () => "Break", frameAnchor: "top", dy: -6, fontSize: 11}));
  }
  if (shownMarkers.length) {
    marks.push(Plot.ruleX(shownMarkers, {x: "when", stroke: colors[7], strokeOpacity: 0.7}));
    marks.push(Plot.text(shownMarkers, {x: "when", text: (d, i) => String(i + 1), frameAnchor: "top", dy: 8, dx: 6, fontSize: 11, fontWeight: 700}));
  }
  if (Plot.tip) {
    const deviation = view.kind === "deviation";
    const y = deviation ? "deviation" : "value";
    const tipText = d => {
      const meta = spec.series[d.id || ids[0]];
      const name = d.label || seriesName(spec, ids[0]);
      return `${name}\n${fmtPeriod(d.date, meta.frequency)}: ${fmtValue(d[y], meta.units, deviation)}`;
    };
    marks.push(Plot.tip(plotted, Plot.pointerX({x: "date", y, title: tipText, stroke: view.kind === "multi" ? "label" : undefined})));
  }

  const values = plotted.map(d => (view.kind === "deviation" ? d.deviation : d.value));
  const big = d3.max(values, Math.abs) >= 100000;
  const width = Math.max(280, opts.width || 640);
  const chart = Plot.plot({
    width,
    height: Math.round(Math.min(440, Math.max(260, width * 0.55))),
    marginLeft: big ? 56 : 48,
    marginTop: 24,
    x: {type: "utc", label: null},
    y: {label: yLabel, grid: true, type: opts.log ? "log" : "linear", tickFormat: big ? "~s" : undefined, nice: true},
    color: colorScale,
    marks,
    ariaLabel: `${spec.chartTitle}: ${view.label}`,
    ariaDescription: `Line chart of ${ids.map(id => seriesName(spec, id)).join(", ")} over time.`,
  });

  const wrap = element("figure", "keel-chart");
  wrap.append(legend(legendItems), chart);
  const list = element("ul", "keel-chart-notes");
  shownBreaks.forEach(b => list.append(element("li", null, `Series break, ${fmtDate(b.when)}: ${b.note}`)));
  shownMarkers.forEach((m, i) => list.append(element("li", null, `Marker ${i + 1}, ${fmtDate(m.when)}: ${m.label}`)));
  notes.forEach(n => list.append(element("li", null, n)));
  if (list.childElementCount) wrap.append(list);
  wrap.append(dataTable(spec, plotted, view, ids, legendItems[0].label));
  return wrap;
}

// ------------------------------------------------------------------ stacked bars (EA2)
// One bar per sample on a time axis, centred on the middle of its sample window, split into groups
// that add to 100 and stacked family by family (owner review, 2026-11-19). Segments between breaks are
// labelled as method groups, with a definition on hover, focus or tap.

// Warm for the first family (automation), cool for the second (augmentation); light and dark themes.
const STACK_COLORS = {
  light: [["#b5562f", "#e3a079"], ["#1f5f7a", "#4f93ad", "#9cc6d6"]],
  dark: [["#e07a50", "#f0b996"], ["#3d8fb0", "#6fb2cb", "#b4dbe8"]],
};
const BAR_HALF_DAYS = 11; // bars are drawn 22 days wide whatever the sample length, so each stays visible
const DAY = 864e5;

// A small tooltip for the method-group labels in the chart and the data table.
function groupTip(figure) {
  const tip = element("div", "keel-grouptip");
  tip.setAttribute("role", "tooltip");
  tip.hidden = true;
  figure.append(tip);
  const show = el => {
    tip.textContent = el.getAttribute("data-tip");
    tip.hidden = false;
    const f = figure.getBoundingClientRect(), b = el.getBoundingClientRect();
    tip.style.left = `${Math.max(0, Math.min(b.left - f.left, f.width - tip.offsetWidth))}px`;
    tip.style.top = `${b.bottom - f.top + 6}px`;
  };
  const target = e => e.target.closest && e.target.closest("[data-tip]");
  figure.addEventListener("mouseover", e => { const t = target(e); if (t) show(t); else tip.hidden = true; });
  figure.addEventListener("mouseleave", () => { tip.hidden = true; });
  figure.addEventListener("focusin", e => { const t = target(e); if (t) show(t); });
  figure.addEventListener("focusout", () => { tip.hidden = true; });
  figure.addEventListener("keydown", e => { if (e.key === "Escape") tip.hidden = true; });
  document.addEventListener("pointerdown", e => {
    const t = figure.contains(e.target) && target(e);
    if (t) show(t); else tip.hidden = true;
  });
}

function markTip(el, text) {
  el.setAttribute("data-tip", text);
  el.setAttribute("tabindex", "0");
  el.classList.add("keel-grouplabel");
}

function renderStacked(Plot, d3, spec, data, view, opts) {
  const id = view.series[0];
  const meta = spec.series[id];
  const rows = data[id] || [];
  if (!rows.length) return message("No data yet.");
  const order = view.families.flatMap(f => f.groups);
  const theme = STACK_COLORS[currentTheme()];
  const colorOf = Object.fromEntries(view.families.flatMap((f, i) => f.groups.map((g, j) => [g, theme[i][j]])));
  const name = g => view.groupNames[g] || g;
  const groupOf = seg => view.methodGroups[seg] || {name: String(seg + 1), tip: ""};
  const fmtDay = d3.utcFormat("%-d %B %Y");
  const asDate = v => (v instanceof Date ? v : utc(String(v)));

  // One record per sample, in date order, with its window and its group values.
  const samples = [];
  for (const d of [...rows].sort((a, b) => a.date - b.date)) {
    let s = samples.find(x => +x.date === +d.date);
    if (!s) {
      const end = asDate(d.sample_end);
      s = {date: d.date, end, mid: new Date((+d.date + +end) / 2), period: d.period, release: asDate(d.release),
        segment: d.segment ?? 0, values: {}};
      samples.push(s);
    }
    s.values[d.group] = d.value;
  }
  const pieces = [];
  for (const s of samples) {
    let y = 0;
    for (const g of order) {
      const v = s.values[g] ?? 0;
      pieces.push({x1: new Date(+s.mid - BAR_HALF_DAYS * DAY), x2: new Date(+s.mid + BAR_HALF_DAYS * DAY), y1: y, y2: y + v,
        group: g, value: v, period: s.period, release: s.release});
      y += v;
    }
    s.first = view.families[0].groups.reduce((t, g) => t + (s.values[g] ?? 0), 0);
  }
  const firstName = view.families[0].name.toLowerCase();
  const firsts = samples.filter((s, i) => i === 0 || s.segment !== samples[i - 1].segment);
  const separators = firsts.slice(1).map(s => {
    const prev = samples[samples.indexOf(s) - 1];
    return new Date((+prev.end + +s.date) / 2);
  });
  const x0 = new Date(+samples[0].mid - 40 * DAY), x1 = new Date(+samples.at(-1).mid + 40 * DAY);

  const full = Math.max(280, opts.width || 640);
  const width = full >= 640 ? full - 170 : full; // room for the legend on the right on wide screens
  // Narrow charts: group labels shorten to "A", "B"..., and a share label too close to the one before
  // it is raised a line so the two do not overlap.
  const narrow = width < 560;
  const groupText = s => (narrow ? "" : "Group ") + groupOf(s.segment).name;
  const pxPerDay = (width - 64) / ((+x1 - +x0) / DAY);

  // Of two labels too close to share a line, the higher value goes on top (owner, 2026-11-19).
  samples.forEach((s, i) => {
    const prev = samples[i - 1];
    s.raise = false;
    if (prev && !prev.raise && (+s.mid - +prev.mid) / DAY * pxPerDay < 34) {
      if (s.first > prev.first) s.raise = true;
      else prev.raise = true;
    }

  });
  const tipText = d => `${name(d.group)}, sampled ${d.period}\n${fmtValue(d.value, meta.units)} (released ${fmtDay(d.release)})`;
  const marks = [
    Plot.ruleX(separators, {stroke: "currentColor", strokeOpacity: 0.6, strokeDasharray: "2,3"}),
    // Behind the bars, so it shows between them and does not cross the share labels.
    Plot.ruleY([50], {stroke: "currentColor", strokeDasharray: "4,3", strokeWidth: 1.5}),
    Plot.rect(pieces, {x1: "x1", x2: "x2", y1: "y1", y2: "y2", fill: d => colorOf[d.group], ...(Plot.tip ? {} : {title: tipText})}),
    // The first family's total sits on the bar just above where its segments end (owner, 2026-11-19),
    // in white with a dark halo so it reads on the blue and where it overhangs a narrow bar.
    ...[samples.filter(s => !s.raise), samples.filter(s => s.raise)].map((set, k) =>
      Plot.text(set, {x: "mid", y: "first", text: s => s.first.toFixed(1), dy: k ? -24 : -9, fontWeight: 700, fontSize: 12,
        fill: "white", stroke: "rgba(15, 25, 35, 0.85)", strokeWidth: 3, paintOrder: "stroke"})),
    Plot.text(firsts, {x: s => new Date(+s.mid - BAR_HALF_DAYS * DAY), y: 100, text: groupText,
      dy: -12, textAnchor: "start", fontSize: 11}),
  ];
  if (Plot.tip) {
    marks.push(Plot.tip(pieces, Plot.pointer({x: d => new Date((+d.x1 + +d.x2) / 2), y: d => (d.y1 + d.y2) / 2, title: tipText})));
  }
  const chart = Plot.plot({
    width,
    height: Math.round(Math.min(420, Math.max(300, width * 0.55))),
    marginLeft: 44, marginTop: 30, marginBottom: 44,
    // Every tick names its year (owner, 2026-11-19); quarterly ticks, half-yearly on narrow screens.
    x: {type: "utc", domain: [x0, x1], label: "Sampling date", labelAnchor: "center", labelArrow: "none",
      ticks: d3.utcMonth.every(narrow ? 6 : 3), tickFormat: d3.utcFormat("%b\n%Y")},
    y: {domain: [0, 100], ticks: [0, 25, 50, 75, 100], tickFormat: d => `${d}%`, grid: true, label: null},
    marks,
    ariaLabel: `${spec.chartTitle}: ${view.label}`,
    ariaDescription: `Stacked bar chart: for each sample, the share of each pattern (${order.map(name).join(", ")}), adding to 100 percent.`,
  });
  // Matched by text: the Plot bundled with Quarto ignores the className option.
  chart.querySelectorAll("text").forEach(t => {
    const s = firsts.find(x => groupText(x) === t.textContent);
    if (s) markTip(t, groupOf(s.segment).tip);
  });

  // Legend on the right, top to bottom in stacking order (top of the bar first), by family.
  const box = element("div", "keel-legend keel-legend-stack");
  for (const f of [...view.families].reverse()) {
    box.append(element("strong", "keel-legend-family", f.name));
    for (const g of [...f.groups].reverse()) {
      const item = element("span");
      const swatch = element("span", "keel-legend-swatch");
      swatch.style.background = colorOf[g];
      item.append(swatch, document.createTextNode(name(g)));
      box.append(item);
    }
  }
  const row = element("div", "keel-chart-row");
  row.append(chart, box);

  const wrap = element("figure", "keel-chart keel-chart-stacked");
  wrap.append(row);
  const list = element("ul", "keel-chart-notes");
  list.append(element("li", null, `Each bar is one sample, centred on the middle of its sample window and drawn the same width so it stays visible. The number on each bar is its ${firstName} share: the height of the ${firstName} patterns at the bottom of the bar, printed where the ${view.families[1].name.toLowerCase()} patterns begin. The dashed line marks 50 percent. Dotted lines separate the method groups: compare bars only within a group.`));
  if (view.groupsLink) list.append(groupsLinkItem(view.groupsLink));
  wrap.append(list);
  wrap.append(stackedTable(spec, view, samples, name, groupOf, data));
  groupTip(wrap);
  return wrap;
}

// "Method groups A to D are defined under Method groups." with a link to the page section.
function groupsLinkItem(href, tag = "li") {
  const item = element(tag);
  const a = element("a", null, "Method groups");
  a.href = href;
  item.append(document.createTextNode("The method groups A to D are defined under "), a, document.createTextNode("."));
  return item;
}

// Data table for the stacked view: the groups under their family headings, then each family's total,
// then (if the view names one) the share left out of the totals, on its own denominator.
function stackedTable(spec, view, samples, name, groupOf, data) {
  const dateKey = d => d.toISOString().slice(0, 10);
  const footnotes = Object.entries(view.footnotes || {})
    .filter(([key]) => samples.some(s => dateKey(s.date) === key))
    .map(([key, text], i) => ({key, text, n: i + 1, id: `${spec.id}-note-${i + 1}`}));
  const leftOut = view.leftOut && data[view.leftOut.series]
    ? new Map(data[view.leftOut.series].map(d => [+d.date, d.value])) : null;
  const meta = spec.series[view.series[0]];
  const cls = (i, start) => `keel-fam-${i}${start ? " keel-fam-start" : ""}`;
  const details = element("details", "keel-datatable keel-datatable-stacked");
  details.append(element("summary", null, "Data table"));
  const scroller = element("div", "keel-datatable-scroll");
  const table = element("table");
  table.append(element("caption", null, `Values plotted in this chart (${samples.length} samples), percent of classified conversations.`));
  const thead = element("thead");
  const top = element("tr"), sub = element("tr");
  for (const text of ["Sampled", "Group"]) {
    const th = element("th", null, text);
    th.scope = "col";
    th.rowSpan = 2;
    top.append(th);
  }
  view.families.forEach((f, i) => {
    const th = element("th", `keel-fam ${cls(i, true)}`, `${f.name} patterns`);
    th.colSpan = f.groups.length;
    th.scope = "colgroup";
    top.append(th);
    f.groups.forEach((g, j) => {
      const h = element("th", cls(i, j === 0), name(g));
      h.scope = "col";
      sub.append(h);
    });
  });
  const totals = element("th", "keel-fam keel-fam-start keel-fam-total", "Totals");
  totals.colSpan = view.families.length;
  totals.scope = "colgroup";
  top.append(totals);
  view.families.forEach((f, i) => {
    const h = element("th", cls(i, i === 0), f.name);
    h.scope = "col";
    sub.append(h);
  });
  if (leftOut) {
    const h = element("th", "keel-fam keel-fam-start keel-leftout", view.leftOut.heading);
    h.scope = "colgroup";
    top.append(h);
    const sh = element("th", "keel-fam-start keel-leftout", view.leftOut.label);
    sh.scope = "col";
    sub.append(sh);
  }
  thead.append(top, sub);
  table.append(thead);
  const body = element("tbody");
  for (const s of samples) {
    const tr = element("tr");
    const th = element("th", null, s.period);
    const note = footnotes.find(f => f.key === dateKey(s.date));
    if (note) {
      const sup = element("sup");
      const a = element("a", null, String(note.n));
      a.href = `#${note.id}`;
      a.setAttribute("aria-label", `Note ${note.n}`);
      sup.append(a);
      th.append(sup);
    }
    th.scope = "row";
    const g = element("td");
    const label = element("span", null, groupOf(s.segment).name);
    markTip(label, groupOf(s.segment).tip);
    g.append(label);
    tr.append(th, g);
    view.families.forEach((f, i) => f.groups.forEach((grp, j) =>
      tr.append(element("td", cls(i, j === 0), fmtValue(s.values[grp] ?? 0, meta.units)))));
    view.families.forEach((f, i) => {
      const total = f.groups.reduce((t, grp) => t + (s.values[grp] ?? 0), 0);
      const td = element("td", cls(i, i === 0));
      td.append(element("strong", null, fmtValue(total, meta.units)));
      tr.append(td);
    });
    if (leftOut) {
      const v = leftOut.get(+s.date);
      tr.append(element("td", "keel-fam-start keel-leftout", v == null ? "–" : fmtValue(v, meta.units)));
    }
    body.append(tr);
  }
  table.append(body);
  scroller.append(table);
  details.append(scroller);
  if (leftOut) details.append(element("p", "keel-datatable-note", view.leftOut.note));
  for (const f of footnotes) {
    const p = element("p", "keel-datatable-note");
    p.id = f.id;
    p.append(element("sup", null, String(f.n)), document.createTextNode(" " + f.text));
    details.append(p);
  }
  if (view.groupsLink) {
    const p = element("p", "keel-datatable-note");
    p.append(groupsLinkItem(view.groupsLink, "span"));
    details.append(p);
  }
  return details;
}
