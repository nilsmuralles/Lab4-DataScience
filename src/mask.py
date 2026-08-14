from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask

from src.download import DATA_RAW

GEOJSON_DIR = DATA_RAW.parent / "geojson"
NDWI_THRESHOLD = 0.0

def _geojson_path(lago: str) -> Path:
    return GEOJSON_DIR / f"{lago}.geojson"

def _water_mask_from_geojson(lago: str, tif_path: Path) -> np.ndarray:
    gdf = gpd.read_file(_geojson_path(lago))
    with rasterio.open(tif_path) as src:
        geom = gdf.to_crs(src.crs).geometry
        out_image, _ = rio_mask(src, geom, nodata=0, filled=True)
    return out_image[0] != 0

def _water_mask_from_ndwi(ndwi: np.ndarray, threshold: float = NDWI_THRESHOLD) -> np.ndarray:
    return ndwi > threshold

def get_water_mask(lago: str, tif_path: Path, ndwi: np.ndarray) -> np.ndarray:
    if _geojson_path(lago).exists():
        return _water_mask_from_geojson(lago, tif_path)
    return _water_mask_from_ndwi(ndwi)

def zonal_mean(array: np.ndarray, water: np.ndarray) -> float:
    valid = water & ~np.isnan(array)
    return float(np.nanmean(array[valid])) if valid.any() else float("nan")
