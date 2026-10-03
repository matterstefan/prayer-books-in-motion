const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const element=()=>({value:'',textContent:'',innerHTML:'',hidden:false,classList:{add(){},remove(){}},setAttribute(){},focus(){},insertAdjacentHTML(){},addEventListener(){}});
const elements=new Map();const doc={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},addEventListener(){}};
const map={getZoom(){return this.zoom||4},setView(){return this},closePopup(){},fitBounds(){this.fits=(this.fits||0)+1}};
const layer=()=>({addTo(){return this},clearLayers(){},bindPopup(){},bindTooltip(){},on(){},setStyle(style){this.style={...this.style,...style}},bringToFront(){}});
const context=vm.createContext({console,document:doc,L:{map:()=>map,tileLayer:layer,layerGroup:layer,polyline:layer,circleMarker:layer}});
vm.runInContext(fs.readFileSync('assets/app.js','utf8').replace(/loadData\(\);\s*$/,''),context);
context.copiesText=fs.readFileSync('data/expanded/tables/mei-copies.csv','utf8');context.stationsText=fs.readFileSync('data/expanded/tables/mei-itinerary-stations-resolved.csv','utf8');context.assert=assert;
vm.runInContext(`
state.bundleStrength=0;state.lineScale=1;
state.copies=parseCsv(copiesText).filter(directCopy);
for(const s of parseCsv(stationsText).map(reviewedStation)){if(!state.stationsByCopy.has(s.copy_id))state.stationsByCopy.set(s.copy_id,[]);state.stationsByCopy.get(s.copy_id).push(s)}
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
state.year=2026;render();
const first=state.layers.find(x=>!x.marker&&x.copyId);focusCopy(first.copyId);
assert.equal(first.layer.style.weight,6);
assert.equal(state.layers.find(x=>x.marker&&x.copyId!==first.copyId).layer.style.opacity,.12);
updateRouteFocus();assert.equal(first.layer.style.weight,6);
render({list:false});assert.equal(state.focusedCopy,first.copyId);
focusCopy(null);assert.equal(state.layers[0].layer.style.opacity,.55);
const hoveredId=state.layers.find(x=>state.layers.filter(y=>y.copyId===x.copyId&&!y.marker).length>1).copyId;
hoverCopy(hoveredId);
assert.ok(state.layers.filter(x=>x.copyId===hoveredId&&!x.marker).every(x=>x.layer.style.weight===6));
assert.ok(state.layers.filter(x=>x.marker&&x.copyId!==hoveredId).every(x=>x.layer.style.opacity===.12));
assert.equal(els['clear-focus'].hidden,true);
const lockedId=state.layers.find(x=>x.copyId!==hoveredId).copyId;
focusCopy(lockedId);hoverCopy(hoveredId);hoverCopy(null);
assert.ok(state.layers.filter(x=>x.copyId===lockedId).every(x=>x.layer.style.opacity===1));
focusCopy(null);hoverCopy(hoveredId);hoverCopy(null);
assert.ok(state.layers.every(x=>x.layer.style.opacity===.55));
const groups=bundleRoutes(state.copies,2026);
assert.ok(groups.some(g=>g.entries.size>=23));
assert.equal(new Set(groups.map(g=>g.key)).size,groups.length);
for(const g of groups) assert.equal(g.entries.size,new Set([...g.entries.values()].map(e=>e.copy.copy_id)).size);
const one=state.copies.find(c=>routeAtYear(c.copy_id,2026).length>2);
assert.ok(bundleRoutes([one],2026).every(g=>g.entries.size===1));
assert.equal(bundleRoutes(state.copies,1450).length,0);
const shared=groups.find(g=>g.entries.size>2);
assert.equal((bundlePopup(shared).match(/data-track-id=/g)||[]).length,shared.entries.size);
state.focusedBundle=new Set(shared.entries.keys());updateRouteFocus();
assert.equal(els['clear-focus'].hidden,false);
focusCopy([...shared.entries.keys()][0]);assert.equal(state.focusedBundle,null);
const fake={copy_id:'test-repeat'};
const stop=(latitude,longitude,source_order)=>({latitude,longitude,source_order:String(source_order),station_type:'provenance_place',time_start:'1500',time_end:'1500'});
state.stationsByCopy.set(fake.copy_id,[stop('10','20',0),stop('30','40',1),stop('10','20',2),stop('30','40',3)]);
const repeated=bundleRoutes([fake],2026);
assert.equal(repeated.length,1);assert.equal(repeated[0].entries.size,1);assert.equal(repeated[0].entries.get(fake.copy_id).legs.length,3);
state.stationsByCopy.delete(fake.copy_id);
const a={source_order:'0',time_start:'1500',time_end:'1505'},b={source_order:'1',time_start:'1505',time_end:'1510'};
assert.equal(segmentEvidence(a,b,[a,b]).dashed,false);
assert.equal(segmentEvidence(a,{...b,time_start:'1550'},[a,b]).dashed,true);
assert.equal(segmentEvidence(a,{...b,spatial_precision:'country'},[a,b]).dashed,true);
assert.equal(segmentEvidence(a,{...b,time_start:''},[a,b]).dashed,true);

focusCopy(null);
for (const year of [1450,1499,1600,1800,1950,2026]) {
  state.year=year;
  const locations=groupLocations(state.copies,year);
  const ids=locations.flatMap(g=>[...g.entries.keys()]);
  assert.equal(ids.length,new Set(ids).size);
  assert.equal(ids.length,state.copies.filter(c=>locationAtYear(c.copy_id,year)).length);
  setMapView('locations');
  assert.equal(state.layers.length,locations.length);
  assert.ok(state.layers.every(l=>l.marker));
  assert.equal(els['map-message'].hidden,locations.length>0);
}
const currentGroups=groupLocations(state.copies,2026);
assert.equal(currentGroups.reduce((n,g)=>n+g.entries.size,0),484);
const biggest=currentGroups.sort((a,b)=>b.entries.size-a.entries.size)[0];
assert.ok(biggest.entries.size>1);
assert.equal((locationPopup(biggest).match(/data-track-id=/g)||[]).length,biggest.entries.size);
const focusId=[...biggest.entries.keys()][0];
openDetail(focusId);
assert.equal(state.focusedCopy,focusId);
assert.equal(state.layers.filter(l=>l.layer.style.opacity===1).length,1);
state.search='bologna';
const selectedBefore=[...state.selected].join(',');
state.year=1800;
setMapView('connections');setMapView('locations');
assert.equal(state.search,'bologna');assert.equal(state.year,1800);
assert.equal([...state.selected].join(','),selectedBefore);
assert.equal(map.fits,undefined);
assert.equal(els['connection-legend'].hidden,true);
assert.equal(els['location-legend'].hidden,false);
state.search='';
const testCopies=[{copy_id:'test-bounded'},{copy_id:'test-carried'},{copy_id:'test-country'}];
for(const c of testCopies)state.stationsByCopy.set(c.copy_id,[{...stop('10','20',0),time_start:'1500',time_end:c.copy_id==='test-carried'?'1500':'1600',spatial_precision:c.copy_id==='test-country'?'country':'locality'}]);
const testGroups=groupLocations([...testCopies,testCopies[0]],1550);
assert.equal(testGroups.length,2); // Never conflate a country with a locality.
const mixed=testGroups.find(g=>g.entries.size===2);
assert.equal([...mixed.entries.values()].filter(e=>e.inferred).length,1);
testCopies.forEach(c=>state.stationsByCopy.delete(c.copy_id));
state.selected.clear();render();
assert.equal(state.layers.length,0);assert.equal(els['map-message'].hidden,false);
const corrected=copyStations('02128182').find(s=>s.station_id==='02128182-p003-loc01');
assert.equal(corrected.location_label,'Frankreich, genauer Ort unbekannt');
assert.equal(corrected.source_location_label,'Fort-de-France');
assert.equal(locationAtYear('02128182',1750).station,corrected);
assert.ok(!routeAtYear('02128182',2026).some(s=>isArea(s)||excludedDisplayPoint(s)));
const correctedRoute=routeAtYear('02128182',2026);
assert.ok(segmentEvidence(correctedRoute[0],correctedRoute[1],copyStations('02128182')).description.includes('Frankreich'));
for(const stations of state.stationsByCopy.values())for(const station of stations) {
 if(countryPlaceIds.has(station.place_authority_id))assert.equal(spatialPrecision(station),'country');
 if(regionPlaceIds.has(station.place_authority_id))assert.equal(spatialPrecision(station),'region');
 if(station.place_authority_id==='9408659')assert.equal(hasPoint(station),false);
}
assert.equal(reviewedStation({...corrected,station_id:'different'}).station_id,'different');
const sourceSnapshot=JSON.stringify([...state.stationsByCopy]);
for(const [raw, target] of displayPointAliases) {
 const [latitude,longitude]=raw.split(',');
 assert.deepEqual(point({latitude,longitude}),target);
 assert.ok(samePoint({latitude,longitude},{latitude:String(target[0]),longitude:String(target[1])}));
}
const venice1935=groupLocations(state.copies,1935).filter(g=>point(g.station).join(',')==='45.43713,12.33265');
assert.equal(venice1935.length,1);assert.equal(venice1935[0].entries.size,73);
const europe=copyStations('02020083').find(s=>s.place_authority_id==='6255148');
assert.ok(europe);assert.equal(hasPoint(europe),false);
assert.ok(!routeAtYear('02020083',2026).includes(europe));
openDetail('02020083');assert.ok(els['detail-content'].innerHTML.includes('Nur Grossraum angegeben'));
for(const id of ['3172456','2634341','3074982','5110302']) {
 const s=[...state.stationsByCopy.values()].flat().find(s=>s.place_authority_id===id);
 assert.ok(s);assert.deepEqual(point(s),[Number(s.latitude),Number(s.longitude)]);
}
assert.equal(JSON.stringify([...state.stationsByCopy]),sourceSnapshot);
state.copies.forEach(c=>state.selected.add(c.copy_id));state.year=2026;state.view='connections';
state.bundleStrength=32;state.lineScale=1.5;map.zoom=3;
const zoomedOut=bundleRoutes(state.copies,2026);map.zoom=8;
const zoomedIn=bundleRoutes(state.copies,2026);
assert.ok(zoomedIn.length>zoomedOut.length);
for(const g of zoomedOut){assert.equal(g.entries.size,new Set([...g.entries.keys()]).size);assert.ok(g.coordinates.flat().every(Number.isFinite));}
render();
const selectedGroup=bundleRoutes(displayedCopies(),2026).find(g=>g.entries.size>1);
selectSegment(selectedGroup);
assert.equal(els['bundle-panel'].hidden,false);
assert.equal(state.layers.filter(l=>l.layer.style.opacity===1).length,1);
assert.equal(state.layers.find(l=>l.layer.style.opacity===1).segmentKey,selectedGroup.key);
state.hoveredSegment='another';updateRouteFocus();
assert.equal(state.layers.filter(l=>l.layer.style.opacity===1).length,1);
openDetail([...selectedGroup.entries.keys()][0]);
assert.equal(els['bundle-panel'].hidden,true);assert.equal(state.focusedSegment,null);
assert.equal(map.fits,undefined);

`,context);
console.log('PASS: full data rendering with Leaflet/DOM stubs; all 484 detail views, six slider years, pre-print dates, historic endpoints, filters, country point, date conflict and viewport.');
