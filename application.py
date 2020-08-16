import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
from plotly.graph_objs import *
from datetime import datetime as dt
import pickle
import re

def build_graph_title(title):
    return html.P(className="graph-title", children=title)

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
# server = app.server
application = app.server
# Import sales data
with open('data/streeteasy_for_sale_05082020.pkl', 'rb') as f:
    sales_property_parsed_list = pickle.load(f)
sales_parsed_property_df = pd.DataFrame(sales_property_parsed_list)
sales_parsed_property_df = sales_parsed_property_df.drop_duplicates(subset=['property_name'])
sales_parsed_property_df = sales_parsed_property_df[['property_name', 'latitude', 'longitude', 'id', 'taxes', 'price', 'maintenance',
       'mortgage_rate', 'mortgage_term', 'down_payment_amount',
       'down_payment_rate', 'min_down_payment_rate', 'min_down_payment_amount', 'estimated_monthly_payment',
       'layout_info', 'region_description', 'area', 'url_of_details']]
sales_parsed_property_df['longitude'] = [longitude.split('\"')[0] for longitude in sales_parsed_property_df.longitude]

latitude_list = []
for latitude in sales_parsed_property_df.latitude:
    try:
        latitude_list.append(float(latitude))
    except:
        latitude_list.append(None)
longitude_list = []
for longitude in sales_parsed_property_df.longitude:
    try:
        longitude_list.append(float(longitude))
    except:
        longitude_list.append(None)
sales_parsed_property_df['cleaned_latitude'] = latitude_list
sales_parsed_property_df['cleaned_longitude'] = longitude_list
sales_parsed_property_df = sales_parsed_property_df.dropna(subset=['cleaned_latitude', 'cleaned_longitude'])

# Import rental data
with open('data/streeteasy_for_rent_05092020.pkl', 'rb') as f:
    rental_property_parsed_list = pickle.load(f)
rental_parsed_property_df = pd.DataFrame(rental_property_parsed_list)
rental_parsed_property_df = rental_parsed_property_df.drop_duplicates(subset=['property_name'])
rental_parsed_property_df = rental_parsed_property_df[['property_name', 'latitude', 'longitude', 'rent_price', 'url_of_details',
       'layout_info', 'region_description', 'area']]

latitude_list = []
for latitude in rental_parsed_property_df.latitude:
    try:
        latitude_list.append(float(latitude))
    except:
        latitude_list.append(None)
longitude_list = []
for longitude in rental_parsed_property_df.longitude:
    try:
        longitude_list.append(float(longitude))
    except:
        longitude_list.append(None)
rental_parsed_property_df['cleaned_latitude'] = latitude_list
rental_parsed_property_df['cleaned_longitude'] = longitude_list
rental_parsed_property_df = rental_parsed_property_df.dropna(subset=['cleaned_latitude', 'cleaned_longitude'])

cleaned_rent_price_list = []
for price in rental_parsed_property_df.rent_price:
    cleaned_price = re.sub(r'[,$]', '', price)
    cleaned_rent_price_list.append(int(cleaned_price))
rental_parsed_property_df['cleaned_rent_price'] = cleaned_rent_price_list

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1Ijoiemhlbnl1c3VuIiwiYSI6ImNrYTJsaGptazBlNzQzZm1lb3VsbXAwb3cifQ.1wkPZoPAj_LbCjDDeSBEVA"

# Rental or Sales List
data_source_list = ['Rental','Sales']

