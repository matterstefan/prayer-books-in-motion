"use strict";

const CURRENT_YEAR = 2026;
const DATA_URLS = {
  copies: "data/expanded/tables/mei-copies.csv",
  stations: "data/expanded/tables/mei-itinerary-stations-resolved.csv",
};

const languageLabels = { lat: "Latein", dut: "Niederländisch", ita: "Italienisch", ger: "Deutsch", chu: "Kirchenslawisch", frm: "Mittelfranzösisch", fre: "Französisch", eng: "Englisch", spa: "Spanisch" };
const stationLabels = { print_place: "Druckort", provenance_place: "Provenienzstation", current_holding: "Heutiger Aufbewahrungsort", last_known: "Letzter bekannter Aufenthaltsort" };
const unresolvedLabels = { ambiguous: "mehrdeutig", country_only: "nur Land bekannt", needs_review: "weitere Prüfung nötig", non_geographic: "keine geografische Angabe" };

const state = {
  view: "connections",
  year: CURRENT_YEAR,
  copies: [],
  stationsByCopy: new Map(),
  selected: new Set(),
  search: "",
  place: "",
  language: "",
  layers: [],
  focusedCopy: null,
  hoveredCopy: null,
  focusedBundle: null,
  hoveredBundle: null,
};

const els = Object.fromEntries([
  "year-slider", "year-output", "search-input", "place-filter", "language-filter",
  "print-list", "result-summary", "reset-button", "select-visible", "clear-visible",
  "detail-panel", "detail-content", "detail-close", "about-panel", "about-button",
  "about-close", "map-message", "clear-focus", "view-connections", "view-locations", "connection-legend", "location-legend"
].map(id => [id, document.getElementById(id)]));

const map = L.map("map", { zoomControl: true, minZoom: 2, worldCopyJump: true }).setView([48.8, 8.5], 4);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
const routeLayer = L.layerGroup().addTo(map);
const locationLayer = L.layerGroup().addTo(map);
const highlightLayer = L.layerGroup().addTo(map);

function parseCsv(text) {
  const rows = [];
  let row = [], value = "", quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') { value += '"'; i += 1; }
      else if (char === '"') quoted = false;
      else value += char;
    } else if (char === '"') quoted = true;
    else if (char === ",") { row.push(value); value = ""; }
    else if (char === "\n") { row.push(value.replace(/\r$/, "")); rows.push(row); row = []; value = ""; }
    else value += char;
  }
  if (value || row.length) { row.push(value); rows.push(row); }
  const headers = rows.shift() || [];
  return rows.filter(r => r.some(Boolean)).map(values => Object.fromEntries(headers.map((header, index) => [header, values[index] || ""])));
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

function directCopy(copy) { return copy.relationship_types.split(" | ").includes("direct"); }
function hasPoint(station) { return station.latitude !== "" && station.longitude !== "" && Number.isFinite(Number(station.latitude)) && Number.isFinite(Number(station.longitude)) && Math.abs(Number(station.latitude)) <= 90 && Math.abs(Number(station.longitude)) <= 180; }
function point(station) { return [Number(station.latitude), Number(station.longitude)]; }
function numeric(value) { return value == null || value === "" || !Number.isFinite(Number(value)) ? null : Number(value); }
function copyStations(copyId) { return state.stationsByCopy.get(copyId) || []; }
function printStation(copyId) { return copyStations(copyId).find(s => s.station_type === "print_place"); }
function samePoint(first, second) {
  return Boolean(first && second && first.latitude && second.latitude &&
    first.latitude === second.latitude && first.longitude === second.longitude);
}

function compactStationsForDisplay(copyId) {
  const compacted = [];
  for (const station of copyStations(copyId)) {
    const previous = compacted.at(-1);
    if (["current_holding", "last_known"].includes(station.station_type) &&
        previous?.station_type === "provenance_place" && samePoint(previous, station)) {
      compacted[compacted.length - 1] = { ...station, mergedProvenance: previous };
    } else {
      compacted.push(station);
    }
  }
  return compacted;
}

