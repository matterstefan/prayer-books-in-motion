"use strict";

const CURRENT_YEAR = 2026;
const DATA_URLS = {
  copies: "data/map/copies.csv?v=20261010-2",
  stations: "data/map/stations.csv?v=20261010-2",
};

const languageLabels = { lat: "Latin", dut: "Dutch", ita: "Italian", ger: "German", chu: "Church Slavonic", frm: "Middle French", fre: "French", eng: "English", spa: "Spanish" };
const stationLabels = { print_place: "Printing place", provenance_place: "Provenance record", current_holding: "Current holding location", last_known: "Last known location" };
const unresolvedLabels = { ambiguous: "ambiguous", country_only: "country only", needs_review: "further review needed", non_geographic: "no geographical information" };

const state = {
  view: "connections",
  locationStyle: "circles",
  bundleStrength: 32,
  lineScale: 1.5,
  focusedSegment: null,
  hoveredSegment: null,
  selectedConnection: null,
  returnConnection: null,
  detailIsOpen: false,
  year: CURRENT_YEAR,
  copies: [],
  stationsByCopy: new Map(),
  selected: new Set(),
  collections: new Set(["core"]),
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
  "location-style-controls", "style-circles", "style-heatmap", "heatmap-legend", "circle-legend",
  "collection-core", "collection-liturgy", "collection-devotional",
  "year-slider", "year-output", "search-input", "place-filter", "language-filter",
  "print-list", "result-summary", "reset-button", "select-visible", "clear-visible",
  "detail-panel", "detail-content", "detail-close", "about-panel", "about-button",
  "about-close", "map-message", "clear-focus", "view-connections", "view-locations", "connection-legend", "location-legend", "bundle-panel", "bundle-content", "bundle-close", "bundle-strength", "line-scale", "bundle-value", "line-value", "bundle-controls"
].map(id => [id, document.getElementById(id)]));

const map = L.map("map", {
  zoomControl: true, minZoom: 2, worldCopyJump: true,
  zoomSnap: 0.25, zoomDelta: 0.25, wheelPxPerZoomLevel: 120
}).setView([48.8, 8.5], 4);
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
// Approved display-only alignments, 2026-10-03. Source coordinates stay intact.
const displayPointAliases = new Map([
  ["45.43890,12.33092", [45.43713,12.33265]], // Venice
  ["49.45410,11.07680", [49.45421,11.07752]], // Nuremberg
  ["45.46416,9.19199", [45.46427,9.18951]], // Milan
  ["51.22047,4.40026", [51.21989,4.40346]], // Antwerp
  ["52.06866,4.28635", [52.07667,4.29861]], // The Hague
  ["52.37302,4.89856", [52.37403,4.88969]], // Amsterdam
  ["35.89833,14.51250", [35.89968,14.5148]], // Valletta
  ["41.90268,12.45414", [41.90225,12.4533]], // Vatican City
  ["41.31121,-72.92649", [41.30815,-72.92816]], // Yale / New Haven
  ["52.80900,1.23100", [52.8118,1.2318]], // Blickling Estate / Hall
  ["45.05000,7.66667", [45.07049,7.68682]], // Turin municipality / city
]);
const countryPlaceIds = new Set(["3017382", "2921044", "3175395", "798544", "2658434", "6252001", "6269131"]);
const regionPlaceIds = new Set(["2951839", "2655856", "3174618", "6254927", "3164604"]);
function spatialPrecision(station) {
  const id = (station.place_authority_id || "").trim();
  if (station.place_authority === "GeoNames") {
    if (countryPlaceIds.has(id)) return "country";
    if (regionPlaceIds.has(id)) return "region";
  }
  return station.spatial_precision || "locality";
}
function isArea(station) { return ["country", "region", "area"].includes(spatialPrecision(station)); }
function spatialNote(station) {
  if (excludedDisplayPoint(station)) return "Broad area only; no local map point";
  return isArea(station) ? `${spatialPrecision(station) === "country" ? "Country" : "Region"} only; representative point, not a precise location` : "";
}
function reviewedStation(station) {
  if (station.geolocation_certainty === "probable") station = {...station, display_uncertainty: "Probable place identification"};
  // Narrow correction: do not silently apply it to a changed future source record.
  if (station.station_id !== "02128182-p003-loc01" || station.place_authority_id !== "3570675" || station.time_start !== "1700" || station.time_end !== "1800") return station;
  return {...station, source_location_label: station.location_label,
    source_latitude: station.latitude, source_longitude: station.longitude,
    location_label: "France, precise location unknown", preferred_placename: "France", place_name: "France",
    latitude: "46", longitude: "2", country: "France", spatial_precision: "country",
    display_uncertainty: "Only France is supported; precise location unknown",
    location_resolution_note: "Display decision, 3 October 2026: area code e-fr and review by Stefan Matter support France. The conflicting Fort-de-France reference (GeoNames 3570675) is not mapped. Original data are retained."};
}
function excludedDisplayPoint(station) {
  if (["suppress_broad_area", "no_locality_point"].includes(station.map_point_policy)) return true;
  return station.place_authority === "GeoNames" && ["6255148", "9408659"].includes(station.place_authority_id);
}
function hasPoint(station) { return !excludedDisplayPoint(station) && station.latitude !== "" && station.longitude !== "" && Number.isFinite(Number(station.latitude)) && Number.isFinite(Number(station.longitude)) && Math.abs(Number(station.latitude)) <= 90 && Math.abs(Number(station.longitude)) <= 180; }
function point(station) {
  const raw = station.display_latitude && station.display_longitude ? [Number(station.display_latitude), Number(station.display_longitude)] : [Number(station.latitude), Number(station.longitude)];
  return displayPointAliases.get(raw.map(n => n.toFixed(5)).join(",")) || raw;
}
function numeric(value) { return value == null || value === "" || !Number.isFinite(Number(value)) ? null : Number(value); }
function copyStations(copyId) { return state.stationsByCopy.get(copyId) || []; }
function printStation(copyId) { return copyStations(copyId).find(s => s.station_type === "print_place"); }
function samePoint(first, second) {
  return Boolean(first && second && hasPoint(first) && hasPoint(second) &&
    point(first).every((n, i) => n === point(second)[i]));
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
  if (year === CURRENT_YEAR) return stations.filter(s => hasPoint(s) && !isArea(s));
  return stations.filter(station => station.station_type !== "current_holding" &&
    !station.date_warning && stationAnchor(station) !== null && stationAnchor(station) <= year && hasPoint(station) && !isArea(station));
}

