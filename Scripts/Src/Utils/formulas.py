import numpy as np 
import pandas as pd
import yfinance as yf
#from sklearn.linear_model import LinearRegression 


def cgar(inital_price, final_price, n = 1):
     return ((final_price / inital_price)**1/n) - 1

def volatility(avg_ret):
     return np.std(avg_ret)*np.sqrt(252)

def beta(data):
     ret = np.log(data/data.shift(1)).dropna()
     cov = ret.cov().iloc[0,1]*252
     var = ret.iloc[:,1].var()*252
     return cov/var


def max_drawdown(data):
     data = data.pct_change().dropna()

     cumulative_return = (1+data).cumprod()
     peak = cumulative_return.expanding(min_periods=1).max()
     dd = (cumulative_return/peak)-1
     return dd.min()
     #peak = cumulative_return.expanding(min_periods=1).max()
     #print(peak)