function compactMappedRoute(stations) {
  const compacted = [];
  for (const station of stations) {
    if (samePoint(compacted.at(-1), station)) compacted[compacted.length - 1] = station;
    else compacted.push(station);
  }
  return compacted;
}

function stationAnchor(station) {
  if (station.date_warning) return null;
  if (station.station_type === "current_holding") return numeric(station.observation_date.slice(0, 4)) || CURRENT_YEAR;
  return numeric(station.time_start) ?? numeric(station.time_end);
}

function locationAtYear(copyId, year) {
  const all = copyStations(copyId);
  const birth = stationAnchor(printStation(copyId) || {});
  if (birth !== null && year < birth) return null;
  if (year === CURRENT_YEAR) {
    const current = all.find(s => s.station_type === "current_holding");
    if (current) return hasPoint(current) ? { station: current, inferred: Boolean(current.display_uncertainty) } : null;
    const last = all.find(s => s.station_type === "last_known");
    return last && hasPoint(last) ? { station: last, inferred: true } : null;
  }
  // Follow source order. A later unlocated event interrupts any carried location.
  const eligible = all.filter(s => s.station_type !== "current_holding" && !s.date_warning && stationAnchor(s) !== null && stationAnchor(s) <= year);
  const latest = eligible.at(-1);
  if (!latest || !hasPoint(latest)) return null;
  const start = numeric(latest.time_start), end = numeric(latest.time_end);
  const bounded = start !== null && end !== null && start <= year && year <= end;
  return { station: latest, inferred: !bounded || Boolean(latest.display_uncertainty) };
}

function routeAtYear(copyId, year) {
  const stations = copyStations(copyId);
  const birth = stationAnchor(printStation(copyId) || {});
  if (birth !== null && year < birth) return [];
  if (year === CURRENT_YEAR) return stations.filter(hasPoint);
  return stations.filter(station => station.station_type !== "current_holding" &&
    !station.date_warning && stationAnchor(station) !== null && stationAnchor(station) <= year && hasPoint(station));
}

function holdingLabel(copy) {
  return ["Historical Copy", "Trade Copy"].includes(copy.holding_institution_name)
    ? "Heutiger Aufenthaltsort unbekannt" : copy.holding_institution_name || "Aufbewahrungsort nicht angegeben";
}

function segmentEvidence(from, to, all) {
  const reasons = [];
  if ([from, to].some(s => s.display_uncertainty || s.spatial_precision === "country")) reasons.push("Ortszuweisung unsicher oder nur näherungsweise");
  if ([from, to].some(s => s.date_warning)) reasons.push("Widersprüchliche Datierung");
  const middle = all.slice(all.indexOf(from) + 1, all.indexOf(to));
  if (middle.length || Number(to.source_order) - Number(from.source_order) > 1) reasons.push("Dazwischenliegende Nachweise nicht dargestellt");
  const end = numeric(from.time_end), start = numeric(to.time_start);
  if (end === null || start === null) reasons.push("Übergang nicht ausreichend datiert");
  else if (start > end + 1) reasons.push("Zeitliche Lücke zwischen den Nachweisen");
  else if (start < (numeric(from.time_start) ?? end)) reasons.push("Zeitliche Reihenfolge nicht eindeutig");
  if (Number(from.source_order) === Number(to.source_order)) reasons.push("Orte desselben Quellenblocks; keine gesicherte Abfolge");
  return { dashed: reasons.length > 0, description: reasons.length ? reasons.join("; ") : "Datierte Ortsfolge ohne erkennbare Lücke in den dargestellten Nachweisen" };
}

