import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_table
import json
import pandas as pd
from dash.dependencies import Input,Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)

colors = {
    'background':'#111111',
    'text': '#7FDBFF'
}

databasetypes=[{'label':'Postgres','value':'pg'},{'label':'Mysql','value':'msl'},{'label':'Vertica','value':'vca'}]

def generate_table(dataframe,max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns 
            ]) for i in range(min(len(dataframe),max_rows))
        ])
    ])

def filter_table(dataframe):
    return dash_table.DataTable(
        id="datatable-advanced-filtering",
        columns=[
            {"name": i, 'id':i,'deletable':True} for i in dataframe.columns
            if i != 'id'
        ],
        data = dataframe.to_dict('records'),
        editable=True,
        page_action='native',
        page_size=10,
        filter_action="native"
    )

markdown_text = '''
###Dash and markdown notes:\n
The status of the **databases are *ok.
'''
df = pd.DataFrame({
    "fruit":["Apples","Oranges","Bananas"],
    "Amount": [4,1,5],
    "city":['SF','TX','NY'],
    "pg":['23','34','3']
})
fig = px.bar(df,x = "fruit", y="Amount",color="city",barmode="group")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text'],

)
app.layout = html.Div(style={'backgroundColor':colors['background']},children=[
    html.H1(
        children = "Monitor",
        style={
            'textAlign':'left',
            'color':colors['text']
        }
        ),
    html.Div(children = 'DashBoard for Postgres and Mysql monitoring',style={
        'color':colors['text']
    }),
    dcc.Graph(id="Example-graph",figure=fig),
    generate_table(df),
    dcc.Markdown(children=markdown_text, style={'color':colors['text']}),
    #More on dcc componets
    html.Div([
    html.Label('DATABASE TYPE'),
    dcc.Dropdown(
        options=databasetypes
    ),
    ], style={'columnCount': 1}),
    html.Div(["hostname",
     dcc.Input(id='my-input',value='MTL',type='text')]),
    dcc.Markdown(children=markdown_text),
    html.Br(),
    html.Div(id='my-output'),
    html.Br(),
    html.Div([
        dcc.RadioItems(
            id="filter-query-read-write",
            options=[
                {'label':'Read filter_query','value':'read'},
                {'label':'Write to filter_query','value':'write'}
            ],
            value='read'
        ),
        html.Br(),
        dcc.Input(id='filter-query-input',placeholder='Enter filter query'),

        html.Div(id='filter-query-output'),
        html.Hr(),
        filter_table(df),
        html.Hr(),
        html.Div(id='datatable-query-structure',style={'whitespace':'pre'})
        
    ])
])

@app.callback(
    Output(component_id='my-output',component_property='children'),
    [Input(component_id='my-input',component_property='value')],
)
def update_output_div(input_value):
    return 'Output: {}'.format(input_value)

@app.callback(
    [Output('filter-query-input', 'style'),
    Output('filter-query-output', 'style')],
    [Input('filter-query-read-write', 'value')]
)
def query_input_output(val):
    input_style = {'width': '100%'}
    output_style = {}
    if val == 'read':
        input_style.update(display='none')
        output_style.update(display='inline-block')
    else:
        input_style.update(display='inline-block')
        output_style.update(display='none')
    return input_style, output_style


@app.callback(
    Output('datatable-advanced-filtering', 'filter_query'),
    [Input('filter-query-input', 'value')]
)
def write_query(query):
    if query is None:
        return ''
    return query


@app.callback(
    Output('filter-query-output', 'children'),
    [Input('datatable-advanced-filtering', 'filter_query')]
)
def read_query(query):
    if query is None:
        return "No filter query"
    return dcc.Markdown('`filter_query = "{}"`'.format(query))


@app.callback(
    Output('datatable-query-structure', 'children'),
    [Input('datatable-advanced-filtering', 'derived_filter_query_structure')]
)
def display_query(query):
    if query is None:
        return ''
    return html.Details([
        html.Summary('Derived filter query structure'),
        html.Div(dcc.Markdown('''```json
{}
```'''.format(json.dumps(query, indent=4))))
    ])


if __name__=='__main__':
    app.run_server(debug=True)