# Area Selection List
area_list = ['all', 'bronx', 'brooklyn', 'manhattan', 'new-jersey', 'queens', 'staten-island']

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.H1("StreetEasy Data Analysis"),
                        html.P(
                            """Data Source Selection"""
                        ),
                        
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="data-source-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in data_source_list
                                            ],
                                            placeholder="Select Sales or Rental Data",
                                            value='Rental'
                                        )
                                    ],
                                ),
                                html.P(
                            """Area Selection"""
                        ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="area-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in area_list
                                            ],
                                            placeholder="Select an Area",
                                            value='all'
                                        )
                                    ],
                                ),
                                                             
                            ],
                        ),
                        html.P(id="total-properties"),
                        html.P(id="total-properties-selection"),
                        html.Br(),
                        html.H4("""Selected Property's Detail Info"""),
                        html.Div(id='target'),
                        html.P(id="detail_link")
                        
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        html.Div(className='row',
                        children=[dcc.Graph(id="map-graph")],
                        style={'height':450}),
                        

                        html.Div(className='row', 
                        children=[
                                #  build_graph_title('Records Number Comparison by Different Region'),
                                 html.Div(className="six columns div-for-charts bg-grey",
                                          children=[html.P("Records Number Comparison by Different Region"),
                                                    dcc.Graph(id="histogram")],
                                                    
                                          style={'height':480}),
                                #  build_graph_title('Price Comparison by Different Region'),
                                 html.Div(className="six columns div-for-charts bg-grey",
                                          children=[html.P(id="price_histogram_title"),
                                                    dcc.Graph(id="histogram2")],
                                                    
                                          style={'height':450})
                                
                                 ])
                        
                        
                        # 
                        ]
        )
    ]
)])

# Update the details URL link
@app.callback(Output("detail_link", 'children'),
             [Input("data-source-dropdown", "value"), Input("map-graph",'clickData')])
def update_url(valuePicked, clickData):
    
    if valuePicked=='Rental':
        source_df = rental_parsed_property_df
    else:
        source_df = sales_parsed_property_df
    if clickData and clickData['points'][0]['text'].split('<br>')[-1]==valuePicked:
        
        url = list(source_df[source_df.property_name==clickData['points'][0]['text'].split('<br>')[0]]['url_of_details'])[0]
    
        if 'streeteasy' not in url:
            url = 'https://streeteasy.com'+url
        result = html.Div([html.A('Link: ' + clickData['points'][0]['text'].split('<br>')[0], 
                    href=url, target='_blank')])
        # print(result)
    else:
        result = ["No Specific Property in Map is selected."]
    return result
    
# Update the preview window
@app.callback(Output("target","children"),
             [Input("data-source-dropdown", "value"), Input("map-graph",'clickData')])
def update_target_info(valuePicked, clickData):
    if valuePicked=='Rental':
        source_df = rental_parsed_property_df.copy()
        source_df['price'] = source_df.rent_price
        
    else:
        source_df = sales_parsed_property_df.copy()
        source_df['price'] = ['$ '+str(round(item/1e6, 2))+'Million' for item in source_df.price]
    # print(clickData)   
    if clickData and clickData['points'][0]['text'].split('<br>')[-1]==valuePicked:
        
        record_df = source_df[source_df.property_name==clickData['points'][0]['text'].split('<br>')[0]]
        property_name = 'Property Name: '+list(record_df['property_name'])[0]
        region_description = 'Region Description: '+list(record_df['region_description'])[0]
        layout_info = 'Layout: '+list(record_df['layout_info'])[0]
        area = 'Area: '+list(record_df['area'])[0]
        price = 'Price: '+list(record_df['price'])[0]
        info_list = [property_name, region_description, layout_info, area, price]
        clickData = None
        return html.Ul([html.Li(x) for x in info_list])
    else:
        return ""

# @app.callback(Output('map-graph','clickData'), Input("data-source-dropdown", "value"))
# def clear_clickData(valuePicked):
#     if valuePicked:
#         return {'points':[{'curveNumber': None, 'pointNumber': None, 'pointIndex': None, 'lon': None, 'lat': None, 'text': None, 'marker.color': 2300}]}
# Update the price histogram title
@app.callback(Output("price_histogram_title",'children'),
              [Input("data-source-dropdown", "value")])
def update_price_histogram_title(valuePicked):
    if valuePicked=='Rental':
        return "Rental Price Comparison by Different Region"
    else:
        return "Sales Price Comparison by Different Region"
 # Update the total number of properties Tag

@app.callback(Output("total-properties", "children"), [Input("data-source-dropdown", "value")])
def update_total_properties(valuePicked):
    rental_record_count = len(rental_parsed_property_df)
    sales_record_count = len(sales_parsed_property_df)
    if valuePicked=='Rental':
        return "Total Number of properties for rent: {}".format(rental_record_count)
    else:
        return "Total Number of properties for sale: {}".format(sales_record_count)


