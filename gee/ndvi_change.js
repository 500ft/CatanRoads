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
// EDIT THIS to a rural region you know. Default: a patch of central Mongolia.
// [west, south, east, north] in degrees.
var aoi = ee.Geometry.Rectangle([106.00, 47.60, 106.40, 47.90]);

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

// --- 6. Optional: export the change raster to inspect in QGIS with OSM roads --
// Uncomment to queue an export to your Google Drive.
// Export.image.toDrive({
//   image: ndviDiff,
//   description: 'ndvi_change_' + earlyYear + '_' + lateYear,
//   region: aoi,
//   scale: 10,
//   maxPixels: 1e9
// });

print('AOI area (km^2):', aoi.area().divide(1e6));
print('Tip: pull OSM roads for this area (Geofabrik / Overpass) and overlay in QGIS.');
