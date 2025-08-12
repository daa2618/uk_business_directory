import pandas as pd
import geopandas as gpd

from dash import Dash, dcc, html, Input, Output, callback
from pathlib import Path
import sys
import webbrowser

try:
    parent_dir = Path(__file__).resolve().parent
    parent_dir_str = str(parent_dir)
    if parent_dir_str not in sys.path:
        sys.path.insert(0, parent_dir_str)
    
    from utils.logging_helper import BasicLogger
    from utils.geo_plots import GeoPlots

    
except ImportError as e:
    print(f"Failed to import required tools\n{str(e)}")

_logger = BasicLogger(verbose = False,
                      logger_name="DASH_APP",
                      log_directory=None)


geo_plots = GeoPlots(country="United Kingdom")


GEO_DF = gpd.read_file("geo_df.geojson")

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(id = 'industry',
                    options = GEO_DF['industry'].unique(),
                    value = GEO_DF['industry'].unique()[0])
    ], style = {'width' : '40%',
               'display' : 'inline-block'}),
    
    html.Div([
        dcc.Dropdown(id = 'geocategory',
                    options = GEO_DF['enterprisesandlocalunits'].unique(),
                    value = GEO_DF['enterprisesandlocalunits'].unique()[0])
    ], style = {'width' : '40%',
               'display' : 'inline-block'}),
    
    dcc.Graph(id = 'plot')
])

@callback(Output(component_id='plot',
                component_property='figure'),
         Input(component_id='industry',
              component_property='value'),
         Input(component_id='geocategory',
              component_property='value'))

def make_employee_distribution(industry, geo_category):

    df_filtered = (
        GEO_DF
        .loc[(GEO_DF["enterprisesandlocalunits"]==geo_category) & \
             (GEO_DF["industry"]==industry)]
    )

    geo_plots.df = df_filtered
    fig = geo_plots.plot_choropleth_map("observation", "LAD25NM",
                                        simplify_polygon_to=1000,

                             custom_data_cols=["LAD25CD", "LAD25NM", "observation", "industry"])

    
    return fig

if __name__ == '__main__':
    if not GEO_DF.empty and not GEO_DF is None:

        webbrowser.open_new("http://127.0.0.1:8051/")
        app.run(debug=True ,use_reloader=False, port=8051
                    )





    