function updateRouteFocus() {
  const highlighted = state.focusedCopy ? new Set([state.focusedCopy]) : state.focusedBundle || (state.hoveredCopy ? new Set([state.hoveredCopy]) : state.hoveredBundle);
  highlightLayer.clearLayers();
  for (const item of state.layers) {
    const active = highlighted && [...(item.copyIds || [item.copyId])].some(id => highlighted.has(id));
    const muted = highlighted && !active;
    item.layer.setStyle({ weight: active ? (item.marker ? 3 : Math.max(6, item.baseWeight || 3)) : (item.marker ? 2 : item.baseWeight || 3), opacity: muted ? .12 : active ? 1 : .55, ...(item.marker ? { fillOpacity: muted ? .15 : 1 } : {}) });
    if (active) item.layer.bringToFront();
  }
  if (highlighted && state.view === "connections") for (const id of highlighted) {
    const route = routeAtYear(id, state.year);
    for (let i = 1; i < route.length; i++) {
      if (samePoint(route[i-1], route[i])) continue;
      const evidence = segmentEvidence(route[i-1], route[i], copyStations(id));
      L.polyline([point(route[i-1]), point(route[i])], {color:colorFor(id),weight:5,opacity:.95,dashArray:evidence.dashed?"6 5":null,interactive:false}).addTo(highlightLayer);
    }
  }
  els["clear-focus"].hidden = !state.focusedCopy && !state.focusedBundle;
}

function focusCopy(copyId) {
  state.focusedCopy = copyId;
  state.hoveredCopy = null;
  state.focusedBundle = null;
  state.hoveredBundle = null;
  updateRouteFocus();
}

function hoverCopy(copyId) {
  state.hoveredCopy = copyId;
  state.hoveredBundle = null;
  updateRouteFocus();
}

function bundleRoutes(copies, year) {
  const groups = new Map();
  const keyFor = s => point(s).map(n => n.toFixed(5)).join(",");
  for (const copy of copies) {
    const route = routeAtYear(copy.copy_id, year);
    for (let i=1;i<route.length;i++) {
      const from=route[i-1],to=route[i],a=keyFor(from),b=keyFor(to);
      if(a===b) continue;
      // Opposite directions share geometry, but remain separately labelled in the popup.
      const key=[a,b].sort().join("|");
      if(!groups.has(key)) groups.set(key,{key,from,to,entries:new Map()});
      const group=groups.get(key),id=copy.copy_id;
      if(!group.entries.has(id)) group.entries.set(id,{copy,legs:[]});
      group.entries.get(id).legs.push({from,to,evidence:segmentEvidence(from,to,copyStations(id))});
    }
  }
  return [...groups.values()];
}

function bundlePopup(group) {
  const entries=[...group.entries.values()];
  const name=s=>s.preferred_placename || s.place_name || s.location_label;
  return `<h3>${escapeHtml(name(group.from))} ↔ ${escapeHtml(name(group.to))}</h3>
    <p>${entries.length} ${entries.length===1?"Exemplar":"Exemplare"} in dieser Auswahl</p>
    <p class="method-note">Gemeinsame Ortsverbindung, keine gemeinsam belegte Reise. Richtung und Einstufung stehen beim jeweiligen Druck.</p>
    <div class="bundle-list" tabindex="0" aria-label="Beteiligte Drucke">${entries.map(({copy,legs})=>`<div class="bundle-copy">
      ${popupHtml(copy)}
      <p class="popup-meta">${[...new Set(legs.map(l=>`${name(l.from)} → ${name(l.to)}: ${l.evidence.description}`))].map(escapeHtml).join("<br>")}</p>
    </div>`).join("")}</div>`;
}

function colorFor(id) {
  let hash = 0;
  for (const char of id) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  const hues = [342, 9, 28, 194, 216, 263, 305];
  return `hsl(${hues[hash % hues.length]} 62% 39%)`;
}

function printYear(copy) {
  const station = printStation(copy.copy_id);
  if (!station || (!station.time_start && !station.time_end)) return "ohne Datierung";
  return station.time_start === station.time_end ? station.time_start : [station.time_start, station.time_end].filter(Boolean).join("–");
}