# Update the total properties selection Tag
@app.callback(Output("total-properties-selection", "children"), 
[Input("data-source-dropdown", "value"),Input("area-dropdown", "value")])
def update_selected_properties(valuePicked, areaValue):
    rental_record_count = len(rental_parsed_property_df)
    if areaValue=='all':
        selected_rent_count = rental_record_count
    else:
        selected_rent_count = len(rental_parsed_property_df[rental_parsed_property_df.area==areaValue])
    sales_record_count = len(sales_parsed_property_df)
    if areaValue=='all':
        selected_sales_count = sales_record_count
    else:
        selected_sales_count = len(sales_parsed_property_df[sales_parsed_property_df.area==areaValue])
    if valuePicked=='Rental':
        return "{} out of {} properties for rent are selected".format(selected_rent_count, rental_record_count)
    else:
        return "{} out of {} properties for sale are selected".format(selected_sales_count, sales_record_count)

# Update Histogram Figure based on data source selection
@app.callback(
    Output("histogram", "figure"),
    [Input("data-source-dropdown", "value")],
)
def update_histogram(valuePicked):
    if valuePicked=='Rental':
        source_df = rental_parsed_property_df.copy()
    else:
        source_df = sales_parsed_property_df.copy()
    histogram_df = source_df.groupby(['area']).count()['property_name'].reset_index()
    histogram_df.columns = ['area','count']
    xVal = list(histogram_df['area'])
    yVal = list(histogram_df['count'])
    yVal_max = max(yVal)
    yVal_min = min(yVal)
    layout = go.Layout(
            # title_text="Record Count Comparison by Different Region",
            bargap=0.01,
            bargroupgap=0,
            barmode="group",
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            showlegend=False,
            plot_bgcolor="#323130",
            paper_bgcolor="#323130",
            dragmode="select",
            font=dict(color="white"),
            yaxis=dict(
                range=[0, max(yVal) + max(yVal) / 4],
                showticklabels=False,
                showgrid=False,
                fixedrange=True,
                rangemode="nonnegative",
                zeroline=False,
            ),
            annotations=[
                dict(
                    x=xi,
                    y=yi,
                    text=str(yi),
                    xanchor="center",
                    yanchor="bottom",
                    showarrow=False,
                    font=dict(color="white"),
                )
                for xi, yi in zip(xVal, yVal)
            ],
        )
    fig = go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=go.bar.Marker(
            opacity=0.9,

            color=yVal,
            colorscale=[[0, "#02bd27"],
                         [0.5,'#eb9f34'],
                         [1, '#eb4034']],
            cmax=yVal_max,
            cmin=yVal_min,
            showscale=True
        ), 
            hoverinfo="x")
            
        
        ],
        layout=layout,
    )
    
    return fig


