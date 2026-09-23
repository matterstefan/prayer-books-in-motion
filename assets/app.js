"use strict";

const CURRENT_YEAR = 2026;
const DATA_URLS = {
  copies: "data/derived/mei-copies.csv",
  stations: "data/derived/mei-itinerary-stations-resolved.csv",
};

const languageLabels = { lat: "Latein", dut: "Niederländisch", ita: "Italienisch", ger: "Deutsch", chu: "Kirchenslawisch" };
const stationLabels = { print_place: "Druckort", provenance_place: "Provenienzstation", current_holding: "Heutiger Aufbewahrungsort" };
const unresolvedLabels = { ambiguous: "mehrdeutig", country_only: "nur Land bekannt", needs_review: "weitere Prüfung nötig", non_geographic: "keine geografische Angabe" };

const state = {
  year: CURRENT_YEAR,
  copies: [],
  stationsByCopy: new Map(),
  selected: new Set(),
  search: "",
  place: "",
  language: "",
  layers: [],
};

const els = Object.fromEntries([
  "year-slider", "year-output", "search-input", "place-filter", "language-filter",
  "print-list", "result-summary", "reset-button", "select-visible", "clear-visible",
  "detail-panel", "detail-content", "detail-close", "about-panel", "about-button",
  "about-close", "map-message"
].map(id => [id, document.getElementById(id)]));

const map = L.map("map", { zoomControl: true, minZoom: 2, worldCopyJump: true }).setView([48.8, 8.5], 4);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
const routeLayer = L.layerGroup().addTo(map);
const locationLayer = L.layerGroup().addTo(map);

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
function hasPoint(station) { return station.latitude !== "" && station.longitude !== ""; }
function point(station) { return [Number(station.latitude), Number(station.longitude)]; }
function numeric(value) { return value === "" ? null : Number(value); }
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
    if (station.station_type === "current_holding" &&
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
  if (station.station_type === "current_holding") return numeric(station.observation_date.slice(0, 4)) || CURRENT_YEAR;
  return numeric(station.time_start) ?? numeric(station.time_end);
}

function locationAtYear(copyId, year) {
  const stations = copyStations(copyId).filter(hasPoint);
  if (year === CURRENT_YEAR) {
    const current = stations.find(s => s.station_type === "current_holding");
    return current ? { station: current, inferred: false } : null;
  }
  const exact = stations.filter(station => {
    if (station.station_type === "current_holding") return false;
    const start = numeric(station.time_start);
    const end = numeric(station.time_end);
    if (start === null && end === null) return false;
    return (start === null || start <= year) && (end === null || year <= end);
  }).sort((a, b) => Number(b.source_order) - Number(a.source_order));
  if (exact.length) return { station: exact[0], inferred: false };
  const earlier = stations.filter(station => station.station_type !== "current_holding" && stationAnchor(station) !== null && stationAnchor(station) <= year)
    .sort((a, b) => stationAnchor(b) - stationAnchor(a) || Number(b.source_order) - Number(a.source_order));
  return earlier.length ? { station: earlier[0], inferred: true } : null;
}

function routeAtYear(copyId, year) {
  const stations = copyStations(copyId).filter(hasPoint);
  if (year === CURRENT_YEAR) return stations;
  return stations.filter((station, index) => {
    if (station.station_type === "current_holding") return false;
    const anchor = stationAnchor(station);
    if (anchor !== null) return anchor <= year;
    const later = stations.slice(index + 1).map(stationAnchor).find(value => value !== null);
    return later !== undefined && later <= year;
  });
}

function colorFor(id) {
  let hash = 0;
  for (const char of id) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  const hues = [342, 9, 28, 194, 216, 263, 305];
  return `hsl(${hues[hash % hues.length]} 62% 39%)`;
}

function printYear(copy) {
  const station = printStation(copy.copy_id);
  if (!station) return "ohne Datierung";
  return station.time_start === station.time_end ? station.time_start : [station.time_start, station.time_end].filter(Boolean).join("–");
}

