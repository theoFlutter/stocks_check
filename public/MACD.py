import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass

#Crate stock data class
@dataclass
class Stock:
    ticker: str
    period: str
    df: pd.DataFrame = None

    def __post_init__(self):
        stock = yf.Ticker(self.ticker)
        df = stock.history(period=self.period)
        self.df = df.set_index(pd.DatetimeIndex(df.index.values))

class MACD:
    '''
    Buy Indicators:
    1. If MACD > Signal Line and above Zero Line, buy
    2. If Price > 200 days moving average, buy

    Sell Indicators:
    1. If MACD < Signal Line and below Zero Line, sell
    2. If Price < 200 days moving average, sell
    
    '''

    def __init__(self,stock):
        self.ticker = stock.ticker
        self.df = stock.df
        self.prices = self.df['Close']

        #Calculate the MACD and Signal Line indicators

        self.ema_short = pd.Series(self.prices).ewm(span=12, adjust=False).mean()
        self.ema_long = pd.Series(self.prices).ewm(span=26, adjust=False).mean()
        self.macd_line = self.ema_short - self.ema_long
        self.macd_signal = pd.Series(self.macd_line).ewm(span=9, adjust=False).mean()
        self.macd_histogram = self.macd_line - self.macd_signal

        # Calculate moving averages 200 days
        self.ma_200 = pd.Series(self.prices).ewm(span=200, adjust=False).mean()

        # initial the index as x_values
        self.x_values = self.df.index
    
    def buy_sell(self):
        buy_list = []
        sell_list = []
        flag = -1
        for i in range(0,len(self.macd_line)):
            if self.macd_line[i] > self.macd_signal[i] and self.df.Close[i] > self.ma_200[i] and self.macd_line[i] <= 0:
                sell_list.append(np.nan)
                if flag != 1:
                    buy_list.append(self.prices[i])
                    flag = 1
                else:
                    buy_list.append(np.nan)
            elif self.macd_line[i] < self.macd_signal[i] and self.df.Close[i] < self.ma_200[i] and self.macd_line[i] >= 0:
                buy_list.append(np.nan)
                if flag != 0 and flag != -1:
                    sell_list.append(self.prices[i])
                    flag = 0
                else:
                    sell_list.append(np.nan)
            else:
                buy_list.append(np.nan)
                sell_list.append(np.nan)
        return (buy_list,sell_list)

    # def buy_sell(self):
    #     buy_list = []
    #     sell_list = []

    #     for i in range(0,len(self.macd_line)):
    #         if self.macd_line[i] > self.macd_signal[i] and self.macd_line[i] == 0 and self.df.Close[i] > self.ma_200[i] :
    #             buy_list.append(self.df.Close[i])
    #             sell_list.append(np.nan)
    #         elif self.macd_line[i] < self.macd_signal[i] and self.macd_line[i] == 0:
    #             buy_list.append(np.nan)
    #             sell_list.append(self.df.Close[i])
    #         else:
    #             buy_list.append(np.nan)
    #             sell_list.append(np.nan)
    #     return (buy_list,sell_list)

    def plot_macd(self):
        # Create moving averages subplot
        fig_ma = go.Figure()

        # Add original price line
        fig_ma.add_trace(go.Scatter(
            x=self.x_values,
            y=self.prices,
            mode='lines',
            name='Price',
            line=dict(color='black', width=2)
        ))


        # Add 200-day moving average line
        fig_ma.add_trace(go.Scatter(
            x=self.x_values,
            y=self.ma_200,
            mode='lines',
            name='200-day EMA',
            line=dict(color='green')
        ))
        # plot the chart to show buy and sell signals by plotly
        buy_sell = self.buy_sell()
        self.df['Buy_Signal_Price'] = buy_sell[0]
        self.df['Sell_Signal_Price'] = buy_sell[1]

        fig_ma.add_trace(go.Scatter(x=self.x_values, y=self.df['Buy_Signal_Price'], name='Buy Signal', mode='markers', marker=dict(color='green', size=10)))
        fig_ma.add_trace(go.Scatter(x=self.x_values, y=self.df['Sell_Signal_Price'], name='Sell Signal', mode='markers', marker=dict(color='red', size=10)))

        # Customize moving averages layout
        fig_ma.update_layout(
            title='Price with Moving Averages',
            xaxis_title='Period',
            yaxis_title='Value',
        )

        # Create the combined layout


        # Create MACD plot
        fig_macd = go.Figure()

        # Add MACD line
        fig_macd.add_trace(go.Scatter(
            x=self.x_values,
            y=self.macd_line,
            mode='lines',
            name='MACD Line',
            line=dict(color='blue')
        ))

        # Add signal line
        fig_macd.add_trace(go.Scatter(
            x=self.x_values,
            y=self.macd_signal,
            mode='lines',
            name='Signal Line',
            line = dict(color='orange')
        ))

        # Add histogram
        fig_macd.add_trace(go.Bar(
            x=self.x_values,
            y=self.macd_histogram,
            marker_color= ['red' if hist <0 else 'blue' for hist in self.macd_histogram],
            name='Histogram'
        ))

        # Customize layout
        fig_macd.update_layout(
            title='MACD Line with Signal Line and Histogram',
            xaxis_title='Period',
            yaxis_title='Value',
        )


        fig_macd.add_trace(go.Scatter(
            x=self.x_values,
            y=[0] * len(self.prices),
            mode='lines',
            name='Zero Line'
        ))


        # Create the combined layout

        fig = make_subplots(rows=2, cols=1)
        fig.update_xaxes(range=[self.x_values[0], self.x_values[-1]])


        # Add the moving averages subplot to the combined layout
        fig.add_trace(fig_ma.data[0], row=1, col=1)
        fig.add_trace(fig_ma.data[1], row=1, col=1)
        fig.add_trace(fig_ma.data[2], row=1, col=1)
        fig.add_trace(fig_ma.data[3], row=1, col=1)

        # Add the MACD subplot to the combined layout
        fig.add_trace(fig_macd.data[0], row=2, col=1)
        fig.add_trace(fig_macd.data[1], row=2, col=1)
        fig.add_trace(fig_macd.data[2], row=2, col=1)
        fig.add_trace(fig_macd.data[3], row=2, col=1)



        # Update the combined layout
        fig.update_layout(
            height=600,
            title_text=f'{self.ticker} MACD and Moving Averages',
            showlegend=True
        )



        # Show the combined plot
        return fig
    

#run
if __name__ == "__main__":
    stock = Stock('9988.HK','5y')
    macd = MACD(stock)
    macd.plot_macd()