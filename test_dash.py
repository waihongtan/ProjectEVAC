import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

map_accesstoken = "pk.eyJ1Ijoienh0cmF2ZWxzIiwiYSI6ImNrOWNsYzVoYzA1NDQzbXFkMm5wcXN5cDEifQ.48BOBZwgRyj3zznw7s1MeQ"


df = px.data.carshare()

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

new_df = pd.read_csv(r"dummy_values.csv")

new_df["data"] = "Name: " + new_df["name"] + "|| Location: " + new_df["location"]

color_scale = ['#43de5a','#e3972d','#e84c20']

fig = px.scatter_mapbox(new_df, lat="lat", lon="long", hover_name="text", hover_data=["data"],
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

# App layout

app.layout = html.Div(children=[
                    html.H1('EVAC Dashboard', style={'textAlign': 'center', 'borderBottom': 'solid black 2px', 'padding' : '20px'}),
                      html.Div(className='row',  # Define the row element
                               children=[
                                  html.Div(className='four columns div-user-controls', children = [
                                        html.H3('Unattended cooking fire'),
#                                        html.Div(className='div-for-dropdown',
#                                          children=[
#                                              dcc.Dropdown(options=[
#                                                    {'label': 'Unattended cooking Fire', 'value': 'ucf'},
#                                                ],
#                                                value='ucf')
#                                                    ],
#                                          style={'color': '#1E1E1E'}),
                                        html.P('''Connected to 4 users ...'''),
                                        html.Ul(className='fellows',
                                                 children=[
                                                        html.Ul(children=[html.Button('fellow_a', id='1', n_clicks=0, style={'backgroundColor' : '#e84c20'})]),
                                                        html.Ul(children=[html.Button('fellow_b', id='2', n_clicks=0, style={'backgroundColor' : '#e84c20'})]),
                                                        html.Ul(children=[html.Button('fellow_c', id='3', value=3, style={'backgroundColor' : 'orange'})]),
                                                        html.Ul(children=[html.Button('fellow_d', id='4', value=4, style={'backgroundColor' : '#43de5a'})]),
#                                                         html.Ul(children=[html.Button(new_df['desp'][i], id="{}".format(i), value=i, style={'backgroundColor' : color_scale[new_df['case'][i]- 1]})]) for i in range(4)                                            
                                                         ])
                                    ]),  # Define the left element
                                  html.Div(className='eight columns div-for-charts bg-grey',
                                           children=[dcc.Graph(id='graph', figure=fig),
                                                     html.Div(id='my-div', style={'padding':'30px'})
                                                     ])  # Define the right element
                                  ], style={'textAlign': 'center'})
                                ])

tracker = [0,0,0,0]
@app.callback(Output('my-div', 'children'),
              [Input('1', 'n_clicks'), Input('2', 'n_clicks'), Input('3', 'n_clicks'), Input('4', 'n_clicks')])
def update_now(*s):
    print("clicked")
    clicked = -1
    for i,num in enumerate(s):
        if num == None:
            pass
        elif num == tracker[i] + 1:
            clicked = i
            tracker[i] += 1
    if clicked == -1:
        return "Select an individual"
    else:
        name = new_df['name'][clicked]
        location = new_df['location'][clicked]
        age = new_df['age'][clicked]
        return "NAME : {} || LOCATION : {} || AGE : {}".format(name, location, age)
    print(tracker)
    print(s)
    print(clicked)
    

if __name__ == '__main__':
    app.run_server()