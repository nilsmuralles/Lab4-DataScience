import pandas as pd

from src.config import LAGOS
from src.download import DATA_RAW
from src.indices import compute_indices
from src.mask import get_water_mask, zonal_mean

def build_temporal_table() -> pd.DataFrame:
    rows = []
    for lago, datos in LAGOS.items():
        for fecha in datos["fechas"]:
            tif_path = DATA_RAW / lago / f"{fecha}.tif"
            indices = compute_indices(lago, fecha)
            water = get_water_mask(lago, tif_path, indices["ndwi"])
            rows.append(
                {
                    "lago": lago,
                    "fecha": fecha,
                    "ndvi": zonal_mean(indices["ndvi"], water),
                    "ndwi": zonal_mean(indices["ndwi"], water),
                    "cianobacteria": zonal_mean(indices["cianobacteria"], water),
                    "pct_agua": 100 * water.sum() / water.size,
                }
            )
    df = pd.DataFrame(rows)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.sort_values(["lago", "fecha"]).reset_index(drop=True)
