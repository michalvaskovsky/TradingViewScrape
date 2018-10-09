'''
    Author: TheLightOne
    Contact: 
        Telegram: vsk inc 
    Scrape Trading view Strategy tester -> List of trades
    Chart strategy -> OCC Strategy R5.1
    IMPORTANT NOTES: Do not move your mouse when browser window is open
    
    Depedencies:
        pywin32
        bs4
        selenium
'''

import time
import win32api, win32con
from bs4 import BeautifulSoup
from timehelper import TimeHelper
from seleniumhelper import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

CHART_URL = "https://www.tradingview.com/chart/ENQi0sGB/" # EOSUSDT Binance

class TradingView:
    def __init__(self, username, password, urltrade):
        self.username = username
        self.password = password
        self.urltrade = urltrade
        self.wait = 60

    # PURPOSE: Obtain latest trades from trades list for the trade chart
    # NOTES:
    #   Trades list is dynamicaly generated table thus it is necessary to scroll it down to the last row in order to read active/last trade
    #   For scrolling down the trades table, nothing of what Selenium ActionChain offers worked. It was necessary to emulate Windows events.
    #   Return table element HTML
    # UPDATE. 30.9.2018:
    #   1. Scrape trading pair close price from the graph view

    def ObtainLastTrades(self):
        try:
            d = InitDriver()
            d.get(self.urltrade)

            # click strategy tester button
            e = WebDriverWait(d, self.wait).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="footer-chart-panel"]/div[2]/span[3]/span')))
            e.click()

            # click list of trades button
            xpath = '//*[@id="bottom-area"]/div[3]/div[1]/div[2]/ul/li[3]'
            ClickWaitByXpath(d, xpath, self.wait)

            # wait for trades table
            xpath = '//*[@id="bottom-area"]/div[3]/div[2]'
            WaitByXpath(d, xpath, self.wait)

            time.sleep(10)

            # move cursor to the table
            loc = (int(e.location["x"]), int(e.location["y"]) + 300)
            win32api.SetCursorPos(loc)

            # scroll down to the last trade
            for i in range(5):
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -9000, 0)
                time.sleep(2)

            time.sleep(2)

            # obtain data
            a = d.find_element_by_xpath('//*[@id="bottom-area"]/div[3]/div[2]/div/div/div')
            data = a.get_attribute('innerHTML')

            # scrape close price
            #x = '//*/span[@class="pane-legend-item-value pane-legend-line pane-legend-item-value__main"]' # upper value at chart
            x = '//*/span[@class="dl-header-price"]' # right panel with actual price
            elems = d.find_elements_by_xpath(x)
            close_price = float(elems[0].text)

            d.close()
            return data, close_price

        except Exception as e:
            d.close()
            print "ObtainLastTrades() - Exception - " + e.message
            return False, 0

    #
    # Trade definition (Tradingview:
    #      0         1         2           3            4           5        6         7          8            9           10
    # trade_id, type_open, signal_open, time_open, price_open, contracts, profit,  type_close, signal_close, time_close, price_close
    def parseTrades(self, data):
#        try:
        if True:
            soup = BeautifulSoup(data, "lxml")
            bodies = soup.find("table").find_all("tbody")

            # read all tds in table sequentaly and store them to array
            tmp = []
            for body in bodies:
                a = body.find_all("td")
                tmp.extend([a[i].text.replace(u'\xa0', ' ') for i in range(len(a))])

            # cut the 7items from a. This will change alignment of trades array.
            # alignment is paired to either: ExitShort-EntryLong / ExitLong-EntryShort
            # tw_trade_id, profit, contracts are just zeroes as those values are useless now
            tmp1 = []
            tmp = tmp[7:]
            while True:
                try:
                    if(len(tmp) < 11):
                        break
                    elif tmp[1] == 'Open':
                        break
                    a = ['0'] + tmp[0:4] + ['0', '0'] + tmp[5:9]
                    tmp1.append(a)
                    tmp = tmp[11:]
                except Exception:
                    break

            # now sort trades by open_time, ascending
            th = TimeHelper()
            return th.sortArrayByDateEx(tmp1, 3)

#        except Exception as e:
#            print(e.message)
#            return None

def twmain():
    tw_url = CHART_URL

    print "Scraping trades for url=%s" % tw_url

    tr = TradingView("", "", tw_url)
    data, actual_price = tr.ObtainLastTrades()
    if not data:
        print "Error -> Data is None"
        return

    trades = tr.parseTrades(data)
    if not trades:
        print "Error -> Trades is None"
        return

    print "Actual price: %s" % actual_price
    for trade in trades:
        print "Trade \n\ttype=%s\n\tprice=%s\n\ttimeopen=%s" % (trade[7], trade[4], trade[3])

twmain()

#
#   TEST MODULES
#
#
#
import unittest
import codecs

class TestTradingviewClass(unittest.TestCase):

    def test_PrintLastTrades(self):
        tr = TradingView("", "", CHART_URL)
        data, actual_price = tr.ObtainLastTrades()
        assert data
        trades = tr.parseTrades(data)
        assert trades

        print "Actual price: %s" % actual_price
        for trade in trades:
            print "Trade \n\ttype=%s\n\tprice=%s\n\ttimeopen=%s" % (trade[7], trade[4], trade[3])

    # scrape data and dump it to the file
    def test_TwScrape1(self):

        tr = TradingView("", "", CHART_URL)
        data, actual_price  = tr.ObtainLastTrades()
        assert data
        with codecs.open("trading_table.txt", "w", "utf-8") as f:
            f.write(data)