function searchable(copy) {
  const station = printStation(copy.copy_id);
  return [copy.title, copy.holding_institution_name, copy.shelfmark, copy.mei_id, copy.host_istc_id, copy.gw_references, station?.location_label].join(" ").toLocaleLowerCase("de");
}

function matchesFilters(copy) {
  const station = printStation(copy.copy_id);
  return (!state.search || searchable(copy).includes(state.search)) &&
    (!state.place || station?.location_label === state.place) &&
    (!state.language || copy.language === state.language);
}

function filteredCopies() { return state.copies.filter(matchesFilters); }
function displayedCopies() { return filteredCopies().filter(copy => state.selected.has(copy.copy_id)); }

function routeSummary(copyId) {
  const names = compactStationsForDisplay(copyId).map(s => s.location_label || s.preferred_placename || s.place_name).filter(Boolean);
  return names.filter((name, index) => index === 0 || name !== names[index - 1]).join(" → ");
}

function popupHtml(copy) {
  const station = printStation(copy.copy_id);
  return `<h3>${escapeHtml(copy.title || "Ohne Titel")}</h3>
    <p class="popup-meta">${escapeHtml(station?.location_label || "Druckort ungeklärt")}, ${escapeHtml(printYear(copy))}<br>${escapeHtml(holdingLabel(copy))} · ${escapeHtml(copy.shelfmark || "ohne Signatur")}</p>
    <p class="popup-route">${escapeHtml(routeSummary(copy.copy_id))}</p>
    <button class="popup-button" type="button" data-track-id="${escapeHtml(copy.copy_id)}">Druck verfolgen</button>`;
}

function clearMapLayers() {
  state.hoveredCopy = null;
  state.hoveredBundle = null;
  state.focusedBundle = null;
  state.layers = [];
  routeLayer.clearLayers();
  locationLayer.clearLayers();
  highlightLayer.clearLayers();
}

function groupLocations(copies, year) {
  const groups = new Map();
  for (const copy of copies) {
    const location = locationAtYear(copy.copy_id, year);
    if (!location) continue;
    const station = location.station;
    const key = point(station).map(n => n.toFixed(5)).join(",") + "|" + (station.spatial_precision === "country" ? "country" : "locality");
    if (!groups.has(key)) groups.set(key, { station, entries: new Map() });
    groups.get(key).entries.set(copy.copy_id, { copy, ...location });
  }
  return [...groups.values()];
}

function locationPopup(group) {
  const entries = [...group.entries.values()];
  const names = [...new Set(entries.map(e => e.station.preferred_placename || e.station.place_name || e.station.location_label))];
  return `<h3>${names.map(escapeHtml).join(" / ")} · ${state.year}</h3>
    <p>${entries.length} Exemplare am letzten zuweisbaren Ort bis ${state.year}.</p>
    <p class="method-note">Gemeinsamer Kartenpunkt, kein Beleg für gleichzeitigen Besitz oder ununterbrochenen Aufenthalt.</p>
    <div class="bundle-list" tabindex="0" aria-label="Drucke an diesem Kartenpunkt">${entries.map(({copy, station}) => `<div class="bundle-copy">${popupHtml(copy)}
      <p class="popup-meta">${escapeHtml(station.location_label)} · ${escapeHtml(stationTime(station))}${station.display_uncertainty ? " · " + escapeHtml(station.display_uncertainty) : ""}</p></div>`).join("")}</div>`;
}

