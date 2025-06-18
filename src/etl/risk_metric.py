import etl.data_ingest
import pandas as pd
import numpy as np
import yfinance as yf
from etl.db import connection
from etl.Utils import formulas
import datetime


def risk_metric(start_date, end_date, market_data, annalized_risk_free = 0):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    

    group_data = market_data.groupby('ticker')
    benchmark = group_data.get_group('^GSPC').copy()
    benchmark.rename(columns = {'close': 'Close_benchmark'}, inplace = True)
    
    stage_data = []
    missing_data = []

    for t, group in group_data:

        group.rename(columns = {'close': f'Close_{t}'}, inplace = True)
        _temp = pd.merge(group[['date',f'Close_{t}']], benchmark[['date', 'Close_benchmark']], how = 'inner', on = 'date').drop('date', axis = 1)
        # Making note of ticker with less than 5 years of data, adjusted date for the given range
        if len(_temp) < len(benchmark):
            missing_length = len(benchmark) - len(_temp)
            missing_data.append((t, missing_length))
            print(f'Ticker {t} has less than 5 years of data', missing_length)
        
        group_one_year = group[group['date'].between(start_date, end_date)]     # filtering data between start and end date
        #returns = group_one_year.pct_change()
        
        _log_returns = np.log(group_one_year[f'Close_{t}']/group_one_year[f'Close_{t}'].shift(1))
        _log_returns_annual = _log_returns.mean()*252
        _annual_ret = round((np.exp(_log_returns_annual) - 1),2)         # for metric calculation - Use discrete returns
        
        _beta_5y = round(formulas.beta(_temp),2)
        
        _logstd_dev_annual = _log_returns.std() * np.sqrt(252) 
        _std_dev_annual = round((np.exp(_logstd_dev_annual) - 1),2)        # for metric calculation - Use discrete std
        
       
        _sharp_ratio = round(((_annual_ret - annalized_risk_free)/_std_dev_annual),2)
        
        _max_dd =round(formulas.max_drawdown(group_one_year[f'Close_{t}']),2)
        
        stage_data.append((int(group_one_year['stock_id'].values[0]), float(_annual_ret),float( _std_dev_annual),float( _sharp_ratio), float(_beta_5y),float(_max_dd)))
        
        
    return stage_data
        