# Update Histogram 2 Figure based on data source selection
@app.callback(
    Output("histogram2", "figure"),
    [Input("data-source-dropdown", "value")],
)
def update_histogram2(valuePicked):
    if valuePicked=='Rental':
        source_df = rental_parsed_property_df.copy()
        histogram_df = source_df.groupby(['area']).agg({'cleaned_rent_price':np.mean}).reset_index()
        histogram_df.columns = ['area', 'price']
        
    else:
        source_df = sales_parsed_property_df.copy()
        histogram_df = source_df.groupby(['area']).agg({'price':np.mean}).reset_index()
        histogram_df2 = source_df.groupby(['area']).count()['property_name'].reset_index()

    xVal = list(histogram_df.area)
    yVal = list(histogram_df.price)
    yVal_max = max(yVal)
    yVal_min = min(yVal)
    # colorVal = [colorVal_template[round((yi-yVal_min)/(yVal_max-yVal_min)*(len(colorVal_template)-1))] for yi in yVal]

    if valuePicked=='Sales':
        layout = go.Layout(
            # title_text="Sales Price Comparison by Different Region",
            bargap=0.01,
            bargroupgap=0,
            barmode="group",
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            showlegend=False,
            plot_bgcolor="#323130",
            paper_bgcolor="#323130",
            dragmode="select",
            font=dict(color="white"),
            yaxis=dict(
                range=[0, max(yVal) + max(yVal) / 4],
                showticklabels=False,
                showgrid=False,
                fixedrange=True,
                rangemode="nonnegative",
                zeroline=False,
            ),
            annotations=[
                dict(
                    x=xi,
                    y=yi,
                    text='$ '+str(round(yi/1e6, 2))+'Millon',
                    xanchor="center",
                    yanchor="bottom",
                    showarrow=False,
                    font=dict(color="white"),
                )
                for xi, yi in zip(xVal, yVal)
            ],
        )
    else:
        layout = go.Layout(
            # title_text="Rental Price Comparison by Different Region",
            bargap=0.01,
            bargroupgap=0,
            barmode="group",
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            showlegend=False,
            plot_bgcolor="#323130",
            paper_bgcolor="#323130",
            dragmode="select",
            font=dict(color="white"),
            yaxis=dict(
                range=[0, max(yVal) + max(yVal) / 4],
                showticklabels=False,
                showgrid=False,
                fixedrange=True,
                rangemode="nonnegative",
                zeroline=False,
            ),
            annotations=[
                dict(
                    x=xi,
                    y=yi,
                    text='$ '+str(round(yi)),
                    xanchor="center",
                    yanchor="bottom",
                    showarrow=False,
                    font=dict(color="white"),
                )
                for xi, yi in zip(xVal, yVal)
            ],
        )
    # fig = make_subplots(1,2)
    fig = go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=go.bar.Marker(
            opacity=0.9,

            color=yVal,
            colorscale=[[0, "#02bd27"],
                         [0.5,'#eb9f34'],
                         [1, '#eb4034']],
            cmax=yVal_max,
            cmin=yVal_min,
            showscale=True
        ), 
            hoverinfo="x")
            
        
        ],
        layout=layout,
    )
    
    return fig

@app.callback(
    Output("map-graph", "figure"),
    [Input("data-source-dropdown", "value"),Input("area-dropdown", "value")]
)

def update_graph(valuePicked, areaValue):
    if valuePicked=='Rental':
        source_df = rental_parsed_property_df.copy()
        source_df['price'] = source_df.cleaned_rent_price
        if areaValue=='all':
            pass
        else:
            source_df = source_df[source_df.area==areaValue]
        cmax_=10000
        cmin_=0
    else:
        source_df = sales_parsed_property_df.copy()
        if areaValue=='all':
            pass
        else:
            source_df = source_df[source_df.area==areaValue]
        cmax_=2e6
        cmin_=0.1e6
    
    text_list = []
    for property_name, price, layout_info in zip(source_df.property_name, 
                                                source_df.price,
                                                source_df.layout_info):
        if valuePicked=='Rental':
            text_list.append('<br>'.join([property_name, '$ '+str(price), layout_info, 'Rental']))
        else:
            price = '$ '+str(round(price/1e6, 2)) + ' Million'
            text_list.append('<br>'.join([property_name, price, layout_info, 'Sales']))
        
    fig = go.Figure(go.Scattermapbox(
            lat=list(source_df.latitude),
            lon=list(source_df.longitude),
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=5,
                opacity=0.5,
                color=source_df.price,
                colorscale=[[0, "#02bd27"],
                            [0.5,'#eb9f34'],
                            [1, '#eb4034']],
                
                cmax=cmax_,
                cmin=cmin_,
                showscale=True
            ),
            text=text_list
        ))

    fig.update_layout(
        font=dict(color="white"),
        # height=800,
        # title_text='StreetEasy Rental Info Visualization',
        autosize=True,
        margin=go.layout.Margin(l=0, r=35, t=0, b=1),
        hovermode='closest',
        mapbox=dict(
            style="dark",
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=40.7,
                lon=-74
            ),
            pitch=0,
            zoom=9
        ),
         updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 9,
                                        "mapbox.center.lon": "-74",
                                        "mapbox.center.lat": "40.7",
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
    )
    return fig
if __name__ == "__main__":
    application.run()
