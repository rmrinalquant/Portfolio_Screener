
from yfinance import yf
import pipeline
import pandas as pd
import numpy as np
from Scripts.Src.db import connection


rf = yf.download(tickers = "^IRX", period = '8y', interval = '1d',group_by = 'ticker', auto_adjust = True)

print(rf.head(10))
conn  = connection.get_neon_connection(pipeline.path)
cursor = conn.cursor()

query = " Select Date, m.Stock_ID,Ticker,Close \
          from MetaData_US_companies as m \
          inner join Technical_Data as t on m.Stock_Id = t.Stock_Id\
          where date between '2024-04-16' and '2025-12-20' \
          order by m.Ticker, t.date "

market_data = pd.read_sql_query(query, conn)


data = pd.read_sql_query(query, conn)

group_data = data.groupby('ticker')

for t, group in group_data:
    log_returns = group['close'].pct_change()
    log_returns_t = np.log(group['close']/group['close'].shift(1))
    print(log_returns_t.mean()*252)
    print(log_returns.mean()*252)

    break