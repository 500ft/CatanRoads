/**
 * Catan Roads — composite surface-disturbance change (Phase 1)
 * ------------------------------------------------------------
 * Paste into the Earth Engine Code Editor: https://code.earthengine.google.com/
 *
 * This is NOT an NDVI road classifier. It builds a *composite surface-disturbance*
 * signal between two multi-year, same-season baselines and normalizes it against
 * the local surroundings, so that persistent, locally anomalous disturbance stands
 * out. Single 2.5-3 m tracks are sub-pixel at 10 m; the target is corridor-scale
 * structure (braided / parallel-track / network-scale disturbance) that becomes a
 * prioritized candidate for higher-resolution confirmation.
 *
 * Signal (all oriented so higher = more candidate disturbance):
 *   dNDVI  = recent - early vegetation   (loss -> disturbance)
 *   dBSI   = recent - early bare-soil     (gain -> disturbance)  [related, not independent]
 *   comp   = 0.5 * (dBSI - dNDVI)         composite disturbance magnitude
 *   z      = local-control-normalized comp (focal mean/std) -> anomaly vs surroundings
 *   persist= fraction of recent years disturbed vs the early baseline
 *
 * Wording is deliberately "candidate disturbance / recovery", not active/abandoned:
 * no classification claim is made before validation exists.
 */

// --- 1. Area of interest -----------------------------------------------------
// Right-click a spot in Google Maps and copy the two numbers (latitude, longitude),
// IN THAT ORDER. The script builds the box for you (Earth Engine uses [lon, lat]).
var centerLat = 47.9200;   // Google Maps: FIRST number
var centerLon = 106.9000;  // Google Maps: SECOND number
var halfKm    = 8;         // half-size of the box in km (8 -> ~16 x 16 km)
var aoi = ee.Geometry.Point([centerLon, centerLat]).buffer(halfKm * 1000).bounds();
Map.centerObject(aoi, 12);

// --- 2. Multi-year, same-season baselines ------------------------------------
var MONTH        = 7;                    // July: peak growing season (max contrast)
var earlyYears   = [2019, 2020, 2021];
var recentYears  = [2024, 2025, 2026];

// --- 3. Cloud/shadow/snow mask (Scene Classification band) -------------------
function maskS2(img) {
  var scl = img.select('SCL');
  var clear = scl.neq(3).and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10)).and(scl.neq(11));
  return img.updateMask(clear);
}

// --- 4. One same-season composite (NDVI + BSI) for a given year --------------
function julyComposite(year) {
  var start = ee.Date.fromYMD(year, MONTH, 1);
  var c = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi).filterDate(start, start.advance(1, 'month'))
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40)).map(maskS2).median();
  var ndvi = c.normalizedDifference(['B8', 'B4']).rename('NDVI');
  // BSI = ((SWIR+Red) - (NIR+Blue)) / ((SWIR+Red) + (NIR+Blue))
  var sr = c.select('B11').add(c.select('B4'));
  var nb = c.select('B8').add(c.select('B2'));
  var bsi = sr.subtract(nb).divide(sr.add(nb)).rename('BSI');
  return ndvi.addBands(bsi).clip(aoi).set('year', year);
}
function collFor(years) { return ee.ImageCollection(years.map(julyComposite)); }

var earlyNDVI = collFor(earlyYears).select('NDVI').median();
var earlyBSI  = collFor(earlyYears).select('BSI').median();
var recentNDVI = collFor(recentYears).select('NDVI').median();
var recentBSI  = collFor(recentYears).select('BSI').median();

// --- 5. Composite disturbance -------------------------------------------------
var dNDVI = recentNDVI.subtract(earlyNDVI);
var dBSI  = recentBSI.subtract(earlyBSI);
var comp  = dBSI.subtract(dNDVI).multiply(0.5).rename('v');   // higher = disturbance

// --- 6. Local-control normalization (anomaly vs surroundings) ----------------
// This makes "compared against local controls" true in code, not just in prose:
// regional/seasonal drift cancels; only locally anomalous disturbance survives.
var k = ee.Kernel.circle({radius: 600, units: 'meters'});
var localMean = comp.reduceNeighborhood(ee.Reducer.mean(), k).rename('v');
var localStd  = comp.reduceNeighborhood(ee.Reducer.stdDev(), k).rename('v');
var zscore = comp.subtract(localMean).divide(localStd.max(1e-4)).rename('disturbance_z');