function renderLocations(copies, fit) {
  const groups = groupLocations(copies, state.year);
  let located = 0;
  // Large circles first so smaller nearby circles remain selectable.
  groups.sort((a, b) => b.entries.size - a.entries.size);
  for (const group of groups) {
    const entries = [...group.entries.values()], ids = new Set(group.entries.keys());
    located += entries.length;
    const marker = L.circleMarker(point(group.station), {
      radius: 6 * Math.sqrt(entries.length), color: "#75132f", weight: 2,
      fillColor: "#75132f", fillOpacity: 1,
      dashArray: group.station.spatial_precision === "country" ? "3 3" : null,
      bubblingMouseEvents: false
    }).addTo(locationLayer);
    state.layers.push({layer: marker, copyIds: ids, marker: true});
    marker.bindPopup(locationPopup(group), {autoPan: false, maxWidth: 380});
    marker.bindTooltip(`${escapeHtml(group.station.preferred_placename || group.station.place_name || group.station.location_label)} · ${entries.length} Exemplare`);
    marker.on("click", () => { state.focusedCopy = null; state.focusedBundle = ids; state.hoveredBundle = null; updateRouteFocus(); });
    marker.on("mouseover", () => { state.hoveredBundle = ids; updateRouteFocus(); });
    marker.on("mouseout", () => { state.hoveredBundle = null; updateRouteFocus(); });
  }
  updateRouteFocus();
  const notPrinted = copies.filter(c => { const birth = stationAnchor(printStation(c.copy_id) || {}); return birth !== null && birth > state.year; }).length;
  els["result-summary"].textContent = `${copies.length} Drucke ausgewählt · ${located} an ${groups.length} Kartenpunkten für ${state.year} · ${notPrinted} noch nicht gedruckt · ${copies.length - located - notPrinted} ohne zuweisbaren Ort`;
  els["map-message"].hidden = groups.length > 0;
  els["map-message"].textContent = copies.length ? "Für dieses Jahr und diese Auswahl ist kein Kartenpunkt zuweisbar." : "Für diese Auswahl sind keine Drucke markiert.";
  if (fit && groups.length) map.fitBounds(groups.map(g => point(g.station)), {padding: [34, 34], maxZoom: 6});
}

function setMapView(view) {
  state.view = view;
  map.closePopup();
  els["view-connections"].setAttribute("aria-pressed", String(view === "connections"));
  els["view-locations"].setAttribute("aria-pressed", String(view === "locations"));
  els["connection-legend"].hidden = view !== "connections";
  els["location-legend"].hidden = view !== "locations";
  render({list: false});
}

function renderMap({ fit = false } = {}) {
  clearMapLayers();
  const copies = displayedCopies();
  if (!copies.some(c => c.copy_id === state.focusedCopy)) state.focusedCopy = null;
  if (state.view === "locations") { renderLocations(copies, fit); return; }
  const bounds = [];
  let located = 0;
  let mappedStations = 0;

  for (const copy of copies) {
    const color = colorFor(copy.copy_id);
    const route = routeAtYear(copy.copy_id, state.year);
    mappedStations += route.length;
    const coordinates = route.map(point);
    coordinates.forEach(value => bounds.push(value));
    const location = locationAtYear(copy.copy_id, state.year);
    if (location) {
      located += 1;
      const marker = L.circleMarker(point(location.station), {
        radius: location.station.spatial_precision === "country" ? 11 : 6,
        bubblingMouseEvents: false,
        dashArray: location.station.spatial_precision === "country" ? "3 3" : null,
        color,
        weight: 2,
        fillColor: location.inferred ? "#ffffff" : color,
        fillOpacity: 1
      }).addTo(locationLayer);
      state.layers.push({ layer: marker, copyId: copy.copy_id, marker: true });
      marker.bindPopup(popupHtml(copy), { autoPan: false });
      marker.on("click", () => focusCopy(copy.copy_id));
      marker.on("mouseover", () => hoverCopy(copy.copy_id));
      marker.on("mouseout", () => hoverCopy(null));
      marker.bindTooltip(`${copy.title || "Ohne Titel"} · ${location.station.location_label}${location.inferred ? " · Annäherung / letzter Nachweis" : ""}${location.station.display_uncertainty ? " · " + location.station.display_uncertainty : ""}`, { direction: "top", opacity: .94 });
      bounds.push(point(location.station));
    }
  }

  const bundles = bundleRoutes(copies, state.year);
  for (const group of bundles) {
    const ids=new Set(group.entries.keys()),single=ids.size===1;
    const legs=[...group.entries.values()].flatMap(e=>e.legs);
    const dashed=legs.some(l=>l.evidence.dashed);
    const weight=2+Math.log2(ids.size+1)*1.5;
    const line=L.polyline([point(group.from),point(group.to)],{color:single?colorFor([...ids][0]):"#596674",weight,opacity:.55,dashArray:dashed?"6 5":null,bubblingMouseEvents:false}).addTo(routeLayer);
    state.layers.push({layer:line,copyIds:ids,copyId:single?[...ids][0]:null,baseWeight:weight,marker:false});
    line.bindPopup(bundlePopup(group),{autoPan:false,maxWidth:380});
    line.bindTooltip(`${ids.size} ${single?"Exemplar":"Exemplare"} · ${group.from.preferred_placename || group.from.location_label} ↔ ${group.to.preferred_placename || group.to.location_label}`);
    line.on("click",()=>{state.focusedCopy=single?[...ids][0]:null;state.focusedBundle=single?null:ids;state.hoveredCopy=null;state.hoveredBundle=null;updateRouteFocus()});
    line.on("mouseover",()=>{state.hoveredCopy=null;state.hoveredBundle=ids;updateRouteFocus()});
    line.on("mouseout",()=>{state.hoveredBundle=null;updateRouteFocus()});
  }
  updateRouteFocus();

  els["result-summary"].textContent = `${copies.length} Drucke angezeigt · ${located} mit Kartenpunkt für ${state.year} · ${mappedStations} dargestellte Wegpunkte`;
  els["map-message"].hidden = copies.length > 0;
  els["map-message"].textContent = copies.length ? "" : "Für diese Auswahl sind keine Drucke markiert.";
  if (fit && bounds.length) map.fitBounds(bounds, { padding: [34, 34], maxZoom: 6 });
}