function holdingLabel(copy) {
  return ["Historical Copy", "Trade Copy"].includes(copy.holding_institution_name)
    ? "Current location unknown" : copy.holding_institution_name || "Holding location not specified";
}

function segmentEvidence(from, to, all) {
  const reasons = [];
  if ([from, to].some(s => s.display_uncertainty || s.spatial_precision === "country")) reasons.push("Uncertain or approximate location");
  if ([from, to].some(s => s.date_warning)) reasons.push("Conflicting dates");
  const middle = all.slice(all.indexOf(from) + 1, all.indexOf(to));
  const areas = middle.filter(s => isArea(s) || excludedDisplayPoint(s));
  if (areas.length) reasons.push("Intermediate records: " + [...new Set(areas.map(s => s.location_label))].join("; ") + " (no precise location)");
  if (middle.length || Number(to.source_order) - Number(from.source_order) > 1) reasons.push("Intermediate records not mapped");
  const end = numeric(from.time_end), start = numeric(to.time_start);
  if (end === null || start === null) reasons.push("Transition insufficiently dated");
  else if (start > end + 1) reasons.push("Gap between dated records");
  else if (start < (numeric(from.time_start) ?? end)) reasons.push("Chronological order unclear");
  if (Number(from.source_order) === Number(to.source_order)) reasons.push("Places in the same source block; sequence not established");
  return { dashed: reasons.length > 0, description: reasons.length ? reasons.join("; ") : "Dated sequence with no apparent gap in the displayed records" };
}

