from stock import stock
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
if __name__ == "__main__":
    ticker_df = pd.read_csv('tickers.csv').values.T.tolist()[0]


    columns = ['Symbol', 'Date', 'Pressure', 'Call_Open_Int', 'Put_Open_Int', 'Call_ROI', 'Put_ROI']
    df = pd.DataFrame(columns=columns)
    while len(ticker_df)>0:
        symbol = ticker_df.pop()
        print(symbol, len(ticker_df))
        current_date = datetime.strptime("2016-10-05", "%Y-%m-%d")
        end_date = datetime.now()
        x = None

        while current_date<end_date:
            current_date = current_date + timedelta(days=1)
            if current_date.isoweekday() in range(1, 6):
                if x is None:
                    x = stock(symbol, current_date)
                else:
                    x = stock(symbol, current_date, x.exp_dates)
                if hasattr(x, "result"):
                    df = df.append(pd.Series(x.result, index=columns), ignore_index=True)
            #print(df)
            #input()
        #print(df)
        print(df.corr())
        try:
            if len(ticker_df) % 10 == 0:
                df.to_csv('data.csv')

            df['Pressure'] = df['Pressure'].round(decimals=1)
            print(df.columns)
            dfs = df.groupby(['Pressure'])
            for i in dfs:
                print(i)
        except Exception as e:
            print(e)
            pass