// --- 7. Temporal persistence (fraction of recent years disturbed) ------------
var perYear = ee.ImageCollection(recentYears.map(function (y) {
  var im = julyComposite(y);
  var yd = im.select('BSI').subtract(earlyBSI)
             .subtract(im.select('NDVI').subtract(earlyNDVI)).multiply(0.5);
  return yd.gt(0.02).rename('d');
}));
var persistence = perYear.mean().rename('persistence');   // 0..1

// --- 8. Hard-mask permanent water only (soft-handle land cover elsewhere) ----
var water = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').gt(50).unmask(0);
var zMasked = zscore.updateMask(water.not());
var persistMasked = persistence.updateMask(water.not());

// --- 9. Display ---------------------------------------------------------------
var divVis = {min: -2.0, max: 2.0,
  palette: ['01665e', '5ab4ac', 'c7eae5', 'ffffff', 'f6e8c3', 'd8b365', '8c510a']};
Map.addLayer(recentNDVI, {min: 0, max: 0.8, palette: ['ffffff', '238443']}, 'NDVI recent', false);
Map.addLayer(comp.rename('disturbance'), {min: -0.2, max: 0.2,
  palette: ['01665e', 'ffffff', '8c510a']}, 'Composite disturbance (raw)', false);
Map.addLayer(zMasked, divVis, 'Candidate disturbance (local-normalized z)');
Map.addLayer(persistMasked, {min: 0, max: 1, palette: ['ffffff', '8c510a']},
  'Disturbance persistence', false);
// Static land-cover context (WorldCover 2021) — for stratification, not masking.
Map.addLayer(ee.ImageCollection('ESA/WorldCover/v200').first().clip(aoi), {}, 'WorldCover 2021', false);

// --- 10. Legend (candidate wording — no activity claim) ----------------------
var legend = ui.Panel({style: {position: 'bottom-left', padding: '8px 10px'}});
legend.add(ui.Label('Candidate surface-disturbance ' + earlyYears[0] + '-' + earlyYears[2] +
  ' vs ' + recentYears[0] + '-' + recentYears[2], {fontWeight: 'bold', fontSize: '12px', margin: '0 0 4px 0'}));
legend.add(ui.Label('■ brown  —  candidate disturbance (locally anomalous)', {color: '8c510a', fontSize: '11px', margin: '1px 0'}));
legend.add(ui.Label('■ teal   —  candidate recovery / greening', {color: '01665e', fontSize: '11px', margin: '1px 0'}));
legend.add(ui.Label('Look for PERSISTENT, LINEAR / corridor-scale features.', {fontSize: '10px', color: '555', margin: '3px 0 0 0'}));
Map.add(legend);

// --- 11. Export + run manifest ------------------------------------------------
var stack = zMasked.addBands(comp.rename('disturbance')).addBands(persistMasked).toFloat();
Export.image.toDrive({
  image: stack, description: 'disturbance_' + recentYears[0] + '_' + earlyYears[0],
  region: aoi, scale: 10, maxPixels: 1e9
});
// Rendered z-score PNG for tools/compose_figure.py:
print('Candidate-disturbance thumbnail (click):',
  zMasked.visualize(divVis).getThumbURL({dimensions: 1400, region: aoi, format: 'png'}));

// Run manifest — record what actually went into each baseline (provenance).
function countJuly(y) {
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(aoi)
    .filterDate(ee.Date.fromYMD(y, MONTH, 1), ee.Date.fromYMD(y, MONTH, 1).advance(1, 'month'))
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40)).size();
}
print('RUN MANIFEST', {
  aoi_km2: aoi.area().divide(1e6),
  month: MONTH, early_years: earlyYears, recent_years: recentYears,
  scenes_per_recent_year: ee.Dictionary.fromLists(
    recentYears.map(String), recentYears.map(countJuly)),
  scenes_per_early_year: ee.Dictionary.fromLists(
    earlyYears.map(String), earlyYears.map(countJuly))
});
print('GATE: does this survive negative controls? Compare a road-free control site before trusting any signal.');