function updateRouteFocus() {
  const segment = state.focusedSegment || state.hoveredSegment;
  const highlighted = segment ? null : state.focusedCopy ? new Set([state.focusedCopy]) : state.focusedBundle || (state.hoveredCopy ? new Set([state.hoveredCopy]) : state.hoveredBundle);
  highlightLayer.clearLayers();
  for (const item of state.layers) {
    const active = segment ? item.segmentKey === segment : highlighted && [...(item.copyIds || [item.copyId])].some(id => highlighted.has(id));
    const muted = (segment || highlighted) && !active;
    item.layer.setStyle({ weight: active ? (item.marker ? 3 : Math.max(6, item.baseWeight || 3)) : (item.marker ? 2 : item.baseWeight || 3), opacity: muted ? .12 : active ? 1 : .55, ...(item.marker ? { fillOpacity: muted ? .08 : active ? .65 : (item.baseFillOpacity ?? 1) } : {}) });
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
  els["clear-focus"].hidden = !state.focusedCopy && !state.focusedBundle && !state.focusedSegment;
}

function focusCopy(copyId) {
  state.selectedConnection = null;
  state.returnConnection = null;
  state.focusedSegment = null; state.hoveredSegment = null;
  els["bundle-panel"].hidden = true;
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

function weightedPlaceGroups(copies, year, zoom, strength) {
  const places = new Map(), assignments = new Map();
  const placeKey = station => point(station).map(n => n.toFixed(5)).join(",");
  for (const copy of copies) for (const station of routeAtYear(copy.copy_id, year)) {
    const key = placeKey(station);
    if (!places.has(key)) places.set(key, {key, station, copies: new Set()});
    places.get(key).copies.add(copy.copy_id);
  }
  const ordered = [...places.values()].sort((a,b)=>b.copies.size-a.copies.size || a.key.localeCompare(b.key));
  const size=256*2**zoom, maximum=ordered[0]?.copies.size || 1;
  const project=station=>{
    const [lat,lon]=point(station), sine=Math.sin(Math.max(-85,Math.min(85,lat))*Math.PI/180);
    return [(lon+180)/360*size,(.5-Math.log((1+sine)/(1-sine))/(4*Math.PI))*size];
  };
  const centers=[];
  for (const place of ordered) {
    const xy=project(place.station);
    let best=null, bestScore=Infinity;
    for (const center of centers) {
      const dx=Math.abs(xy[0]-center.xy[0]);
      const distance=Math.hypot(Math.min(dx,size-dx),xy[1]-center.xy[1]);
      // Finite radius; strong neighbouring centers are harder to absorb.
      const radius=strength*(.5+.5*Math.sqrt(center.copies.size/maximum))*(1-.5*place.copies.size/center.copies.size);
      if (radius>0 && distance<=radius && distance/radius<bestScore) {
        best=center; bestScore=distance/radius;
      }
    }
    if (!best) { best={...place,xy,members:[]};centers.push(best); }
    best.members.push(place);
    assignments.set(place.key,best);
  }
  return {assignments,placeKey};
}

function bundleRoutes(copies, year) {
  const groups = new Map();
  const clustering=weightedPlaceGroups(copies,year,map.getZoom(),state.bundleStrength);
  const centerFor=s=>clustering.assignments.get(clustering.placeKey(s));
  const keyFor=s=>centerFor(s).key;
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
  for (const g of groups.values()) {
    const endpoints = [new Map(), new Map()];
    const firstKey = keyFor(g.from);
    for (const e of g.entries.values()) for (const leg of e.legs) {
      const pair = keyFor(leg.from) === firstKey ? [leg.from,leg.to] : [leg.to,leg.from];
      pair.forEach((st,i)=>endpoints[i].set(point(st).join(","),st));
    }
    g.centers=[centerFor(g.from),centerFor(g.to)];
    g.coordinates=g.centers.map(center=>point(center.station));
    g.endpointNames = endpoints.map(points=>[...new Set([...points.values()].map(st=>st.preferred_placename||st.place_name||st.location_label))]);
  }
  return [...groups.values()];
}
function bundleTitle(group) {
  return group.centers.map(center=>`${center.members.length>1?"Cluster around ":""}${center.station.preferred_placename || center.station.place_name || center.station.location_label}`).join(" ↔ ");
}
function selectSegment(group) {
  state.selectedConnection = group;
  state.returnConnection = null;
  state.focusedCopy=null; state.focusedBundle=null; state.hoveredCopy=null; state.hoveredBundle=null;
  state.focusedSegment=group.key; state.hoveredSegment=null;
  closePanel(els["detail-panel"]); closePanel(els["about-panel"]);
  els["bundle-content"].innerHTML=bundlePopup(group);
  els["bundle-panel"].hidden=false;
  els["bundle-panel"].scrollTop=0;
  updateRouteFocus();
}

function bundlePopup(group) {
  const entries=[...group.entries.values()];
  const name=s=>s.preferred_placename || s.place_name || s.location_label;
  return `<h3>${escapeHtml(bundleTitle(group))}</h3>
    <p>${entries.length} ${entries.length===1?"copy":"copies"} on this connection</p>
    <p class="popup-meta">A place cluster groups locations, not copies. A single copy can connect two place clusters.</p>
    <p class="popup-meta">Places on this connection: ${group.endpointNames.map(names=>names.map(escapeHtml).join(", ")).join(" ↔ ")}</p>
    <p class="method-note">Frequently recorded places form cluster centres and may include nearby places. These are not historical territories or evidence of a shared journey. Each copy lists its actual recorded places.</p>
    <div class="bundle-list" tabindex="0" aria-label="Copies on this connection">${entries.map(({copy,legs})=>`<div class="bundle-copy">
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
  if (!station || (!station.time_start && !station.time_end)) return "undated";
  return station.time_start === station.time_end ? station.time_start : [station.time_start, station.time_end].filter(Boolean).join("–");
}

function searchable(copy) {
  const station = printStation(copy.copy_id);
  return [copy.title, copy.holding_institution_name, copy.shelfmark, copy.mei_id, copy.host_istc_id, copy.gw_references, station?.location_label].join(" ").toLocaleLowerCase("en");
}

function copyCollections(copy) { return (copy.collection_groups || "core").split(" | "); }
function matchesCollection(copy) { return copyCollections(copy).some(group => state.collections.has(group)); }

function matchesFilters(copy) {
  const station = printStation(copy.copy_id);
  return matchesCollection(copy) && (!state.search || searchable(copy).includes(state.search)) &&
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
  return `<h3>${escapeHtml(copy.title || "Untitled")}</h3>
    <p class="popup-meta">${escapeHtml(station?.location_label || "Printing place unknown")}, ${escapeHtml(printYear(copy))}<br>${escapeHtml(holdingLabel(copy))} · ${escapeHtml(copy.shelfmark || "no shelfmark")}</p>
    <p class="popup-route">${escapeHtml(routeSummary(copy.copy_id))}</p>
    <button class="popup-button" type="button" data-track-id="${escapeHtml(copy.copy_id)}">Trace this copy</button>`;
}

function clearMapLayers() {
  if (heatCanvas) heatCanvas.hidden = true;
  state.selectedConnection = null;
  state.returnConnection = null;
  state.focusedSegment = null; state.hoveredSegment = null;
  els["bundle-panel"].hidden = true;
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
    const key = point(station).map(n => n.toFixed(5)).join(",") + "|" + spatialPrecision(station);
    if (!groups.has(key)) groups.set(key, { station, entries: new Map() });
    groups.get(key).entries.set(copy.copy_id, { copy, ...location });
  }
  return [...groups.values()];
}

function locationPopup(group) {
  const entries = [...group.entries.values()];
  const names = [...new Set(entries.map(e => e.station.preferred_placename || e.station.place_name || e.station.location_label))];
  return `<h3>${names.map(escapeHtml).join(" / ")} · ${state.year}</h3>
    <p>${entries.length} copies at the last identifiable location by ${state.year}.</p>
    <p class="method-note">Copies shown at the same map point were not necessarily held together or continuously kept there.</p>
    <div class="bundle-list" tabindex="0" aria-label="Copies at this map point">${entries.map(({copy, station}) => `<div class="bundle-copy">${popupHtml(copy)}
      <p class="popup-meta">${escapeHtml(station.location_label)} · ${escapeHtml(stationTime(station))}${spatialNote(station) ? " · " + escapeHtml(spatialNote(station)) : ""}${station.display_uncertainty ? " · " + escapeHtml(station.display_uncertainty) : ""}</p></div>`).join("")}</div>`;
}

// Screen-space density: zooming changes the geographical reach of a 28px kernel.
const HEAT_RADIUS = 28;
const HEAT_STEP = 4;
let heatCanvas = null;
let heatReference = { key: null, maximum: 1 };
function densityField(points, width, height) {
  const cols = Math.ceil(width / HEAT_STEP), rows = Math.ceil(height / HEAT_STEP);
  const values = new Float32Array(cols * rows);
  const radius = HEAT_RADIUS / HEAT_STEP;
  for (const {x, y, weight} of points) {
    const cx = x / HEAT_STEP, cy = y / HEAT_STEP;
    for (let iy = Math.max(0, Math.floor(cy-radius)); iy < Math.min(rows, Math.ceil(cy+radius)); iy++) {
      for (let ix = Math.max(0, Math.floor(cx-radius)); ix < Math.min(cols, Math.ceil(cx+radius)); ix++) {
        const d2 = ((ix+.5-cx)**2 + (iy+.5-cy)**2) / (radius*radius);
        if (d2 <= 1) values[iy*cols+ix] += weight * Math.exp(-4.5*d2);
      }
    }
  }
  return {values, cols, rows};
}
function heatPotential(copies) {
  const places = new Map();
  for (const copy of copies) {
    const seen = new Set();
    for (const station of copyStations(copy.copy_id)) {
      if (!hasPoint(station) || isArea(station)) continue;
      const coordinates = point(station), key = coordinates.join(',');
      if (seen.has(key)) continue;
      seen.add(key);
      if (!places.has(key)) places.set(key, {coordinates, weight:0});
      places.get(key).weight++;
    }
  }
  return [...places.values()];
}
function drawHeatmap(copies, groups) {
  if (!heatCanvas) {
    heatCanvas = document.createElement('canvas');
    heatCanvas.className = 'density-canvas';
    heatCanvas.setAttribute('aria-hidden', 'true');
    map.getContainer().appendChild(heatCanvas);
  }
  heatCanvas.hidden = false;
  const size = map.getSize(), center = map.getCenter();
  const project = (coordinates, weight) => ({...map.latLngToContainerPoint(coordinates), weight});
  const key = [map.getZoom(), center.lat, center.lng, size.x, size.y, copies.map(c=>c.copy_id).join(',')].join('|');
  if (key !== heatReference.key) {
    // All recorded localities form a time-independent reference envelope.
    // A copy counts once per candidate locality, not once per provenance record.
    const potential = heatPotential(copies).map(p=>project(p.coordinates,p.weight));
    const field = densityField(potential,size.x,size.y);
    let maximum = 0;
    for (const value of field.values) maximum = Math.max(maximum,value);
    heatReference = {key, maximum: Math.max(1,maximum)};
  }
  const field = densityField(groups.map(g=>project(point(g.station),g.entries.size)),size.x,size.y);
  heatCanvas.width = field.cols; heatCanvas.height = field.rows;
  heatCanvas.style.width = size.x+'px'; heatCanvas.style.height = size.y+'px';
  const ctx = heatCanvas.getContext('2d'), pixels = ctx.createImageData(field.cols,field.rows);
  const stops = [[255,224,130],[246,147,64],[213,64,54],[117,19,47]];
  for (let i=0;i<field.values.length;i++) {
    const ratio = Math.min(1,field.values[i]/heatReference.maximum);
    if (ratio<=0) continue;
    const intensity=Math.sqrt(ratio), position=intensity*(stops.length-1);
    const lo=Math.min(stops.length-2,Math.floor(position)), blend=position-lo;
    for(let c=0;c<3;c++)pixels.data[i*4+c]=Math.round(stops[lo][c]*(1-blend)+stops[lo+1][c]*blend);
    pixels.data[i*4+3]=Math.round(190*Math.min(1,intensity*3));
  }
  ctx.putImageData(pixels,0,0);
}

function renderLocations(copies, fit) {
  const heat = state.locationStyle === "heatmap";
  const groups = groupLocations(copies, state.year).filter(g => !heat || !isArea(g.station));
  if (heat) drawHeatmap(copies, groups);
  let located = 0;
  // Large circles first so smaller nearby circles remain selectable.
  groups.sort((a, b) => b.entries.size - a.entries.size);
  for (const group of groups) {
    const entries = [...group.entries.values()], ids = new Set(group.entries.keys());
    located += entries.length;
    const marker = L.circleMarker(point(group.station), {
      radius: heat ? 4 : 6 * Math.sqrt(entries.length), color: "#75132f", weight: 2,
      fillColor: "#75132f", fillOpacity: heat ? .75 : .22,
      dashArray: isArea(group.station) ? "3 3" : null,
      bubblingMouseEvents: false
    }).addTo(locationLayer);
    state.layers.push({layer: marker, copyIds: ids, marker: true, baseFillOpacity: heat ? .75 : .22});
    marker.bindPopup(locationPopup(group), {autoPan: false, maxWidth: 380});
    marker.bindTooltip(`${escapeHtml(group.station.preferred_placename || group.station.place_name || group.station.location_label)} · ${entries.length} copies${isArea(group.station) ? " · " + spatialNote(group.station) : ""}`);
    marker.on("click", () => { state.focusedCopy = null; state.focusedBundle = ids; state.hoveredBundle = null; updateRouteFocus(); });
    marker.on("mouseover", () => { state.hoveredBundle = ids; updateRouteFocus(); });
    marker.on("mouseout", () => { state.hoveredBundle = null; updateRouteFocus(); });
  }
  updateRouteFocus();
  const notPrinted = copies.filter(c => { const birth = stationAnchor(printStation(c.copy_id) || {}); return birth !== null && birth > state.year; }).length;
  els["result-summary"].textContent = `${copies.length} copies selected · ${located} at ${groups.length} map points for ${state.year} · ${notPrinted} not yet printed · ${copies.length - located - notPrinted} ${heat ? "without a local map point" : "without an identifiable location"}`;
  els["map-message"].hidden = groups.length > 0;
  els["map-message"].textContent = copies.length ? "No location can be assigned for this year and selection." : "No copies are selected for these filters.";
  if (fit && groups.length) map.fitBounds(groups.map(g => point(g.station)), {padding: [24, 24], maxZoom: 6});
}

function setMapView(view) {
  state.view = view;
  els["bundle-controls"].hidden = view !== "connections";
  els["location-style-controls"].hidden = view !== "locations";
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
    if (location && !isArea(location.station)) {
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
      marker.bindTooltip(`${copy.title || "Untitled"} · ${location.station.location_label}${location.inferred ? " · approximation / last record" : ""}${location.station.display_uncertainty ? " · " + location.station.display_uncertainty : ""}`, { direction: "top", opacity: .94 });
      bounds.push(point(location.station));
    }
  }

  const bundles = bundleRoutes(copies, state.year);
  for (const group of bundles) {
    const ids=new Set(group.entries.keys()),single=ids.size===1;
    const legs=[...group.entries.values()].flatMap(e=>e.legs);
    const dashed=legs.some(l=>l.evidence.dashed);
    const weight=state.lineScale * (2 + 2 * Math.sqrt(ids.size));
    const line=L.polyline(group.coordinates,{color:single?colorFor([...ids][0]):"#596674",weight,opacity:.55,dashArray:dashed?"6 5":null,bubblingMouseEvents:false}).addTo(routeLayer);
    state.layers.push({layer:line,segmentKey:group.key,copyIds:ids,copyId:single?[...ids][0]:null,baseWeight:weight,marker:false});
    line.bindTooltip(`${ids.size} ${single?"copy":"copies"} · ${escapeHtml(bundleTitle(group))}`);
    line.on("click",()=>selectSegment(group));
    line.on("mouseover",()=>{state.hoveredSegment=group.key;updateRouteFocus()});
    line.on("mouseout",()=>{state.hoveredSegment=null;updateRouteFocus()});
  }
  updateRouteFocus();

  els["result-summary"].textContent = `${copies.length} copies shown · ${located} with a map point for ${state.year} · ${bundles.length} connection bundles · short connections may disappear when zooming out`;
  els["map-message"].hidden = copies.length > 0;
  els["map-message"].textContent = copies.length ? "" : "No copies are selected for these filters.";
  if (fit && bounds.length) map.fitBounds(bounds, { padding: [24, 24], maxZoom: 6 });
}

