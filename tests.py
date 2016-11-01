#
import pytest
from stock import stock
import os
from datetime import datetime

class TestClass:
    def test_get_exp_date(self):
        # test accuracy of months returned from db
        stock_obj = stock('SVU', datetime.strptime('2016-10-12', '%Y-%m-%d'))

        for month in ['November2016', 'October2016']:
            month_check = stock_obj.exp_dates['Expiration_Date'].str.contains(month).any()
            assert month_check == True

        # test expiraiton within current month
        stock_obj = stock('SVU', datetime.strptime('2016-10-07', '%Y-%m-%d'))
        assert stock_obj.expiration == 'November2016'

        # test expiration next month
        stock_obj = stock('SVU', datetime.strptime('2016-10-19', '%Y-%m-%d'))
        assert stock_obj.expiration == 'October2016'
