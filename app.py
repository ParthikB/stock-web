import yfinance as yf
from binance.client import Client

import dash, dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def update_val(data, security):
    
    if security == 'XRP':
        api_key    = 'jfdgMTk4LEnYl54Lto18zWAvyYS2GEOfvfwfnifaQawFE9TIMUlZnjCPqubWKWoP'
        secret_key = 'H0UfJS8hCj13a3StI3IgZ46C0AfkaUS6zwf7s0bK8bDv1cqP8x49kHe4M4phVfnI'
        
        client = Client(api_key, secret_key)

        # Getting the average price of the COIN in $ and then converting into INR
        cur_price    = client.get_avg_price(symbol=f'{security}USDT')
        cur_price    = round(float(cur_price['price']) * 72, 2)

        # Getting the balance of the security
        total_shares = client.get_asset_balance(asset=security)
        total_shares = round(float(total_shares['free']), 2) - 52 - 41 - 41 # 52:Pranay, 41:Aman, 41:Mayank

        buy_price    = '--'
        
        investement  = 3500
          
    elif security == 'YESBANK.NS':
        stock          = yf.Ticker(security)
        cur_price      = stock.history('max')["Close"][-1]

        total_shares   = [71, 26]
        buy_price      = [27, 35]

        investement    = round(sum([x*y for x, y in zip(total_shares, buy_price)]), 2)
    
    ##########################################################    
    temp_total_shares = total_shares
    if type(total_shares) == list:
        temp_total_shares = sum(total_shares)
        
    returns         = round(temp_total_shares * cur_price, 2)
        
    net             = round(returns - investement, 2)
    emotion_percent = round((returns/investement)*100)

    emotion         = 'PROFIT' if net > 0 else 'LOSS'
        
   
    data[security]['Current Price'] = str(cur_price)
    data[security]['Total Shares']  = str(total_shares)
    data[security]['Buy Price']     = str(buy_price)
    data[security]['Investment']    = str(investement)
    data[security]['Returns']       = str(returns)
    data[security]['Net']           = str(net)
    
    return data



# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

def create_dummy_df():
	df = pd.DataFrame(columns=['Info','YESBANK.NS', 'XRP'])
	df['Info'] = ['Current Price', 'Total Shares', 'Buy Price', 'Investment', 'Returns', 'Net']
	df.index = df.Info
	return df
data = create_dummy_df()


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    # The memory store reverts to the default on every page refresh
    dcc.Store(id='database', storage_type='session'),

    html.Div([
    			html.H2('Stock Analysis',
		                style={'float': 'left',
		                       }),

				dash_table.DataTable(
				    id='table',
				    columns=[{"name": i, "id": i} for i in data.columns],
				    # data=data.to_dict('records'),
				),
			
			    html.Button('Update', id='button', 
			    			style={'width' : '100%', 'height':'25%'}),

			    html.Div(id='output',
             			 children='Net : Great (one day)',
			    		 )

			    

						],
				style={'font-size': '140%'},
				)
])

store = 'database'

@app.callback(Output(store, 'data'),
                  [Input('button', 'n_clicks')],
                  [State(store, 'data')])
def on_click(n_clicks, data):
    if n_clicks is None:
        raise PreventUpdate

    data = create_dummy_df()
    
    for security in ['YESBANK.NS', 'XRP']:
    	data = update_val(data, security)

    data = data.to_dict('records')
    return data


# output the stored clicks in the table cell.
@app.callback(Output('table', 'data'),
              [Input(store, 'modified_timestamp')],
              [State(store, 'data')])
def on_data(ts, data):
    if data is None:
        raise PreventUpdate

    return data


@app.callback(Output('output', 'children'),
              [Input(store, 'modified_timestamp')],
              [State(store, 'data')])
def on_data(ts, data):
    if data is None:
        raise PreventUpdate

    net_worth = 0
    for i in data:
    	if i['Info'] == 'Net':
    		for net in i.values():
    			try:
    				net_worth += float(net)
    			except:
    				pass

    return f'Net : {round(net_worth, 2)}'


if __name__ == '__main__':
    app.title = 'Stock Analysis | ParthikB'
    server = app.server
    app.run_server(debug=True)
