# Import necessary dash and plotly libraries for dashboard visualization
import dash
from dash import html
from dash import dcc
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output

# Import necessary libraries for webscraping (bs4, requests), text pattern recognition (regex),
# dataset manipulation (numpy, pandas), and sentiment analysis (nltk)
import re
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer

app = dash.Dash()

h3_desc = html.P(["A movie script visualizer based on", html.Br(), "Kurt Vonnegut's rejected master's thesis"])
instructions = html.P(["How To: Enter a movie title below. If listed on IMSDb, the code retrieves the script and performs sentiment analysis line-by-line.",
                       html.Br(), "Use the slider to adjust the smoothness of the curve. Hover over areas of the graph to see corresponding excerpts of the script."])
# Dashboard formatting using HTML components
app.layout = html.Div(id = 'parent', children = [
    html.Div(children=[
        html.H1(id = 'H1', children = 'The Shape of Stories',
                style = {'textAlign':'center', 'marginTop':40, 'marginBottom':10}),
        html.H3(id = 'H3', children = h3_desc,
                style = {'textAlign':'center', 'marginTop':10, 'marginBottom':10}),
        html.Div(id = 'Instructions', children = instructions,
                style = {'textAlign':'center', 'marginTop':10, 'marginBottom':30})
    ], style={'font-family':'Arial, sans-serif'}),
    html.Div(children=
             [dcc.Input(id='title',
                           placeholder='Input Movie Title',
                           type='string', value='')],
                     style={'display':'flex', 'justifyContent':'center'}),
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(id='graph'),
            dcc.Slider(50, 500, 50, value=250, id='slider')]),
        html.Div(id='excerpt', style={'textAlign':'center',
                                      'display': 'inline-block',
                                      'background-color' : '#E5ECF5'})
    ], style={"display": "grid", "grid-template-columns": "65% 30%"}),
    html.Div(id='json_data', style={'display': 'none'})
])

# Backend retrieval, parsing, and analysis of movie script
@app.callback(Output('json_data', 'children'),
              [Input('title', 'value'),
               Input('slider', 'value')])
def retrieve_data(title, slider):
    # Convert user input into usable URL
    if title == '':
        return 'ERROR: No title entered.'
    if title[:4] == 'The ':
        title = title[4:] + ', The'
    title = re.sub(' ', '-', title)
    url = 'https://imsdb.com/scripts/' + title + '.html'
    # Request webpage data as html block and isolate preformatted text with <pre> tag
    data  = requests.get(url).text
    soup = BeautifulSoup(data,"html.parser")
    for text in soup.find_all("pre"):
        script = text.get_text()
    if script == '':
        return 'ERROR: No script found.'
    # Remove extraneous tab and newline characters
    script = re.sub('\r', ' ', script)
    lines = re.split('\n', script)
    # Convert to pd.Dataframe and drop NaN values
    df = pd.DataFrame(lines, columns=['Lines'])
    df['Lines'].replace(' ', np.nan, inplace = True)
    df.dropna(inplace = True)
    df.reset_index(drop = True, inplace = True)
    length = len(df)
    # Create instance of SentimentAnalyzer and generate raw sentiment scores per row in df 
    sia = SentimentIntensityAnalyzer()
    df['Raw_Score'] = df.apply(lambda row:
                           sia.polarity_scores(row['Lines'])['compound'], 
                           axis=1)
    # Use slider value to provide rolling window averages of sentiment scores                   
    df['Rolling_Score'] = df['Raw_Score'].rolling(window=slider,
                                              min_periods=1,
                                              center=True,
                                              win_type='triang').mean()
    # Create two separate columns of positive/negative scores for independent graphing                                          
    df['Rolling_Score_Pos'] = df['Rolling_Score'].mask(df['Rolling_Score'] < 0, 0)
    df['Rolling_Score_Neg'] = df['Rolling_Score'].mask(df['Rolling_Score'] > 0, 0)
    #Store scores in non-displayed JSON file for sharing/updating amongst all HTML components
    return df.to_json()


# Graph sentiment scores (positive and negative independent using blue/red respectively)
@app.callback(Output('graph', 'figure'), 
              Input('json_data', 'children'))
def update_graph(json_data):
    try:
        df = pd.read_json(json_data)
    except ValueError:
        return dash.no_update
    if json_data[:5]=='ERROR':
        return dash.no_update
    red = (0.58855585831, 0.15531335149, 0.25613079019)
    blue = (0.11020408163, 0.34285714285, 0.54693877551)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index.values, y=df['Rolling_Score_Pos'],
                             fill='tozeroy', mode='none', fillcolor = '#04578B',
                             name="good fortune"))
    fig.add_trace(go.Scatter(x=df.index.values, y=df['Rolling_Score_Neg'],
                             fill='tozeroy', mode='none', fillcolor = '#BD0F40',
                             name="ill fortune"))
    fig.update_layout(
        xaxis_title = "Line #",
        yaxis_title = "Sentiment Score")
    return fig


# Use hover data to retrieve corresponding text excerpt
@app.callback(Output('excerpt', 'children'),
              [Input('json_data', 'children'),
               Input('graph', 'hoverData')])
def update_excerpt(json_data, hoverData):
    try:
        df = pd.read_json(json_data)
    except ValueError:
        return html.P(html.Br(), 'EXCERPT:')
    if json_data[:5]=='ERROR':
        return 'No Script Found :('
    excerpt_list = ['EXCERPT:', html.Br(), 
                    html.Br(), html.Br()]
    # Retrieve x-value of mouse location                
    try:
        x = hoverData['points'][0]['x']
    except TypeError:
        return html.P(html.Br(), 'EXCERPT:')
    # Fetch 20 lines corresponding to that x-value
    for i in range(20):
        excerpt_list.append(df['Lines'][x+i])
        excerpt_list.append(html.Br())
    excerpt = html.P(excerpt_list)
    return excerpt

if __name__ == '__main__': 
    app.run_server()