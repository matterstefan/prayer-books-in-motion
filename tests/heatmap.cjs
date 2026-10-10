const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const element=()=>({querySelector(){return null},scrollTop:0,value:'',textContent:'',innerHTML:'',hidden:false,classList:{add(){},remove(){}},setAttribute(){},focus(){},insertAdjacentHTML(){},addEventListener(){}});
const elements=new Map();const doc={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},addEventListener(){}};
const map={getZoom(){return this.zoom||4},setView(){return this},closePopup(){},fitBounds(){this.fits=(this.fits||0)+1}};
const layer=()=>({addTo(){return this},clearLayers(){},bindPopup(){},bindTooltip(){},on(){},setStyle(style){this.style={...this.style,...style}},bringToFront(){}});
const context=vm.createContext({console,document:doc,L:{map:()=>map,tileLayer:layer,layerGroup:layer,polyline:layer,circleMarker:layer}});
vm.runInContext(fs.readFileSync('assets/app.js','utf8').replace(/loadData\(\);\s*$/,''),context);

const canvas={style:{},setAttribute(){},getContext(){return {createImageData(w,h){return {data:new Uint8ClampedArray(w*h*4)}},putImageData(image){canvas.image=image}}}};
doc.createElement=()=>canvas;
map.getContainer=()=>({appendChild(){}});map.getSize=()=>({x:800,y:500});map.getCenter=()=>({lat:48,lng:10});
map.latLngToContainerPoint=([lat,lng])=>({x:400+(lng-10)*2**map.getZoom(),y:250-(lat-48)*2**map.getZoom()});
context.assert=assert;
context.copiesText=fs.readFileSync('data/map/copies.csv','utf8');context.stationsText=fs.readFileSync('data/map/stations.csv','utf8');
vm.runInContext(`
state.copies=parseCsv(copiesText).filter(directCopy);
for(const s of parseCsv(stationsText).map(reviewedStation)){if(!state.stationsByCopy.has(s.copy_id))state.stationsByCopy.set(s.copy_id,[]);state.stationsByCopy.get(s.copy_id).push(s)}
state.copies.forEach(c=>state.selected.add(c.copy_id));state.collections=new Set(['core','liturgy','devotional']);
state.view='locations';state.locationStyle='heatmap';
const one=densityField([{x:100,y:100,weight:1}],200,200),twice=densityField([{x:100,y:100,weight:2}],200,200);
assert.ok(one.values.some(v=>v>0));for(let i=0;i<one.values.length;i++)assert.equal(twice.values[i],2*one.values[i]);
state.year=2026;render({list:false});const key=heatReference.key,max=heatReference.maximum;assert.ok(max>1);
assert.ok(state.layers.every(item=>item.baseFillOpacity===.75));
state.year=1500;render({list:false});assert.equal(heatReference.key,key);assert.equal(heatReference.maximum,max);
map.getZoom; // map itself is outside this VM; change zoom through the supplied object below.
`,context);
map.zoom=6;
vm.runInContext(`render({list:false});assert.notEqual(heatReference.key,key);const zoomKey=heatReference.key;
state.year=1800;render({list:false});assert.equal(heatReference.key,zoomKey);
state.collections=new Set();render({list:false});assert.equal(heatReference.maximum,1);
state.collections=new Set(['core']);state.locationStyle='circles';render({list:false});assert.ok(heatCanvas.hidden);assert.ok(state.layers.every(item=>item.baseFillOpacity===.22));
console.log('Heatmap passed: weighted density, stable time scale, zoom recalibration, empty selection, markers and circle transparency.');`,context);
