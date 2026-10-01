const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const element=()=>({value:'',textContent:'',innerHTML:'',hidden:false,classList:{add(){},remove(){}},setAttribute(){},focus(){},insertAdjacentHTML(){},addEventListener(){}});
const elements=new Map();const doc={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},addEventListener(){}};
const map={setView(){return this},fitBounds(){this.fits=(this.fits||0)+1}};
const layer=()=>({addTo(){return this},clearLayers(){},bindPopup(){},bindTooltip(){},on(){},setStyle(){}});
const context=vm.createContext({console,document:doc,L:{map:()=>map,tileLayer:layer,layerGroup:layer,polyline:layer,circleMarker:layer}});
vm.runInContext(fs.readFileSync('assets/app.js','utf8').replace(/loadData\(\);\s*$/,''),context);
context.copiesText=fs.readFileSync('data/expanded/tables/mei-copies.csv','utf8');context.stationsText=fs.readFileSync('data/expanded/tables/mei-itinerary-stations-resolved.csv','utf8');context.assert=assert;
vm.runInContext(`
state.copies=parseCsv(copiesText).filter(directCopy);
for(const s of parseCsv(stationsText)){if(!state.stationsByCopy.has(s.copy_id))state.stationsByCopy.set(s.copy_id,[]);state.stationsByCopy.get(s.copy_id).push(s)}
for(const a of state.stationsByCopy.values())a.sort((a,b)=>Number(a.source_order)-Number(b.source_order)||Number(a.place_order_within_source)-Number(b.place_order_within_source));
state.copies.forEach(c=>state.selected.add(c.copy_id));
assert.equal(state.copies.length,484);assert.equal(state.selected.size,484);
assert.equal(locationAtYear('00201166',2026).station.time_start,'1905');
assert.equal(locationAtYear('00201167',2026).station.location_label,'Rom');
assert.equal(locationAtYear('00201576',2026).station.time_start,'2024');
assert.equal(locationAtYear('02125950',2026).station.time_start,'2018');
for(const c of state.copies){const p=printStation(c.copy_id);assert.ok(p);const y=stationAnchor(p);if(y!==null){assert.equal(locationAtYear(c.copy_id,y-1),null);assert.equal(routeAtYear(c.copy_id,y-1).length,0)}}
assert.equal(copyStations('00200668').find(s=>s.station_type==='print_place').spatial_precision,'country');
assert.ok(!routeAtYear('02013229',1930).some(s=>s.date_warning));
for(const year of [1450,1499,1600,1800,1950,2026]){state.year=year;render();}
state.search='bologna';assert.ok(filteredCopies().length>0);state.search='';
for(const c of state.copies)openDetail(c.copy_id);
assert.equal(map.fits,undefined); // Opening details or moving time never resets the map.
assert.ok(popupHtml(state.copies[0]).includes('Druck verfolgen'));
`,context);
console.log('PASS: full data rendering with Leaflet/DOM stubs; all 484 detail views, six slider years, pre-print dates, historic endpoints, filters, country point, date conflict and viewport.');
