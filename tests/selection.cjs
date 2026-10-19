const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const element=()=>({querySelector(){return null},querySelectorAll(){return []},scrollTop:0,value:'',textContent:'',innerHTML:'',hidden:false,classList:{add(){},remove(){}},setAttribute(){},focus(){},insertAdjacentHTML(){},addEventListener(){}});
const elements=new Map();const doc={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},addEventListener(){}};
const map={getZoom(){return this.zoom||4},setView(){return this},closePopup(){},fitBounds(){this.fits=(this.fits||0)+1}};
const layer=()=>({addTo(){return this},clearLayers(){},bindPopup(){},bindTooltip(){},on(){},setStyle(style){this.style={...this.style,...style}},bringToFront(){}});
const context=vm.createContext({console,document:doc,L:{map:()=>map,tileLayer:layer,layerGroup:layer,polyline:layer,circleMarker:layer}});
vm.runInContext(fs.readFileSync('assets/app.js','utf8').replace(/loadData\(\);\s*$/,''),context);

context.assert=assert;
vm.runInContext(`
state.copies=[
 {copy_id:'a',title:'Antidotarius animae',collection_groups:'core'},
 {copy_id:'b',title:'Hortulus animae',collection_groups:'core'},
 {copy_id:'c',title:'Antidotarius animae',collection_groups:'core'},
 {copy_id:'d',title:'Supplement',collection_groups:'liturgy'}
];
state.selected=new Set(['a','b','d']);
state.search='antidotarius';
addCheckedMatches();addCheckedMatches();
assert.equal(state.savedCopies.size,1);
assert.ok(state.savedCopies.has('a'));assert.ok(!state.savedCopies.has('c'));
state.search='hortulus';addCheckedMatches();assert.equal(state.savedCopies.size,2);
assert.equal(displayedCopies().length,1);
state.showSaved=true;assert.equal(displayedCopies().length,2);
state.collections.clear();state.places.add('Impossible');state.search='no match';
assert.equal(displayedCopies().length,2);
renderList();renderSelectionControls();
assert.ok(els['print-list'].innerHTML.includes('Antidotarius'));
assert.ok(els['print-list'].innerHTML.includes('Hortulus'));
assert.equal(els['search-controls'].hidden,true);
state.savedCopies.delete('a');assert.equal(displayedCopies().length,1);
state.showSaved=false;assert.equal(displayedCopies().length,0);
state.savedCopies.clear();renderSelectionControls();
assert.equal(els['show-selection'].disabled,true);
assert.equal(els['clear-selection'].disabled,true);
console.log('Multi-search selection, unchecked exclusion, deduplication, independent display, removal and empty state passed.');
`,context);
