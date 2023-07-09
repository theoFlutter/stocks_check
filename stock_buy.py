# %%
import stock_check as sc
import datetime as dt
import numpy as np
import pandas as pd
import MACD as md
import yfinance as yf

import warnings 
warnings.filterwarnings('ignore')

# %%
# initial value
period = '6mo' # monitor the stock price for 5 years
return_period = 4 # return period is 12 weeks

# %% [markdown]
# ## **HSI Stock**

# %%
# get HSI stock list
stock_list= sc.StockPrinciple.get_hsi_stock_list()

# Calculate the stock performance
hsi_stock = sc.StockPrinciple.get_stock_performance_report(stock_list, period, return_period=return_period)
hsi_stock = hsi_stock.sort_values(by=['Avg_Return'], ascending=False)
hsi_stock

# %%
# ### get the stock data
# period = '5y'
# df_index = sc.StockPrinciple.get_stock_info('0001.HK', period)
# df = pd.DataFrame()
# df.index = [d for d in df_index.index]
# for stock in stock_list:
#     temp = sc.StockPrinciple.get_stock_info(stock, period)
#     temp = pd.DataFrame(temp)
#     df[stock] = temp.Close

# # calculate the correlation matrix
# corr_matrix = pd.DataFrame(df.corr())

#tech_stock = sc.CorrelatedStock("0001.HK", sc.StockPrinciple.process_correlation_matrix("0386.HK", corr_matrix))
#tech_stock
#tech_stock.correlation_matrix

# %% [markdown]
# ## **SP500 Stock**

# %%
# get SP500 stock list
stock_list, sp500= sc.StockPrinciple.get_sp500_stock_list()
# Calculate the stock performance
stock = sc.StockPrinciple.get_stock_performance_report(stock_list, period, return_period=return_period)
stock = stock.sort_values(by=['Avg_Return'], ascending=False)
stock

# %%
# select the stock with high return and low volatility
stock[(stock['Avg_Return'] > 0.05) & (stock['Dev_Return'] < 0.05)]

# %% [markdown]
# ## **Monitor HK Stock**

# %%
# monitor the stock price list
monitor_list = ['0857.HK', '0386.HK', '0005.HK', '0700.HK', '0267.HK', '0388.HK', 
               '0836.HK', '9988.HK' ] #中國石油化工股份有限公司, 中國石油股份有限公司, 匯豐控股有限公司, 腾讯控股有限公司, 中信股份有限公司, 香港交易所有限公司, 华润电力控股,阿里巴巴

# %%
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# List of stock tickers
def export_macd_plot(tickers, file_name):
    tickers_title = [ticker for sublist in [[t, ' '] for t in tickers] for ticker in sublist]

    # List to store plots
    plots = []

    # Loop through each ticker and generate plot
    for ticker in tickers:
        check = md.Stock(ticker,'5y')
        macd = md.MACD(check)
        plot = macd.plot_macd()
        plots.append(plot)

    # Create grid of subplots
    fig = make_subplots(rows=len(tickers)*2, cols=1, subplot_titles=tickers_title)

    # Add each plot to corresponding subplot
    for i, plot in zip(range(0, 2*len(tickers),2), plots):
        row = i + 1
        col = 1
        fig.add_trace(plot.data[0], row=row, col=col)
        fig.add_trace(plot.data[1], row=row, col=col)
        fig.add_trace(plot.data[2], row=row, col=col)
        fig.add_trace(plot.data[3], row=row, col=col)

        
        # Add MACD subplot to combined layout
        row = row + 1
        fig.add_trace(plot.data[4], row=row, col=col)
        fig.add_trace(plot.data[5], row=row, col=col)
        fig.add_trace(plot.data[6], row=row, col=col)
        fig.add_trace(plot.data[7], row=row, col=col)
        fig.update_xaxes(range=[check.df.index[0], check.df.index[-1]])
    # Update layout


    fig.update_layout(
        height=5000,
        title_text='MACD and Moving Averages for Multiple Stocks',
        showlegend=False
    )


    # Write plot to HTML file
    fig.write_html(f'{file_name}_MACD.html')

# %%
export_macd_plot(monitor_list, 'HK')

# %%



