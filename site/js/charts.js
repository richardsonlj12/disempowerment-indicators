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
