/**
 * Desire Lines — NDVI change on-ramp
 * ----------------------------------
 * Paste this into the Google Earth Engine Code Editor:
 *   https://code.earthengine.google.com/
 *
 * It builds two cloud-masked, SAME-MONTH Sentinel-2 NDVI composites a few years
 * apart and maps their difference. On a track:
 *   NDVI went DOWN (brown)  -> vegetation lost / surface disturbed -> likely ACTIVE
 *   NDVI went UP   (green)  -> vegetation regrown                  -> likely ABANDONED
 *
 * Look for LINEAR features in the change layer — those are your route corridors.
 * This is an exploratory sketch, not a classifier. Season matching matters:
 * always compare the same month, or you measure grass growth, not road use.
 */

// --- 1. Area of interest -----------------------------------------------------
// Right-click a spot in Google Maps and copy the two numbers it shows — they are
// (latitude, longitude), IN THAT ORDER. Paste them below; the script builds a
// small box around that point, so you never worry about coordinate order or size.
//
// (Earth Engine geometries use [lon, lat] — the OPPOSITE of Google Maps — which is
// the usual reason a pasted coordinate "jumps to the wrong place". Giving a center
// point plus a size avoids the swap and keeps the box a sensible size.)
var centerLat = 47.9200;   // Google Maps: the FIRST number
var centerLon = 106.9000;  // Google Maps: the SECOND number
var halfKm    = 8;         // half-size of the box in km (8 -> ~16 x 16 km area)

var aoi = ee.Geometry.Point([centerLon, centerLat]).buffer(halfKm * 1000).bounds();

// --- 2. Comparison years (SAME month) ---------------------------------------
var earlyYear = 2019;
var lateYear  = 2025;
var month     = 7;    // July: peak growing season in Mongolia (max contrast).

// --- 3. Cloud/shadow/snow mask using the Scene Classification (SCL) band -----
function maskS2(img) {
  var scl = img.select('SCL');
  // Drop: 3 cloud-shadow, 8/9 cloud, 10 cirrus, 11 snow.
  var clear = scl.neq(3).and(scl.neq(8)).and(scl.neq(9))
                 .and(scl.neq(10)).and(scl.neq(11));
  return img.updateMask(clear);
}

// --- 4. Seasonal median NDVI for one year -----------------------------------
function seasonalNDVI(year) {
  var start = ee.Date.fromYMD(year, month, 1);
  var end   = start.advance(1, 'month');
  var col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi)
    .filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .map(maskS2);
  // NDVI = (NIR - Red) / (NIR + Red) = (B8 - B4) / (B8 + B4)
  return col.median().normalizedDifference(['B8', 'B4']).rename('NDVI').clip(aoi);
}

var ndviEarly = seasonalNDVI(earlyYear);
var ndviLate  = seasonalNDVI(lateYear);
var ndviDiff  = ndviLate.subtract(ndviEarly).rename('NDVI_change');

// --- 5. Display --------------------------------------------------------------
Map.centerObject(aoi, 12);

var ndviVis = {min: 0.0, max: 0.8, palette: ['ffffff', '74a9cf', '238443']};
Map.addLayer(ndviEarly, ndviVis, 'NDVI ' + earlyYear, false);
Map.addLayer(ndviLate,  ndviVis, 'NDVI ' + lateYear,  false);

// Diverging BrBG: brown = NDVI dropped (disturbance/active),
//                 teal  = NDVI rose (regrowth/abandonment).
var diffVis = {
  min: -0.30, max: 0.30,
  palette: ['8c510a', 'd8b365', 'f6e8c3', 'ffffff', 'c7eae5', '5ab4ac', '01665e']
};
Map.addLayer(ndviDiff, diffVis, 'NDVI change ' + earlyYear + ' -> ' + lateYear);

// --- 6. On-map legend --------------------------------------------------------
var legend = ui.Panel({style: {position: 'bottom-left', padding: '8px 10px'}});
legend.add(ui.Label('NDVI change ' + earlyYear + ' → ' + lateYear,
  {fontWeight: 'bold', fontSize: '13px', margin: '0 0 4px 0'}));
legend.add(ui.Label('■ brown  —  disturbance / active use',
  {color: '8c510a', fontSize: '11px', margin: '1px 0'}));
legend.add(ui.Label('■ green  —  regrowth / abandonment',
  {color: '01665e', fontSize: '11px', margin: '1px 0'}));
Map.add(legend);

// --- 7. Export for figure composition ----------------------------------------
// The rendered (RGB) change map, ready to drop into tools/compose_figure.py.
var diffRGB = ndviDiff.visualize(diffVis);

// (a) Quick PNG: click this printed URL to download a thumbnail.
print('Thumbnail PNG (click to download):',
  diffRGB.getThumbURL({dimensions: 1400, region: aoi, format: 'png'}));

// (b) Full-resolution rendered export to Google Drive -> compose_figure.py.
Export.image.toDrive({
  image: diffRGB,
  description: 'ndvi_change_' + earlyYear + '_' + lateYear,
  region: aoi, scale: 10, maxPixels: 1e9
});

// (c) Raw single-band NDVI-change raster for QGIS + OpenStreetMap road overlay.
Export.image.toDrive({
  image: ndviDiff.toFloat(),
  description: 'ndvi_change_raw_' + earlyYear + '_' + lateYear,
  region: aoi, scale: 10, maxPixels: 1e9
});

print('AOI area (km^2):', aoi.area().divide(1e6));
print('Next: compose the export into results/ndvi_change.png (see results/README.md).');
