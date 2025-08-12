
from typing import Optional
from pathlib import Path
import sys
import geopandas as gpd
import pandas as pd

try:
    parent_dir = Path(__file__).resolve().parent
    parent_dir_str = str(parent_dir)
    if parent_dir_str not in sys.path:
        sys.path.insert(0, parent_dir_str)
    
    from utils.logging_helper import BasicLogger
    from utils.geo_plots import GeoPlots
    from utils.data_loader import Dataset

    
except ImportError as e:
    print(f"Failed to import required tools\n{str(e)}")

_logger = BasicLogger(verbose = False,
                      logger_name="DASH_APP",
                      log_directory=None)

def make_geo_df()->Optional[gpd.GeoDataFrame]:
    csv_url = "https://download.ons.gov.uk/downloads/datasets/uk-business-by-enterprises-and-local-units/editions/2022/versions/1.csv"
    try:
        _logger.info(f"Getting businesses data from {csv_url}")
        businesses_data = Dataset(doc_url=csv_url).load_data()
        businesses_df = pd.DataFrame(businesses_data)
        _logger.info("Sucessfully obtained businesses data")
    except Exception as e:
        _logger.error(f"Failed to get business data", e)
        
        return
    
    businesses_df.columns = [col.lower() for col in businesses_df.columns]

    businesses_df.rename(columns={'administrative-geography': 'LAD25CD', 
                             'geography': 'LAD25NM',
                            'v4_0' : 'observation',
                              "unofficialstandardindustrialclassification" : "industry",
                            'time' : 'year',
                            "empcount" : "observation"}, 
                    inplace=True)
    
    geojson_url = "https://open-geography-portalx-ons.hub.arcgis.com/api/download/v1/items/3da2689754f449e2a4f6cd901c99dbd9/geojson?layers=0"
    try:
        _logger.info(f"Getting LAD geo data from {geojson_url}")
        lad_geo = gpd.read_file(geojson_url)
        _logger.info("Sucessfully obtained LAD geo data")
    except Exception as e:
        _logger.error(f"Failed to get LAD geo data", e)
        return
    
    geo_df_merged = lad_geo[['LAD25CD', 'geometry']].merge(businesses_df, on = "LAD25CD").set_index("LAD25CD")
    geo_df_merged.to_file("geo_df.geojson", driver="GeoJSON")
    return
    #return geo_df_merged

if __name__ == "__main__":
    make_geo_df()
