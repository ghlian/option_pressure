from stock import stock
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
if __name__ == "__main__":
    x = stock('SVU', datetime.strptime('2016-10-14', '%Y-%m-%d'))
    print(x.result)
    x = stock('SVU', datetime.strptime('2016-10-17', '%Y-%m-%d'))
    print(x.result)
