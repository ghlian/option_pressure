import sys
from time import sleep
import pandas as pd
import MySQLdb
from datetime import datetime, timedelta, time
from math import ceil
import configparser
import calendar

config = configparser.RawConfigParser()
config.read("sql_statements.ini")

c = calendar.Calendar(firstweekday=calendar.SUNDAY)

read_con = MySQLdb.connect(host="192.168.1.20", user="user", passwd="cookie", db="options")
#write_con = MySQLdb.connect(host="192.168.1.20", user="user", passwd="cookie", db="option_pressure_trades")

trade_columns = ['Symbol', 'Date', 'Pressure', 'Call_Interest', 'Put_Interest', 'Call_ROI', 'P']

class stock():
    def __init__(self, symbol, date, exp_dates = None, trades_df = None):
        self.exp_dates = exp_dates
        self.trades_df = trades_df
        self.symbol = symbol
        self.pressure = None
        self.hold_days = 3
        self.strike = None

        self.get_exp_date(date)
        if hasattr(self, 'expiration'):
            self.options = self.get_options(date)

        if self.strike and hasattr(self, "calls") and hasattr(self, "puts"):
            self.get_option_pressure()
            self.get_roi(date)

        if hasattr(self, "call_roi") and hasattr(self, "put_roi"):  # store results. will be stored in db later
            self.result = [self.symbol, date.strftime('%Y-%m-%d'), self.pressure, self.call_interest, self.put_interest, self.call_roi, self.put_roi]

    # Gets the nearest expiration date for the trade
    def get_exp_date(self, end_date):
        if self.exp_dates is None:
            sql = config['get_exp_date']['sql'].format(self.symbol, end_date.strftime("%Y-%m-%d"))
            sql = sql.replace('\n',' ')
            self.exp_dates = pd.read_sql(sql, read_con)
        if len(self.exp_dates)<2:
            return
        for i in range(self.hold_days):
            end_date = end_date + timedelta(days=1)
            while end_date.isoweekday() not in range(1, 6):
                end_date = end_date + timedelta(days=1)
        self.end_date = end_date

        monthcal = c.monthdatescalendar(end_date.year, end_date.month)
        third_friday = [day for week in monthcal for day in week if \
                        day.weekday() == calendar.FRIDAY and \
                        day.month == end_date.month][2]

        if self.end_date<datetime.combine(third_friday, time()):
            self.expiration = self.exp_dates.iloc[0]['Expiration_Date']
        else:
            self.expiration = self.exp_dates.iloc[1]['Expiration_Date']


    # Gets the options available around nearest strike price
    def get_options(self, date):
        sql = config['get_options']['sql'].format(self.symbol, date.strftime("%Y-%m-%d"), self.expiration)
        options = pd.read_sql(sql, read_con)

        if options.empty:
            return

        self.strike = round(float(options.iloc[0]['Last_Stock_Price']))  # round the last stock price
        last_price_index = options[(options['strike']==self.strike) & (options['Type_Option']=='C')].index[0]
        options = options.iloc[last_price_index-4:last_price_index+6]

        self.calls = options[options['Type_Option']=="C"]
        self.puts = options[options['Type_Option']=="P"]

        if len(self.calls)!=len(self.puts):
            return None

        self.call_trade = options[(options['Type_Option']=="C") & (options['strike']==self.strike)].iloc[0]
        self.put_trade = options[(options['Type_Option']=="P") & (options['strike']==self.strike)].iloc[0]
        self.call_interest = self.call_trade['open_int']
        self.put_interest = self.put_trade['open_int']

        return options

    # Returns option pressure function I created
    def get_option_pressure(self):
            call_pressure = self.calls[['ask','bid']].sum()
            call_pressure = call_pressure['ask'] + call_pressure['bid']
            put_pressure = self.puts[['ask','bid']].sum()
            put_pressure = put_pressure['ask'] + put_pressure['bid']
            try:
                self.pressure = call_pressure/(call_pressure+put_pressure)
            except:
                pass

    # Returns the ROI on the call and put trade
    def get_roi(self, date):
        sql = config['get_roi']['sql'].format(self.symbol, self.end_date.strftime("%Y-%m-%d"), self.expiration, self.strike)
        df = pd.read_sql(sql, read_con)

        if not df.empty:
            print(self.call_trade)
            buy_price = float(self.call_trade['Last_Option_Price'])
            sell_price = float(df.iloc[0]['Last_Option_Price'])
            self.call_roi = (sell_price-buy_price)/buy_price

            buy_price = float(self.put_trade['Last_Option_Price'])
            sell_price = float(df.iloc[1]['Last_Option_Price'])
            self.put_roi = (sell_price-buy_price)/buy_price

    def store_trade(self, trades_df):
        if trades_df is None:
            trades_df = pd.DataFrame(columns = trade_columns)

    # Returns the week of the month for the specified date.
    def week_of_month(self,dt):
        first_day = dt.replace(day=1)
        dom = dt.day
        adjusted_dom = dom + first_day.weekday()
        return int(ceil(adjusted_dom/7.0))
