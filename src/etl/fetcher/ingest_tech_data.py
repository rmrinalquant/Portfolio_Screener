import yfinance as yf 
import numpy as np
import pandas as pd


def data_staging(data, pair = None , Pk_name = "Us"):
    
    staged_data = []    
    for _data in data:
        try:
            df = yf.download(tickers = _data, period = '8y', interval = '1d',group_by = 'ticker', auto_adjust = True)
        
        except Exception as e:
            print(f"Error downloading data for {_data}: {e}")
            continue

        temp_data = df.stack(level = 0).rename_axis(['Date', 'Ticker']).reset_index(level= 1)
        
        if pair is not None:
            temp_data['Stock_Id'] = temp_data['Ticker'].map(pair)
            temp_data = temp_data[['Stock_Id','Open', 'High', 'Low', 'Close', 'Volume']]   
            temp_data.reset_index(inplace = True)  
            temp_data = temp_data[['Stock_Id', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            group_data = temp_data.groupby('Stock_Id')
            print(group_data)
            for t, group in group_data:
                staged_data.extend(group.itertuples(index=False, name=None))

    return staged_data