function renderList() {
  const copies = filteredCopies();
  els["print-list"].innerHTML = copies.map(copy => {
    const station = printStation(copy.copy_id);
    const checked = state.selected.has(copy.copy_id);
    return `<div class="print-card ${checked ? "" : "is-unselected"}" data-copy-card="${escapeHtml(copy.copy_id)}">
      <input type="checkbox" data-copy-select="${escapeHtml(copy.copy_id)}" aria-label="Druck anzeigen: ${escapeHtml(copy.title || copy.copy_id)}" ${checked ? "checked" : ""}>
      <button class="print-card-body" type="button" data-copy-detail="${escapeHtml(copy.copy_id)}"><span class="print-title">${escapeHtml(copy.title || "Ohne Titel")}</span>
      <span class="print-meta">${escapeHtml(station?.location_label || "Druckort ungeklärt")} · ${escapeHtml(printYear(copy))} · ${escapeHtml(languageLabels[copy.language] || copy.language)}<br>${escapeHtml(holdingLabel(copy))} · <span class="print-id">${escapeHtml(copy.shelfmark || copy.mei_id)}</span></span>
      </button></div>`;
  }).join("");
}

function render({ fit = false, list = true } = {}) {
  els["year-output"].value = String(state.year);
  els["year-output"].textContent = String(state.year);
  if (list) renderList();
  renderMap({ fit });
}

function historicalStationTime(station) {
  if (station.time_start && station.time_end && station.time_start !== station.time_end) return `${station.time_start}–${station.time_end}`;
  return station.time_start || station.time_end || "nicht datiert";
}

function stationTime(station) {
  if (station.station_type === "current_holding") {
    const current = `Stand ${station.observation_date || CURRENT_YEAR}`;
    if (!station.mergedProvenance) return current;
    const historical = historicalStationTime(station.mergedProvenance);
    return historical === "nicht datiert" ? current : `Ortsnachweis ${historical}; ${current}`;
  }
  return historicalStationTime(station);
}

