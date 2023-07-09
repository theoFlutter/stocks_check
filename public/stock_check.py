import datetime as dt
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

''''
-------------------------------
Function for Stock Principle
-------------------------------
version: 2023.07.09:
1. Add the function for calculating the Sharpe Ratio
2. Add the Shapre Ratio into the performance report


Stock Trading Principle:
1. Timeframe Defination (1m, 2m ,3m ,6m and 1y)
2. At least 5% return 
3. Lower than 3% volatility

Input value:
1. Ticker (e.g. AAPL)
2. Timeframe (e.g. 1y), for monitoring the stock price
3. Return period (e.g. 4 = 4 weeks), for calculating the return

Reference: https://www.youtube.com/watch?v=lObuM2O7wjY&list=PLvcbYUQ5t0UHdm6bNx3Rnj1fdpt9sGNsm&index=2


'''

@dataclass
class CorrelatedStock:
    parent_stock: str
    correlation_matrix: pd.DataFrame

    def __init__(self, parent_stock: str, correlation_matrix: pd.DataFrame):
        self.parent_stock = parent_stock
        self.correlation_matrix = correlation_matrix



class StockPrinciple:
    MIN_RETURN = 0.05
    MAX_VOLATILITY = 0.03

    # get the stock info
    @staticmethod
    def get_stock_info(ticker, period):
        stock = yf.Ticker(ticker)
        stock_info = stock.history(period=period)
        return stock_info.Close
    


    # calculate the stock return
    @staticmethod
    def perform_analysis_for_stock(ticker, period, return_period, plot_show=False):
  
        #get the data for this ticker
        try:
            df = StockPrinciple.get_stock_info(ticker, period)
        #could not find data on this ticker
        except:
            #return default values
            return -np.inf, np.inf, None
    
        df.index = [d.date() for d in df.index]
    
    #this will store all simulated returns
        pct_return_after_period = []
        buy_dates = []
        sell_dates = []
        buy_prices = []
        sell_prices = []

    #assume we buy the stock on each day in the range
        for buy_date, buy_price in df.items():
            #get price of the stock after given number of weeks
            sell_date = buy_date + dt.timedelta(weeks=return_period)
            try:
                sell_price = df[df.index == sell_date].iloc[0]
        #trying to sell on a non-trading day, skip
            except IndexError:
                continue
        
            #compute the percent return
            pct_return = (sell_price - buy_price)/buy_price
            pct_return_after_period.append(pct_return)
            buy_dates.append(buy_date)
            sell_dates.append(sell_date)
            buy_prices.append(buy_price)
            sell_prices.append(sell_price)
        
    
        #if no data collected return default values
        if len(pct_return_after_period) == 0:
            return -np.inf, np.inf, None
            #report average and deviation of the percent returns
        
        df_return = pd.DataFrame({'buy_date': buy_dates, 'buy_price': buy_prices, 'sell_date': sell_dates, 'sell_price': sell_prices, 'pct_return': pct_return_after_period})
        return np.mean(pct_return_after_period), np.std(pct_return_after_period), df_return
    
    @staticmethod
    def calculate_sharpe_ratio(df,  risk_free_rate=0.035):
        excess_returns = df.pct_return - risk_free_rate
        average_excess_return = excess_returns.mean()
        std_deviation = excess_returns.std()
        sharpe_ratio = average_excess_return / std_deviation
        return sharpe_ratio


    @staticmethod
    def plot_stock_return(ticker, period, return_period):
        df = StockPrinciple.get_stock_info(ticker, period)
        df = pd.DataFrame(df).reset_index()
        avg_return, dev_return, df_return = StockPrinciple.perform_analysis_for_stock(ticker, period, return_period)


        # Assuming you have a DataFrame with a 'Date' column and a 'Price' column


        # Create the plotly figure
        fig = make_subplots(rows=2, cols=1,vertical_spacing=0.1,subplot_titles=("Stock Price Plot", "Return Rate Plot"))

        # Add the price line plot
        fig.add_trace(go.Scatter(x=df.Date, y = df.Close,mode='lines'),row=1, col=1)
        fig.add_trace(go.Scatter(x=df_return.buy_date, y=df_return.pct_return ,mode='lines', name='Return Rate', line=dict(color='green')), row=2, col=1)


        # Customize the layout
        fig.update_layout(
            xaxis=dict(showgrid=False),  # Hide x-axis grid lines
            yaxis=dict(showgrid=False),  # Hide y-axis grid lines
            showlegend=False,             # Hide the legend
            #plot_bgcolor='yellow',         # Set the plot background color
            paper_bgcolor='white',         # Set the paper background color
            title=f"Stock Price Plot for {ticker} | {'Avg Return: %s%% | Dev Return: %s%%'%(round(100*avg_return,2), round(100*dev_return,2))}",  # Set the title
            title_font=dict(size=20),     # Customize the title font size
            height=800,                   # Set the plot height
            width=1000                     # Set the plot width
        )

        # Add a horizontal line at a specific y-value in the second plot
        y_value = avg_return # Set the y-value for the horizontal line
        fig.add_shape(type="line", x0=df_return.buy_date.iloc[0], y0=y_value, x1=df_return.buy_date.iloc[-1], y1=y_value, 
                    line=dict(color='black', width=2, dash='dash'), row=2, col=1)


        fig.show()

    @staticmethod
    def get_stock_performance_report(stock_list, period, return_period):
        Stock = []
        Avg_Return = []
        Dev_Return = []
        Sharpe_Ratio = []
        for stock in stock_list:
            avg_return, dev_return, df_return = StockPrinciple.perform_analysis_for_stock(stock, period, return_period)
            try:
                sharpe_value = StockPrinciple.calculate_sharpe_ratio(df_return)
            except:
                sharpe_value = 0
            Stock.append(stock)
            Avg_Return.append(avg_return)
            Dev_Return.append(dev_return)
            Sharpe_Ratio.append(sharpe_value)
            df = pd.DataFrame({'Stock': Stock, 'Avg_Return': Avg_Return, 'Dev_Return': Dev_Return, 'Sharpe_Ratio': Sharpe_Ratio})
        def check_principle(df):
            if df['Avg_Return'] >= StockPrinciple.MIN_RETURN and df['Dev_Return'] <= StockPrinciple.MAX_VOLATILITY:
                return True
            else:
                return False
        df['Buy'] = df.apply(check_principle, axis=1)
        return df
    
    @staticmethod
    def get_hk_stock_list():
        # Download stock list from HKEX
        path = 'https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx'

        # change stock code to int
        df = pd.read_excel(path, dtype={'Stock Code': int}, skiprows=2)

        # Select stock code less than 4800
        '''' Code < 4800: Securities listed on the Main Board and GEM and information pages'''

        df = df[df['Stock Code'] < 4800]

        # if less than 4 digits, add 0 in front and add .HK in the back
        df['Stock Code'] = df['Stock Code'].apply(lambda x: '{0:0>4}'.format(x))
        df['Stock Code'] = df['Stock Code'].astype(str) + '.HK'
        
        return df
    
    @staticmethod
    def get_hsi_stock_list():
        # Send a GET request to the website
        url = 'http://www.aastocks.com/en/stocks/market/index/hk-index-con.aspx'
        response = requests.get(url)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <a> tags containing the titles
        a_tags = soup.find_all('a', {'class': 'bmpLnk cls'})

        # Extract the titles
        stock_list = [a['title'][1:] for a in a_tags]

        return stock_list
    
    @staticmethod
    def get_sp500_stock_list():
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(url)[0]
        stock_list = sp500['Symbol'].tolist()
        return stock_list, sp500

    @staticmethod
    def process_correlation_matrix(stock_code, df_corr, corr_thr=0.7):
        # get the correlation matrix
        df_corr = df_corr[stock_code]
        df_corr = pd.DataFrame(df_corr[(df_corr >0.7) & (df_corr != 1)])
        return df_corr
    
    # Calculate the sharpe ratio
    @staticmethod
    def sharpe_ratio(stock, period, return_period):
        # avg_return, dev_return, df_return = StockPrinciple.perform_analysis_for_stock(stock, period, return_period)
        # return avg_return/dev_return
        pass