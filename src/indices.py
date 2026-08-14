from pathlib import Path
import numpy as np
import rasterio

from src.download import DATA_RAW

DATA_PROCESSED = DATA_RAW.parent / "processed"

def _read_bands(tif_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    with rasterio.open(tif_path) as src:
        raw = src.read(masked=True).astype(np.float32)
    green, red, red_edge, nir = np.ma.filled(raw, np.nan) / 10000
    return green, red, red_edge, nir

def _normalized_difference(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    denom = a + b
    with np.errstate(invalid="ignore", divide="ignore"):
        result = (a - b) / denom
    result = np.where(np.abs(denom) < 1e-6, np.nan, result)
    return np.clip(result, -1, 1)

def ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    return _normalized_difference(nir, red)

def ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
    return _normalized_difference(green, nir)

def ndci(red: np.ndarray, red_edge: np.ndarray) -> np.ndarray:
    return _normalized_difference(red_edge, red)

def cianobacteria(red: np.ndarray, red_edge: np.ndarray) -> np.ndarray:
    ndci_v = ndci(red, red_edge)
    return 826.57 * ndci_v**3 - 176.43 * ndci_v**2 + 19 * ndci_v + 4.071

def compute_indices(lago: str, fecha: str) -> dict[str, np.ndarray]:
    tif_path = DATA_RAW / lago / f"{fecha}.tif"
    green, red, red_edge, nir = _read_bands(tif_path)
    return {
        "ndvi": ndvi(red, nir),
        "ndwi": ndwi(green, nir),
        "cianobacteria": cianobacteria(red, red_edge),
    }

def save_index(lago: str, fecha: str, nombre_indice: str, array: np.ndarray, profile: dict) -> Path:
    out_dir = DATA_PROCESSED / lago
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{fecha}_{nombre_indice}.tif"

    profile = profile.copy()
    profile.update(count=1, dtype="float32", nodata=np.nan)
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(array.astype(np.float32), 1)
    return out_path

def compute_and_save(lago: str, fecha: str) -> dict[str, Path]:
    tif_path = DATA_RAW / lago / f"{fecha}.tif"
    with rasterio.open(tif_path) as src:
        profile = src.profile

    indices = compute_indices(lago, fecha)
    return {
        nombre: save_index(lago, fecha, nombre, array, profile)
        for nombre, array in indices.items()
    }
