const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const element=()=>({querySelector(){return null},scrollTop:0,value:'',textContent:'',innerHTML:'',hidden:false,classList:{add(){},remove(){}},setAttribute(){},focus(){},insertAdjacentHTML(){},addEventListener(){}});
const elements=new Map();const doc={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},addEventListener(){}};
const map={getZoom(){return this.zoom||4},setView(){return this},closePopup(){},fitBounds(){this.fits=(this.fits||0)+1}};
const layer=()=>({addTo(){return this},clearLayers(){},bindPopup(){},bindTooltip(){},on(){},setStyle(style){this.style={...this.style,...style}},bringToFront(){}});
const context=vm.createContext({console,document:doc,L:{map:()=>map,tileLayer:layer,layerGroup:layer,polyline:layer,circleMarker:layer}});
vm.runInContext(fs.readFileSync('assets/app.js','utf8').replace(/loadData\(\);\s*$/,''),context);
context.assert=assert;
vm.runInContext(`
const link={url:'https://example.org/scan',label:'A < B',sources:[{catalogue:'MEI',url:'https://data.cerl.org/mei/test'}]};
state.digitalLinks={copies:{c:[link]},editions:{e:[link,{...link,url:'https://example.org/other'},{...link,url:'javascript:alert(1)'}]}};
const html=digitalLinksHtml({copy_id:'c',host_istc_id:'e'});
assert.ok(html.includes('This copy (1)'));assert.ok(html.includes('This edition (1)'));
assert.ok(html.includes('A &lt; B'));assert.ok(!html.includes('javascript:'));
assert.equal(digitalLinksHtml({copy_id:'missing',host_istc_id:'missing'}),'');
assert.equal(state.heatRadiusKm,200);
console.log('Digital link attribution, duplicate suppression, escaping and fixed heat radius passed.');
`,context);
