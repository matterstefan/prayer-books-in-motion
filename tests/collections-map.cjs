const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const element=()=>({querySelector(){return null},scrollTop:0,value:'',textContent:'',innerHTML:'',hidden:false,classList:{add(){},remove(){}},setAttribute(){},focus(){},insertAdjacentHTML(){},addEventListener(){}});
const elements=new Map();const doc={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},addEventListener(){}};
const map={getZoom(){return this.zoom||4},setView(){return this},closePopup(){},fitBounds(){this.fits=(this.fits||0)+1}};
const layer=()=>({addTo(){return this},clearLayers(){},bindPopup(){},bindTooltip(){},on(){},setStyle(style){this.style={...this.style,...style}},bringToFront(){}});
const context=vm.createContext({console,document:doc,L:{map:()=>map,tileLayer:layer,layerGroup:layer,polyline:layer,circleMarker:layer}});
vm.runInContext(fs.readFileSync('assets/app.js','utf8').replace(/loadData\(\);\s*$/,''),context);
context.copiesText=fs.readFileSync('data/map/copies.csv','utf8');context.stationsText=fs.readFileSync('data/map/stations.csv','utf8');context.assert=assert;
vm.runInContext(`
state.copies=parseCsv(copiesText).filter(directCopy);
for(const s of parseCsv(stationsText).map(reviewedStation)) {
 if(!state.stationsByCopy.has(s.copy_id))state.stationsByCopy.set(s.copy_id,[]);
 state.stationsByCopy.get(s.copy_id).push(s);
}
for(const a of state.stationsByCopy.values())a.sort((a,b)=>Number(a.source_order)-Number(b.source_order)||Number(a.place_order_within_source)-Number(b.place_order_within_source));
state.copies.forEach(c=>state.selected.add(c.copy_id));
assert.equal(state.copies.length,5297);
assert.equal(new Set(state.copies.map(c=>c.copy_id)).size,5297);
assert.equal(filteredCopies().length,531);
for(const c of state.copies)if(copyCollections(c).includes('core'))assert.deepEqual(copyCollections(c),['core']);
const choices=[['core'],['liturgy'],['devotional'],['liturgy','devotional'],['core','liturgy'],['core','devotional'],['core','liturgy','devotional'],[]];
const counts=[531,1778,3041,4766,2309,3572,5297,0];
for(let i=0;i<choices.length;i++) {
 state.collections=new Set(choices[i]);assert.equal(displayedCopies().length,counts[i]);
 assert.equal(new Set(displayedCopies().map(c=>c.copy_id)).size,counts[i]);
}
state.collections=new Set(['core','liturgy','devotional']);
state.search='bologna';assert.ok(filteredCopies().length>0);state.search='';
state.language='lat';assert.ok(filteredCopies().every(c=>c.language==='lat'));state.language='';
const uncertain=[...state.stationsByCopy.values()].flat().filter(s=>s.geolocation_certainty==='probable');assert.ok(uncertain.length);
for(const s of [...state.stationsByCopy.values()].flat())if(s.map_point_policy==='no_locality_point')assert.equal(hasPoint(s),false);
const burgdorf=[...state.stationsByCopy.values()].flat().find(s=>s.source_location_label==='Burgdorf');assert.ok(burgdorf);assert.ok(point(burgdorf)[0]>46&&point(burgdorf)[0]<48);
const copy=state.copies.find(c=>copyCollections(c).includes('devotional'));openDetail(copy.copy_id);assert.ok(els['detail-content'].innerHTML.includes(copy.mei_id));
for(const year of [1450,1500,1800,2026]){state.year=year;render({list:false});}
state.view='locations';render({list:false});
changeCollection('devotional',false);assert.equal(displayedCopies().length,2309);
state.collections=new Set();render();assert.equal(displayedCopies().length,0);
console.log('All collection combinations, deduplication, filters, locality policies, detail view and both map modes passed.');
`,context);
