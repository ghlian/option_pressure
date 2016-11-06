from stock import stock
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    ticker_df = pd.read_csv('tickers.csv').values.T.tolist()[0]


    columns = ['Symbol', 'Date', 'Pressure', 'Call_Open_Int', 'Put_Open_Int', 'Call_ROI', 'Put_ROI']
    df = pd.DataFrame(columns=columns)
    while len(ticker_df)>0:
        symbol = ticker_df.pop()
        #print(symbol, len(ticker_df))
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

        try:
            if len(ticker_df) % 10 != 0:
                continue

            print(len(df), df.corr())
            df.to_csv('data_open_int.csv')
            
            rounded_df = df
            rounded_df['Pressure'] = rounded_df['Pressure'].round(decimals=1)
            rounded_df_put = rounded_df[['Pressure', 'Put_ROI']]
            rounded_df_call = rounded_df[['Pressure', 'Call_ROI']]

            rounded_df_put.to_csv('rounded_df_put.csv')
            rounded_df_call.to_csv('rounded_df_call.csv')

            try:
                plt.figure()
                rounded_df_put.boxplot(by='Pressure')
                plt.savefig('plot_put.png')
                plt.clf()
                plt.close()


                plt.figure()
                rounded_df_call.boxplot(by='Pressure')
                plt.savefig('plot_call.png')
                plt.clf()
                plt.close()
            except Excetion as e:
                print(e)


            dfs = rounded_df.groupby(['Pressure'])
            """
            print('--------')
            for i in dfs:
                if len(i[1])>5:
                    print(round(float(i[0]),1), len(i[1]), i[1]['Call_ROI'].mean(), i[1]['Put_ROI'].mean())
            print('--------')
            """

        except Exception as e:
            print(e)
            pass
