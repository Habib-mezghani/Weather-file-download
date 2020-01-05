# coding=UTF-8
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import flask
from numpy import *
from flask import send_file
from pyepw.epw import EPW
import plotly.graph_objs as go
import pandas as pd

import dash_table_experiments as dt
import urllib.parse
import urllib3
from io import BytesIO
import smtplib
import config
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}
Dict={}
df = pd.read_csv('EWP_data_base.csv', sep=';')
#print(df.head(5)) #print(list(set(df.region)))
region=sorted(list(set(df.Continent_Name)))
#print(list(set(df.loc[df['region'] == region[0]].Country1)))
for i in range(len(region)):
    Dict[region[i]] = sorted(list(set(df.loc[df['Continent_Name'] == region[i]].Country_Name)))
all_options = Dict

app = dash.Dash(__name__)

app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    html.Div([html.Div(dt.DataTable(rows=[{}]), style={"display": "none"})]),
    html.Div([
            html.Div([
                html.H3('Region',style={'backgroundColor':'#E74C3C', 'color': 'White'}),
                dcc.Dropdown(
                    id='region-dropdown',
                    options=[{'label': k, 'value': k} for k in all_options.keys()],
                    value='Europe',
                    multi=False
                ),
                html.H3('Country',style={'backgroundColor':'#E74C3C', 'color': 'White'}),
                dcc.Dropdown(id='Country-dropdown'),

                html.H3('City', style={'backgroundColor':'#E74C3C', 'color': 'White'}),
                dcc.Dropdown(id='City-dropdown'),

                html.Br([]),


                html.H3('Download link', style={'backgroundColor':'#50E3E7', 'color': 'White', 'margin-left':0}),

                html.Div([
                html.A('Weather file (*ewp)',id='download-link3',download="Weather.epw", className="tab"),
                #html.Br([])

                    ],className="row "),
                html.Br([]),

            ], className="six columns"),

            html.Div([
                html.H3('Location Map',style={'backgroundColor':'#239B56', 'color': 'White'}),
                html.Div(
                    id='graph_map',
                )
            ], className="six columns"),
        ], className="row",style ={'margin-left':10})
    ], style={
        'backgroundColor': '#F9F9F9',
        'fontFamily': 'Sans-Serif',
        'margin-left': 'auto',
        'margin-right': 'auto',
    })


####################################################################################################################
##################################### downpop and map setup ##############################################################
###############################################################################################################


@app.callback(
    dash.dependencies.Output('Country-dropdown', 'options'),
    [dash.dependencies.Input('region-dropdown', 'value')])
def set_country_options(selected_region):
    return [{'label': i, 'value': i} for i in all_options[selected_region]]

@app.callback(
    dash.dependencies.Output('City-dropdown', 'options'),
    [dash.dependencies.Input('Country-dropdown', 'value')])
def set_cities_options(selected_Country):
    Dict1 = {}
    Country=sorted(list(set(df.Country_Name)))
    for i in range(len(Country)):
        Dict1[Country[i]] = sorted(list(set(df.loc[df['Country_Name'] == Country[i]].city)))
    return [{'label': i, 'value': i} for i in Dict1[selected_Country]]

@app.callback(
    dash.dependencies.Output('Country-dropdown', 'value'),
    [dash.dependencies.Input('Country-dropdown', 'options')])
def set_country_value(available_options):
    return available_options[9]['value']

@app.callback(
    dash.dependencies.Output('City-dropdown', 'value'),
    [dash.dependencies.Input('City-dropdown', 'options')])
def set_city_value(available_options):
    return available_options[0]['value']


@app.callback(
    dash.dependencies.Output('graph_map', 'children'),
    [dash.dependencies.Input('region-dropdown', 'value'),
     dash.dependencies.Input('Country-dropdown', 'value'),
     dash.dependencies.Input('City-dropdown', 'value'),])
def set_display_Map(setected_region,selected_country, selected_city):
    x = list(df.loc[(df['Continent_Name'] == setected_region) & (df['Country_Name'] == selected_country) & (df['city'] == selected_city)].coorX)[0]
    y = list(df.loc[(df['Continent_Name'] == setected_region) & (df['Country_Name'] == selected_country) & ( df['city'] == selected_city)].coordY)[0]
    return html.Div(
                className="nine columns",
                children=dcc.Graph(
                    id='graph_map_MAJ',
                    figure={
                        'data': [
                            {
                            'lat': df.coordY, 'lon': df.coorX, 'type': 'scattermapbox', 'text': df.city,'name': '',
                            'mode': 'markers', 'marker': dict(size=11, color='rgb(255, 0, 0)', opacity=0.9)

                        },
                            {
                            'lat': [y], 'lon': [x], 'type': 'scattermapbox', 'text': [selected_city],'name': '',
                            'mode': 'markers', 'marker': dict(size=11, color='rgb(0, 0, 255)', opacity=0.9)

                        }
                        ],
                        'layout': {#'autosize':True,
                                    'hovermode':'closest',
                                    'showlegend':False,


                            'width':680,
                            'height':530,
                            'mapbox': {'accesstoken': (
                                    'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3M' +
                                    'DBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw'
                            ), 'center':dict(
                                    lat=y,
                                    lon=x
                                      ),'zoom':7
                            },
                            'margin': {
                                'l': 0, 'r': 0, 'b': 0, 't': 0
                            }
                        }
                    }
                )
            )



@app.callback(dash.dependencies.Output('download-link3', 'href'),
              [dash.dependencies.Input('region-dropdown', 'value'),
               dash.dependencies.Input('Country-dropdown', 'value'),
               dash.dependencies.Input('City-dropdown', 'value'), ])
def update_link(setected_region,selected_country,selected_city):
    #weather_link = str(setected_region) + '_' + str(selected_country) + '_' + str(selected_city) + '.epw'
    Link_weather=list(df.loc[(df['Continent_Name'] == setected_region) & (df['Country_Name'] == selected_country) & (df['city'] == selected_city)].EWP)[0]
    return '/dash/urlToDownload?value={}'.format(Link_weather)

@app.server.route('/dash/urlToDownload')
def download_csv():
    value = flask.request.args.get('value')
    print(value)
    Link_weather=value
    http = urllib3.PoolManager()
    r = http.request('GET', Link_weather)
    r.status

    csv_string = r.data

    strIO = BytesIO()
    strIO.write(csv_string)
    strIO.seek(0)
    return send_file(strIO,
                     mimetype='text/csv',
                     attachment_filename='downloadFile.epw',
                     as_attachment=True)



external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "https://codepen.io/bcd/pen/KQrXdb.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                "https: // codepen.io / chriddyp / pen / brPBPO.css",
                "https://codepen.io/chriddyp/pen/bWLwgP.css"]

for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server(debug=True)
