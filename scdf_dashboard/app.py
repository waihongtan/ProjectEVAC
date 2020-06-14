import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import plotly.express as px
import datetime

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

new_df = pd.read_csv(r"dummy_values.csv")

color_scale = ['#43de5a','#e3972d','#e84c20']

# App layout

app.layout = html.Div(children=[
                    html.H1('EVAC Dashboard', style={'textAlign': 'center', 'borderBottom': 'solid black 2px', 'padding' : '20px'}),
                    html.Div(id='live-update-text',
                             style={'font-size': '10px', 'textAlign' : 'center'}),
                    dcc.Interval(
                                id='interval-component',
                                interval=1*1000, # in milliseconds
                                n_intervals=0
                        ),
                      html.Div(className='row',  # Define the row element
                               children=[
                                  html.Div(className='four columns div-user-controls', children = [
                                        html.H3('Unattended cooking fire'),
                                        html.P('''4 users connected...'''),
                                        html.P('''Sorted according to highest priority metric'''),
                                        html.Ul(className='fellows',
                                                 children=[
                                                        html.Ul(children=[html.Button(id='1', n_clicks=0)]),
                                                        html.Ul(children=[html.Button(id='2', n_clicks=0)]),
                                                        html.Ul(children=[html.Button(id='3', n_clicks=0)]),
                                                        html.Ul(children=[html.Button(id='4', n_clicks=0)]),
                                                        html.Button("Click to change dataset", id='change', n_clicks=0),
                                                         ])
                                    ]),  # Define the left element
                                  html.Div(className='eight columns div-for-charts bg-grey',
                                           children=[dcc.Graph(id='graph'),
                                                     html.Div(id='my-div-name', style={'padding':'30px 0px 0px 0px'}),
                                                     html.Div(id='my-div-location'),
                                                     html.Div(id='my-div-age'),
                                                     html.Div(id='my-div-info')
                                                     ])
                                  ], style={'textAlign': 'center'}),
                                    html.Div(id='output_change'),]
                                )

tracker = [0,0,0,0]
@app.callback([Output('my-div-name', 'children'), Output('my-div-location', 'children'), Output('my-div-age', 'children'), Output('my-div-info', 'children')],
              [Input('1', 'n_clicks'), Input('2', 'n_clicks'), Input('3', 'n_clicks'), Input('4', 'n_clicks')],[State('change', 'n_clicks')])
def update_now(s1,s2,s3,s4,c1):
    s = [s1,s2,s3,s4]
    clicked = -1
    for i,num in enumerate(s):
        if num == None:
            pass
        elif num == tracker[i] + 1:
            clicked = i
            tracker[i] += 1
    if clicked == -1:
        return "Select an individual","","",""
    else:
        if c1 == None:
            my_df = new_df.iloc[0:4].copy()
        else:
            option = c1%9
            my_df = new_df.iloc[option*4:(option+1)*4].copy()
        name = my_df['name'].iloc[clicked]
        location = my_df['location'].iloc[clicked]
        age = my_df['age'].iloc[clicked]
        info = my_df['info'].iloc[clicked]
        return "NAME : {}".format(name), "LOCATION : {}".format(location), "AGE : {}".format(age), "INFO : {}".format(info)
    
@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_date(n):
      return [html.P('Last updated ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]
  
@app.callback([Output('graph', 'figure'), 
               Output('1', 'children'), 
               Output('2', 'children'), 
               Output('3', 'children'), 
               Output('4', 'children'),
               Output('1', 'style'),
               Output('2', 'style'),
               Output('3', 'style'),
               Output('4', 'style')],
              [Input('change', 'n_clicks')])
def update_dataset(change):
    if change == None:
        my_df = new_df.iloc[0:4].copy()
    else:
        option = change%9
        my_df = new_df.iloc[option*4:(option+1)*4].copy()
        
    my_df["data"] = "Name: " + my_df["name"] + " || Location: " + my_df["location"]
    fig = px.scatter_mapbox(my_df, lat="lat", lon="long", hover_name="text", hover_data=["data", "info"],
                        color_continuous_scale=color_scale ,zoom=10, height=400, size_max=30, size="case", color="case")
    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "source": [
                    "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                ]
            }
          ],
        geo = dict(resolution=50)
            )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    s0 = {'backgroundColor' : my_df['color'].iloc[0]}
    s1 = {'backgroundColor' : my_df['color'].iloc[1]}
    s2 = {'backgroundColor' : my_df['color'].iloc[2]}
    s3 = {'backgroundColor' : my_df['color'].iloc[3]}

    return fig, my_df['desp'].iloc[0], my_df['desp'].iloc[1], my_df['desp'].iloc[2], my_df['desp'].iloc[3], s0, s1, s2, s3

if __name__ == '__main__':
    app.run_server()