function openDetail(copyId) {
  const copy = state.copies.find(item => item.copy_id === copyId);
  if (!copy) return;
  focusCopy(copyId);
  const stations = compactStationsForDisplay(copyId);
  const print = printStation(copyId);
  els["detail-content"].innerHTML = `
    <h2 id="detail-title">${escapeHtml(copy.title || "Ohne Titel")}</h2>
    <p class="detail-lead">${escapeHtml(print?.location_label || "Druckort ungeklärt")}, ${escapeHtml(printYear(copy))} · ${escapeHtml(copy.shelfmark || "ohne Signatur")}</p>
    <dl class="detail-facts">
      <dt>MEI</dt><dd><a href="${escapeHtml(copy.mei_url)}" target="_blank" rel="noopener">${escapeHtml(copy.mei_id)}</a></dd>
      <dt>ISTC</dt><dd><a href="https://data.cerl.org/istc/${escapeHtml(copy.host_istc_id)}" target="_blank" rel="noopener">${escapeHtml(copy.host_istc_id)}</a></dd>
      <dt>GW</dt><dd>${escapeHtml(copy.gw_references || "nicht angegeben")}</dd>
      <dt>Sprache</dt><dd>${escapeHtml(languageLabels[copy.language] || copy.language || "nicht angegeben")}</dd>
      <dt>Aufbewahrung</dt><dd>${escapeHtml(holdingLabel(copy))}</dd>
    </dl>
    <h3>Überlieferte Stationen</h3>
    <p class="method-note">Die Liste zeigt die Gesamtfolge. Zeitliche Lücken, undatierte Stationen und fehlende Ortsangaben erlauben keinen lückenlosen Aufenthaltsnachweis.</p>
    <ol class="station-list">${stations.map(station => {
      const unresolved = station.date_warning || station.display_uncertainty || unresolvedLabels[station.location_resolution_status];
      return `<li class="station-item"><span class="station-type">${escapeHtml(stationLabels[station.station_type] || station.station_type)}</span>
        <span class="station-place">${escapeHtml(station.location_label || station.place_name || "Ort nicht angegeben")}</span>
        <span class="station-time">${escapeHtml(stationTime(station))}</span>
        ${unresolved ? `<span class="uncertain-badge">${escapeHtml(unresolved)}</span>` : ""}
        ${station.mergedProvenance ? `<span class="station-note">Gleicher Kartenort zusammengefasst; der Ortsnachweis datiert nicht automatisch den Zugang zur heutigen Institution.</span>` : ""}
        ${station.location_resolution_note ? `<span class="station-note">${escapeHtml(station.location_resolution_note)}</span>` : ""}
        ${(station.source_url || "").split(" | ").filter(url => /^https?:\/\//.test(url)).map(url => `<a class="station-source" href="${escapeHtml(url)}" target="_blank" rel="noopener">Quelle: ${escapeHtml(station.source_catalogue)}</a>`).join(" ")}
      </li>`;
    }).join("")}</ol>`;
  els["about-panel"].classList.remove("is-open");
  els["about-panel"].setAttribute("aria-hidden", "true");
  els["detail-panel"].classList.add("is-open");
  els["detail-panel"].setAttribute("aria-hidden", "false");
  els["detail-close"].focus();
}

function closePanel(panel) {
  panel.classList.remove("is-open");
  panel.setAttribute("aria-hidden", "true");
}

function populateFilters() {
  const places = [...new Set(state.copies.map(copy => printStation(copy.copy_id)?.location_label).filter(Boolean))].sort((a, b) => a.localeCompare(b, "de"));
  const languages = [...new Set(state.copies.map(copy => copy.language).filter(Boolean))].sort();
  els["place-filter"].insertAdjacentHTML("beforeend", places.map(value => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join(""));
  els["language-filter"].insertAdjacentHTML("beforeend", languages.map(value => `<option value="${escapeHtml(value)}">${escapeHtml(languageLabels[value] || value)}</option>`).join(""));
}

function bindEvents() {
  els["view-connections"].addEventListener("click", () => setMapView("connections"));
  els["view-locations"].addEventListener("click", () => setMapView("locations"));
  map.on("click", () => { focusCopy(null); closePanel(els["detail-panel"]); });
  els["clear-focus"].addEventListener("click", () => { focusCopy(null); map.closePopup(); closePanel(els["detail-panel"]); });
  els["year-slider"].addEventListener("input", event => { state.year = Number(event.target.value); render({ list: false }); });
  els["search-input"].addEventListener("input", event => { state.search = event.target.value.trim().toLocaleLowerCase("de"); render(); });
  els["place-filter"].addEventListener("change", event => { state.place = event.target.value; render({ fit: true }); });
  els["language-filter"].addEventListener("change", event => { state.language = event.target.value; render({ fit: true }); });
  els["print-list"].addEventListener("change", event => {
    const id = event.target.dataset.copySelect;
    if (!id) return;
    event.target.checked ? state.selected.add(id) : state.selected.delete(id);
    render();
  });
  els["print-list"].addEventListener("click", event => {
    const button = event.target.closest("[data-copy-detail]");
    if (button) openDetail(button.dataset.copyDetail);
  });
  els["select-visible"].addEventListener("click", () => { filteredCopies().forEach(copy => state.selected.add(copy.copy_id)); render({ fit: true }); });
  els["clear-visible"].addEventListener("click", () => { filteredCopies().forEach(copy => state.selected.delete(copy.copy_id)); render(); });
  els["reset-button"].addEventListener("click", () => {
    state.year = CURRENT_YEAR; state.search = ""; state.place = ""; state.language = ""; state.focusedCopy = null;
    state.copies.forEach(copy => state.selected.add(copy.copy_id));
    els["year-slider"].value = CURRENT_YEAR; els["search-input"].value = ""; els["place-filter"].value = ""; els["language-filter"].value = "";
    render({ fit: true });
  });
  document.getElementById("map").addEventListener("click", event => {
    const button = event.target.closest("[data-track-id]");
    if (button) openDetail(button.dataset.trackId);
  });
  els["detail-close"].addEventListener("click", () => closePanel(els["detail-panel"]));
  els["about-button"].addEventListener("click", () => {
    closePanel(els["detail-panel"]); els["about-panel"].classList.add("is-open"); els["about-panel"].setAttribute("aria-hidden", "false"); els["about-close"].focus();
  });
  els["about-close"].addEventListener("click", () => closePanel(els["about-panel"]));
  document.addEventListener("keydown", event => { if (event.key === "Escape") { closePanel(els["detail-panel"]); closePanel(els["about-panel"]); } });
}

async function loadData() {
  try {
    const [copyResponse, stationResponse] = await Promise.all(Object.values(DATA_URLS).map(url => fetch(url)));
    if (!copyResponse.ok || !stationResponse.ok) throw new Error("Datendateien konnten nicht geladen werden.");
    const [copies, stations] = await Promise.all([copyResponse.text().then(parseCsv), stationResponse.text().then(parseCsv)]);
    state.copies = copies.filter(directCopy).sort((a, b) => (a.title || "").localeCompare(b.title || "", "de"));
    for (const station of stations) {
      if (!state.stationsByCopy.has(station.copy_id)) state.stationsByCopy.set(station.copy_id, []);
      state.stationsByCopy.get(station.copy_id).push(station);
    }
    for (const values of state.stationsByCopy.values()) values.sort((a, b) => Number(a.source_order) - Number(b.source_order) || Number(a.place_order_within_source) - Number(b.place_order_within_source));
    state.copies.forEach(copy => state.selected.add(copy.copy_id));
    populateFilters(); bindEvents(); render({ fit: true });
  } catch (error) {
    els["result-summary"].textContent = "Die Kartendaten konnten nicht geladen werden.";
    els["map-message"].hidden = false;
    els["map-message"].textContent = `${error.message} Bitte die Seite über einen Webserver oder GitHub Pages öffnen.`;
  }
}

loadData();