function searchable(copy) {
  const station = printStation(copy.copy_id);
  return [copy.title, copy.shelfmark, copy.mei_id, copy.host_istc_id, copy.gw_references, station?.location_label].join(" ").toLocaleLowerCase("de");
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
    <p class="popup-meta">${escapeHtml(station?.location_label || "Druckort ungeklärt")}, ${escapeHtml(printYear(copy))}<br>${escapeHtml(copy.holding_institution_name || "Aufbewahrungsort nicht angegeben")} · ${escapeHtml(copy.shelfmark || "ohne Signatur")}</p>
    <p class="popup-route">${escapeHtml(routeSummary(copy.copy_id))}</p>
    <button class="popup-button" type="button" data-track-id="${escapeHtml(copy.copy_id)}">Druck verfolgen</button>`;
}

function clearMapLayers() {
  routeLayer.clearLayers();
  locationLayer.clearLayers();
}

function renderMap({ fit = false } = {}) {
  clearMapLayers();
  const copies = displayedCopies();
  const bounds = [];
  let located = 0;
  let mappedStations = 0;

  for (const copy of copies) {
    const color = colorFor(copy.copy_id);
    const route = compactMappedRoute(routeAtYear(copy.copy_id, state.year));
    mappedStations += route.length;
    const coordinates = route.map(point);
    coordinates.forEach(value => bounds.push(value));
    if (coordinates.length > 1) {
      const line = L.polyline(coordinates, { color, weight: 3, opacity: .48, lineCap: "round" }).addTo(routeLayer);
      line.bindPopup(popupHtml(copy));
      line.on("mouseover", () => line.setStyle({ weight: 6, opacity: .9 }));
      line.on("mouseout", () => line.setStyle({ weight: 3, opacity: .48 }));
    }
    const location = locationAtYear(copy.copy_id, state.year);
    if (location) {
      located += 1;
      const marker = L.circleMarker(point(location.station), {
        radius: 6,
        color,
        weight: 2,
        fillColor: location.inferred ? "#ffffff" : color,
        fillOpacity: 1
      }).addTo(locationLayer);
      marker.bindPopup(popupHtml(copy));
      marker.bindTooltip(`${copy.title || "Ohne Titel"} · ${location.station.location_label}`, { direction: "top", opacity: .94 });
      bounds.push(point(location.station));
    }
  }

  els["result-summary"].textContent = `${copies.length} Drucke angezeigt · ${located} im Jahr ${state.year} verortet · ${mappedStations} dargestellte Wegpunkte`;
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
      <span class="print-meta">${escapeHtml(station?.location_label || "Druckort ungeklärt")} · ${escapeHtml(printYear(copy))} · ${escapeHtml(languageLabels[copy.language] || copy.language)}<br>${escapeHtml(copy.holding_institution_name || "Aufbewahrungsort nicht angegeben")} · <span class="print-id">${escapeHtml(copy.shelfmark || copy.mei_id)}</span></span>
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
    return historical === "nicht datiert" ? current : `als Bibliotheksstation ${historical}; ${current}`;
  }
  return historicalStationTime(station);
}

function openDetail(copyId) {
  const copy = state.copies.find(item => item.copy_id === copyId);
  if (!copy) return;
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
      <dt>Aufbewahrung</dt><dd>${escapeHtml(copy.holding_institution_name || "nicht angegeben")}</dd>
    </dl>
    <h3>Überlieferte Stationen</h3>
    <ol class="station-list">${stations.map(station => {
      const unresolved = unresolvedLabels[station.location_resolution_status];
      return `<li class="station-item"><span class="station-type">${escapeHtml(stationLabels[station.station_type] || station.station_type)}</span>
        <span class="station-place">${escapeHtml(station.location_label || station.place_name || "Ort nicht angegeben")}</span>
        <span class="station-time">${escapeHtml(stationTime(station))}</span>
        ${unresolved ? `<span class="uncertain-badge">${escapeHtml(unresolved)}</span>` : ""}
        ${station.mergedProvenance ? `<span class="station-note">Orts- und Institutionsangabe aus zwei aufeinanderfolgenden MEI-Stationen zusammengeführt.</span>` : ""}
        ${station.location_resolution_note ? `<span class="station-note">${escapeHtml(station.location_resolution_note)}</span>` : ""}
        ${station.source_url ? `<a class="station-source" href="${escapeHtml(station.source_url)}" target="_blank" rel="noopener">Quelle: ${escapeHtml(station.source_catalogue)}</a>` : ""}
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
    state.year = CURRENT_YEAR; state.search = ""; state.place = ""; state.language = "";
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
