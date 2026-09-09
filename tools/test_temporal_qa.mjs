// Local branch/schema model only: this is NOT an Earth Engine integration test.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../gee/ndvi_change.js', import.meta.url), 'utf8');
let sceneCount = 0;
let selectedDataset = '';
class Image {
  constructor(bands, masked = false) { this.bands = bands; this.masked = masked; }
  rename(bands) { this.bands = bands; return this; }
  toFloat() { return this; }
  updateMask(mask) { this.masked = mask === 0; return this; }
  clip() { return this; }
  set() { return this; }
  select(bands) {
    assert(bands.every(b => this.bands.includes(b)), 'requested band absent');
    return new Image(bands, this.masked);
  }
}
class Collection {
  filterBounds() { return this; }
  filterDate() { return this; }
  filter() { return this; }
  map() { return this; }
  select() { return this; }
  size() { return {gt: n => sceneCount > n}; }
  median() {
    const bands = selectedDataset.includes('DYNAMICWORLD') ? ['built', 'crops', 'water'] : ['B2', 'B3', 'B4', 'B8', 'B11', 'SCL'];
    return new Image(sceneCount ? bands : []);
  }
}
const image = value => value;
image.constant = values => new Image(values.map((_, i) => String(i)));
const context = vm.createContext({
  ee: {
    Image: image,
    ImageCollection: dataset => { selectedDataset = dataset; return new Collection(); },
    Algorithms: {If: (condition, yes, no) => condition ? yes : no},
    Date: {fromYMD: () => ({advance: () => null})},
    Filter: {lt: () => null}
  },
  aoi: {}, MONTH: 7, DW_BANDS: ['built', 'crops', 'water']
});
for (const match of source.matchAll(/function \w+\([^\n]*\) \{[\s\S]*?\n\}/g)) {
  vm.runInContext(match[0], context);
}
for (sceneCount of [0, 3]) {
  const s2 = vm.runInContext('julyS2(2018)', context).select(['B2', 'B3', 'B4', 'B8', 'B11']);
  const dw = vm.runInContext('julyDynamicWorld(2018)', context).select(['built', 'crops', 'water']);
  assert.equal(s2.masked, sceneCount === 0);
  assert.equal(dw.masked, sceneCount === 0);
}
assert.match(source, /gateRecord = gateRecord\.set\('s2_scene_count_' \+ year, countJuly\(year\)\)/);
console.log('Temporal QA: empty/nonempty S2 and Dynamic World branch/schema checks PASS; export wiring present. No Earth Engine execution.');