function renderList() {
  const copies = filteredCopies();
  els["print-list"].innerHTML = copies.map(copy => {
    const station = printStation(copy.copy_id);
    const checked = state.selected.has(copy.copy_id);
    return `<div class="print-card ${checked ? "" : "is-unselected"}" data-copy-card="${escapeHtml(copy.copy_id)}">
      <input type="checkbox" data-copy-select="${escapeHtml(copy.copy_id)}" aria-label="Show copy: ${escapeHtml(copy.title || copy.copy_id)}" ${checked ? "checked" : ""}>
      <button class="print-card-body" type="button" data-copy-detail="${escapeHtml(copy.copy_id)}"><span class="print-title">${escapeHtml(copy.title || "Untitled")}</span>
      <span class="print-meta">${escapeHtml(station?.location_label || "Printing place unknown")} · ${escapeHtml(printYear(copy))} · ${escapeHtml(languageLabels[copy.language] || copy.language)}<br>${escapeHtml(holdingLabel(copy))} · <span class="print-id">${escapeHtml(copy.shelfmark || copy.mei_id)}</span></span>
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
  return station.time_start || station.time_end || "undated";
}

function stationTime(station) {
  if (station.station_type === "current_holding") {
    const current = `As of ${station.observation_date || CURRENT_YEAR}`;
    if (!station.mergedProvenance) return current;
    const historical = historicalStationTime(station.mergedProvenance);
    return historical === "undated" ? current : `Location record ${historical}; ${current}`;
  }
  return historicalStationTime(station);
}

function openDetail(copyId, fromConnection = false) {
  const copy = state.copies.find(item => item.copy_id === copyId);
  if (!copy) return;
  const returnTo = fromConnection && state.selectedConnection ? {
    group: state.selectedConnection,
    scrollTop: els["bundle-panel"].scrollTop,
    copyId
  } : null;
  focusCopy(copyId);
  state.returnConnection = returnTo;
  const stations = compactStationsForDisplay(copyId);
  const print = printStation(copyId);
  els["detail-content"].innerHTML = `
    <h2 id="detail-title">${escapeHtml(copy.title || "Untitled")}</h2>
    <p class="detail-lead">${escapeHtml(print?.location_label || "Printing place unknown")}, ${escapeHtml(printYear(copy))} · ${escapeHtml(copy.shelfmark || "no shelfmark")}</p>
    <dl class="detail-facts">
      <dt>MEI</dt><dd><a href="${escapeHtml(copy.mei_url)}" target="_blank" rel="noopener">${escapeHtml(copy.mei_id)}</a></dd>
      <dt>ISTC</dt><dd><a href="https://data.cerl.org/istc/${escapeHtml(copy.host_istc_id)}" target="_blank" rel="noopener">${escapeHtml(copy.host_istc_id)}</a></dd>
      <dt>GW</dt><dd>${escapeHtml(copy.gw_references || "not specified")}</dd>
      <dt>Language</dt><dd>${escapeHtml(languageLabels[copy.language] || copy.language || "not specified")}</dd>
      <dt>Holding institution</dt><dd>${escapeHtml(holdingLabel(copy))}</dd>
    </dl>
    <h3>Recorded locations</h3>
    <p class="method-note">This list shows the full sequence. Gaps, undated records and missing places prevent a continuous account of the copy’s whereabouts.</p>
    <ol class="station-list">${stations.map(station => {
      const unresolved = spatialNote(station) || station.date_warning || station.display_uncertainty || (station.geolocation_certainty === "probable" ? "Probable place identification" : "") || unresolvedLabels[station.location_resolution_status];
      return `<li class="station-item"><span class="station-type">${escapeHtml(stationLabels[station.station_type] || station.station_type)}</span>
        <span class="station-place">${escapeHtml(station.location_label || station.place_name || "Place not specified")}</span>
        <span class="station-time">${escapeHtml(stationTime(station))}</span>
        ${unresolved ? `<span class="uncertain-badge">${escapeHtml(unresolved)}</span>` : ""}
        ${station.mergedProvenance ? `<span class="station-note">Records at the same map location are combined; the location record does not necessarily date acquisition by the present institution.</span>` : ""}
        ${station.location_resolution_note ? `<span class="station-note">${escapeHtml(station.location_resolution_note)}</span>` : ""}
        ${(station.source_url || "").split(" | ").filter(url => /^https?:\/\//.test(url)).map(url => `<a class="station-source" href="${escapeHtml(url)}" target="_blank" rel="noopener">Source: ${escapeHtml(station.source_catalogue)}</a>`).join(" ")}
      </li>`;
    }).join("")}</ol>`;
  els["about-panel"].classList.remove("is-open");
  els["about-panel"].setAttribute("aria-hidden", "true");
  els["detail-panel"].classList.add("is-open");
  state.detailIsOpen = true;
  els["detail-panel"].scrollTop = 0;
  els["detail-panel"].setAttribute("aria-hidden", "false");
  els["detail-close"].setAttribute("aria-label", returnTo ? "Back to connection" : "Close copy details");
  els["detail-close"].setAttribute("title", returnTo ? "Back to connection" : "Close copy details");
  els["detail-close"].focus();
}

function closeDetail() {
  const previous = state.returnConnection;
  closePanel(els["detail-panel"]);
  state.returnConnection = null;
  if (!previous) return;
  state.selectedConnection = previous.group;
  els["bundle-panel"].hidden = false;
  // Keep the selected copy highlighted and restore the existing list unchanged.
  els["bundle-panel"].scrollTop = previous.scrollTop;
  const button = els["bundle-content"].querySelector(`[data-track-id="${previous.copyId}"]`);
  if (button) button.focus({preventScroll: true});
}

function closePanel(panel) {
  if (panel === els["detail-panel"]) state.detailIsOpen = false;
  panel.classList.remove("is-open");
  panel.setAttribute("aria-hidden", "true");
}

function populateFilters() {
  const places = [...new Set(state.copies.map(copy => printStation(copy.copy_id)?.location_label).filter(Boolean))].sort((a, b) => a.localeCompare(b, "en"));
  const languages = [...new Set(state.copies.map(copy => copy.language).filter(Boolean))].sort();
  els["place-filter"].insertAdjacentHTML("beforeend", places.map(value => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join(""));
  els["language-filter"].insertAdjacentHTML("beforeend", languages.map(value => `<option value="${escapeHtml(value)}">${escapeHtml(languageLabels[value] || value)}</option>`).join(""));
}

function changeCollection(group, checked) {
  checked ? state.collections.add(group) : state.collections.delete(group);
  focusCopy(null);
  closePanel(els["detail-panel"]);
  render();
}

function bindEvents() {
  for (const group of ["core", "liturgy", "devotional"]) {
    els[`collection-${group}`].addEventListener("change", event => changeCollection(group, event.target.checked));
  }
  map.on("zoomend",()=>{render({list:false})});
  map.on("moveend",()=>{if(state.view==="locations" && state.locationStyle==="heatmap")render({list:false})});
  map.on("resize",()=>{if(state.view==="locations")render({list:false})});
  map.on("movestart zoomstart",()=>{if(heatCanvas)heatCanvas.hidden=true});
  for (const style of ["circles","heatmap"]) {
    els[`style-${style}`].addEventListener("click",()=>{
      state.locationStyle=style;
      for(const value of ["circles","heatmap"])els[`style-${value}`].setAttribute("aria-pressed",String(value===style));
      els["heatmap-legend"].hidden=style!=="heatmap";
      els["circle-legend"].hidden=style!=="circles";
      map.closePopup();render({list:false});
    });
  }
  for (const [id,key,out] of [["bundle-strength","bundleStrength","bundle-value"],["line-scale","lineScale","line-value"]]) {
    els[id].addEventListener("input",event=>{state[key]=Number(event.target.value);els[out].textContent=String(state[key]);render({list:false})});
  }
  els["bundle-close"].addEventListener("click",()=>focusCopy(null));
  els["bundle-content"].addEventListener("click",event=>{const button=event.target.closest("[data-track-id]");if(button)openDetail(button.dataset.trackId, true)});

  els["view-connections"].addEventListener("click", () => setMapView("connections"));
  els["view-locations"].addEventListener("click", () => setMapView("locations"));
  map.on("click", () => { focusCopy(null); closePanel(els["detail-panel"]); });
  els["clear-focus"].addEventListener("click", () => { focusCopy(null); map.closePopup(); closePanel(els["detail-panel"]); });
  els["year-slider"].addEventListener("input", event => { state.year = Number(event.target.value); render({ list: false }); });
  els["search-input"].addEventListener("input", event => { state.search = event.target.value.trim().toLocaleLowerCase("en"); render(); });
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
    state.collections = new Set(["core"]);
    for (const group of ["core", "liturgy", "devotional"]) els[`collection-${group}`].checked = group === "core";
    focusCopy(null); closePanel(els["detail-panel"]);
    state.year = CURRENT_YEAR; state.search = ""; state.place = ""; state.language = ""; state.focusedCopy = null;
    state.copies.forEach(copy => state.selected.add(copy.copy_id));
    els["year-slider"].value = CURRENT_YEAR; els["search-input"].value = ""; els["place-filter"].value = ""; els["language-filter"].value = "";
    render({ fit: true });
  });
  document.getElementById("map").addEventListener("click", event => {
    const button = event.target.closest("[data-track-id]");
    if (button) openDetail(button.dataset.trackId);
  });
  els["detail-close"].addEventListener("click", closeDetail);
  els["about-button"].addEventListener("click", () => {
    state.returnConnection=null; state.selectedConnection=null; els["bundle-panel"].hidden=true; closePanel(els["detail-panel"]); els["about-panel"].classList.add("is-open"); els["about-panel"].setAttribute("aria-hidden", "false"); els["about-close"].focus();
  });
  els["about-close"].addEventListener("click", () => closePanel(els["about-panel"]));
  document.addEventListener("keydown", event => { if (event.key === "Escape") { if (state.detailIsOpen) { closeDetail(); return; } focusCopy(null); closePanel(els["about-panel"]); } });
}

async function loadData() {
  try {
    const [copyResponse, stationResponse] = await Promise.all(Object.values(DATA_URLS).map(url => fetch(url)));
    if (!copyResponse.ok || !stationResponse.ok) throw new Error("Could not load the data files.");
    const [copies, stations] = await Promise.all([copyResponse.text().then(parseCsv), stationResponse.text().then(parseCsv)]);
    state.copies = copies.filter(directCopy).sort((a, b) => (a.title || "").localeCompare(b.title || "", "en"));
    for (const station of stations.map(reviewedStation)) {
      if (!state.stationsByCopy.has(station.copy_id)) state.stationsByCopy.set(station.copy_id, []);
      state.stationsByCopy.get(station.copy_id).push(station);
    }
    for (const values of state.stationsByCopy.values()) values.sort((a, b) => Number(a.source_order) - Number(b.source_order) || Number(a.place_order_within_source) - Number(b.place_order_within_source));
    state.copies.forEach(copy => state.selected.add(copy.copy_id));
    for (const group of ["core", "liturgy", "devotional"]) {
      document.getElementById(`count-${group}`).textContent = state.copies.filter(copy => copyCollections(copy).includes(group)).length.toLocaleString("en") + " copies";
    }
    populateFilters(); bindEvents(); render({ fit: true });
  } catch (error) {
    els["result-summary"].textContent = "Could not load the map data.";
    els["map-message"].hidden = false;
    els["map-message"].textContent = `${error.message} Please open the site through a web server or GitHub Pages.`;
  }
}

loadData();
