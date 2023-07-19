# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from pandas.core.arrays import categorical
import plotly.express as px
import pandas as pd
import psycopg2
from dash.dependencies import Input, Output
import dash_table

app = dash.Dash(__name__)

# postgres connection details
pgparams = {
    "database": "ofetdb_testenv",
    "user":"postgres",
    "password":"password",
    "host": "127.0.0.1",
    "port": "5432"
    }

def read_select_query(query):

    with psycopg2.connect(**pgparams) as conn:

        df = pd.read_sql_query(query, conn)

    return df

### QUERIES ###

q1 = '''
    SELECT mobility_cm2_vs, concentration_mgml, solvent_name, 
    surface_treatment, polymer_name, mn_kda, mw_kda, pdi, deposition_method
    FROM DEVICE, SOLUTION, POLYMER, COATING_PROCESS
    WHERE device.solution_id = solution.solution_id AND 
    solution.polymer_id = polymer.polymer_id AND
    device.coating_id = coating_process.coating_id;
    '''        

df_1 = read_select_query(q1)

continuous_vars = ['mn_kda','mw_kda', 'pdi', 'concentration_mgml']
categorical_vars = ['solvent_name', 'deposition_method', 'surface_treatment', 'polymer_name', 'electrode_config']

# fig = px.scatter(df_1, x="mw_kda", y="mobility_cm2_vs", color="solvent_name", log_y=True)

q2 = '''
    SELECT polymer_name, mw_kda, COUNT(*) FROM device, solution, polymer
    WHERE device.solution_id = solution.solution_id
    AND solution.polymer_id = polymer.polymer_id
    GROUP BY polymer_name, mw_kda;
    '''        

df_2 = read_select_query(q2)

fig2 = px.histogram(df_2, x="mw_kda", y="count", color="polymer_name", marginal="violin", nbins=40)


def q3(polymer_name):
    query = '''
    SELECT polymer.polymer_name, solvent.solvent_name, boiling_point_c, min(concentration_mgml)	
        AS min_concentration, max(concentration_mgml) AS max_concentration, count(*) AS num_expts
    FROM device, solution, solvent, polymer
    WHERE device.solution_id = solution.solution_id AND
    solution.solvent_name = solvent.solvent_name AND
    solution.polymer_id = polymer.polymer_id AND
    polymer.polymer_name = '%s'
    GROUP BY solvent.solvent_name, polymer_name
    ''' % polymer_name

    df_3 = read_select_query(query)

    return df_3

q4 = '''
    SELECT polymer_name, mobility_cm2_vs, solvent_name, deposition_method, electrode_config, surface_treatment
    FROM device, solution, polymer, coating_process, substrate
    WHERE device.coating_id = coating_process.coating_id AND 
    device.solution_id = solution.solution_id AND 
    solution.polymer_id = polymer.polymer_id AND
    device.design_id = substrate.design_id;
    '''      

df_4 = read_select_query(q4)

fig4 = px.box(df_4, 
    x="deposition_method", 
    y="mobility_cm2_vs", 
    color="polymer_name", 
    points="all",
    log_y=True
    )

q4_vars = ['solvent_name', 'deposition_method', 'surface_treatment', 'electrode_config']
polymer_names = ['P3HT', 'DPP-DTT']

app.layout = html.Div([

    # Query 1
    
    html.Div([
        html.Div([
            html.H2("Mobility Plot"),
            html.Div([
                html.Label('x-axis'),
                dcc.Dropdown(
                    id='xaxis-column',
                    options=[{'label': i, 'value': i} for i in continuous_vars],
                    value='mw_kda'
                ),
            ], style={'width': '45%', 'display': 'inline-block'}),
            html.Div([
                html.Label('Legend'),
                dcc.Dropdown(
                    id='mobility-legend',
                    options=[{'label': i, 'value': i} for i in categorical_vars],
                    value='solvent_name'
                ),
            ], style={'width': '45%', 'display': 'inline-block'}),
            
            html.Div([
                dcc.Graph(
                    id='mobility-graph',
                    # figure=fig
                ), 
            ])
        ], style={'width': '42%', 'display': 'inline-block'}),

        html.Div([], style={'width': '10%', 'display': 'inline-block'}), #spacer

        html.Div([
            html.Div([
                html.H2("Solvent Information"),
                html.H4("Check solvents tested for:"),
                dcc.Dropdown(
                    id='polymer-choice',
                    options=[{'label': i, 'value': i} for i in polymer_names],
                    value='P3HT'
                ),
                dash_table.DataTable(
                    id='solvent-table',
                    # columns=[{"name": i, "id": i} for i in df_3.columns],
                    # data=df_3.to_dict('records')
                )
            ]),    
        ], style={'width': '42%', 'display': 'inline-block'}),
    ]),
    html.Br(),

    # Query 2
    html.Div([
        
        html.Div([
            html.H2("Experimental Distribution of Molecular Weight by Polymer"),
            dcc.Graph(
                id='dist-plot',
                figure=fig2
            ), 
        ], style={'width': '42%', 'display': 'inline-block'}),
        html.Div([], style={'width': '10%', 'display': 'inline-block'}), #spacer
        html.Div([
            html.H2("Device Performance by Polymer and Categorical Process Variables"),
            dcc.Dropdown(
                id='boxplots-dropdown',
                options=[{'label': i, 'value': i} for i in q4_vars],
                value='deposition_method'
            ),
            dcc.Graph(
                id='coating-boxplots',
                figure=fig4
            ), 
        ], style={'width': '42%', 'display': 'inline-block'})



    ]),



])

# Callback for Query 1
@app.callback(
    Output('mobility-graph', 'figure'),
    Input('xaxis-column', 'value'),
    Input('mobility-legend', 'value'))
def update_graph(xaxis_column_name, legend):

    fig = px.scatter(
        df_1,
        x=xaxis_column_name,
        y='mobility_cm2_vs',
        color=legend
    )
    fig.update_yaxes(type='log')
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')


    return fig

# Callback for Query 3
@app.callback(
    Output('solvent-table', 'data'),
    Output('solvent-table', 'columns'),
    Input('polymer-choice', 'value'))
def update_table(polymer_choice):
    column_names = ['Solvent', 'Boiling Point (C)', 'Minimum Concentration', 'Maximum Concentration', '# Experiments']
    df = q3(polymer_choice)
    columns=[{"name": j, "id": i} for i,j in zip(df.columns[1:], column_names)]
    return df.to_dict('records'), columns

# Callback for Query 4
@app.callback(
    Output('coating-boxplots', 'figure'),
    Input('boxplots-dropdown', 'value'))
def update_graph(xaxis_column_name):

    fig4 = px.box(df_4, 
        x=xaxis_column_name, 
        y="mobility_cm2_vs", 
        color="polymer_name", 
        points="all",
        log_y=True
        )

    fig4.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')


    return fig4

if __name__ == '__main__':
    app.run_server(debug=True)