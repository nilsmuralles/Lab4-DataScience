from pathlib import Path
from src.config import BANDS_NDVI_NDWI, LAGOS

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

def _output_path(lago: str, fecha: str) -> Path:
    return DATA_RAW / lago / f"{fecha}.tif"

def download_scene(connection, lago: str, fecha: str) -> Path:
    out_path = _output_path(lago, fecha)
    if out_path.exists():
        return out_path

    cube = connection.load_collection(
        "SENTINEL2_L2A",
        spatial_extent=LAGOS[lago]["bbox"],
        temporal_extent=[fecha, fecha],
        bands=BANDS_NDVI_NDWI,
    )
    cube.download(out_path, format="GTiff")
    return out_path

def download_lago(connection, lago: str) -> list[Path]:
    return [download_scene(connection, lago, fecha) for fecha in LAGOS[lago]["fechas"]]

def download_all(connection) -> dict[str, list[Path]]:
    return {lago: download_lago(connection, lago) for lago in LAGOS}
