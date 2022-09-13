import os
import re
import sys

import requests
import pandas as pd
import numpy as np
import mplfinance as mpf
import pandas_datareader as pdr

from loguru import logger
from datetime import date, timedelta


# set up default values

last_trading_day = None


# set up loggin


logger.add("sp500.log", format="{time:HH:mm:ss} | {level} | \n{message}\n")


# main  # this is the main function, must be clean and easy to understand. logging after every step

@logger.catch
def main():

    print("") #to create a little bit of space after calling this bot

    input_file = "tester.pkl" # input("name of file: ")
    if not file_checker(input_file):
        logger.error(f"file {input_file} not recogniced seccefully");

    working_list_of_symbols = symbol_extracter(input_file); #from input file extract column or index that contains symbols
    logger.info(f"list of symbols discovered");

    raw_working_day = get_last_trading_day(working_list_of_symbols); #need to find some better way to discover last working day
    logger.info(f"last working date discovered");

    working_day = Naming(obj_name = "sp500", obj_date = raw_working_day);
    logger.info(f"Date recognised seccessful: {working_day.pddate}");

    output_sheet, undefind_symbols = new_sheet_creater(working_list_of_symbols, working_day);
    logger.info(f"new sheet created");

    new_sheet_name = working_day.filename;
    logger.info(f"new file name: {new_sheet_name}");

    pd.to_pickle(output_sheet, new_sheet_name);
    logger.success(f"sheet saved");

    send_ready_message()

    if 0 < len(undefind_symbols) < 15:
        logger.warning(f"This symbols are not found: {', '.join(undefind_symbols)}.")
    elif len(undefind_symbols) >= 15:
        logger.warning(f"{len(undefind_symbols)} symbols are not found.")

    exit()


# modules

def file_checker(some_file) -> bool:

    if os.path.exists(some_file) and os.path.splitext(some_file)[1] in (".pkl", ".csv"):
        return True
    else:
        return False



def symbol_extracter(some_file):                        #lets make some sheet
    file_extention = os.path.splitext(some_file)[1]

    if file_extention == ".pkl":
        some_sheet = pd.read_pickle(some_file)
    elif file_extention == ".csv":
        some_sheet = pd.read_csv(some_file)
    else:
        logger.error(f"wrong file {some_file} extention")
        exit()

    if some_sheet.index.name == "Symbol":
        list_of_symbols = list(some_sheet.index)
    elif "Symbol" in some_sheet.columns:
        list_of_symbols = list(some_sheet.Symbol)
    else:
        logger.error(f"Symbols column is not defind")
        exit()
    return list_of_symbols



def new_sheet_creater(some_list, some_date):
    list_of_series = []
    skipped_symbols = []
    errors_in_row = 0
    some_list_len = len(some_list)
    for i in some_list:
        try:
            symbol_row = pdr.DataReader(i, data_source="yahoo", start=some_date.pddate, end=some_date.pddate).iloc[0]
            symbol_row.name = i
            list_of_series.append(symbol_row)
            mini_logger(f"Symbol {i} added {some_list.index(i)}/{some_list_len}")
            errors_in_row = 0

        except (IOError, KeyError):
            skipped_symbols.append(i)
            logger.warning(f"symbol {i} error, skipped")

            errors_in_row += 1
            if errors_in_row >= 5:
                logger.error(f"5 symbols skipped, fave to fix")
                exit()

    response_dataframe = pd.DataFrame(data=list_of_series).sort_index()
    return response_dataframe, skipped_symbols



def get_last_trading_day(some_list):
    response_day = None
    date_week_ago = (date.today() - timedelta(7)).strftime("%Y-%m-%d")

    for i in some_list:
        try:
            placeholderdf = pdr.DataReader(i, data_source="yahoo", start=date_week_ago)
            response_day = placeholderdf.index[-1]
            break

        except (IOError, KeyError):
            logger.debug(f"symbol {i} error, skipped")
            continue

    if response_day == None:
        logger.error(f"date of trading undefind")
        exit()

    return response_day



def mini_logger(some_string): #this logger overwrite itself, unlike loguru
    print("  " * len(some_string), end="\r")
    print(some_string, end="\r")



def send_ready_message():

    script_name = os.path.basename(__file__)
    api_key = os.getenv("tg_api_lazy_bot")
    recipient = os.getenv("chat_ing")
    text_message = f"{script_name} has been finished"

    url = f"https://api.telegram.org/bot{api_key}/sendMessage?chat_id={recipient}&text={text_message}"
    res = requests.get(url).json()

    if res["ok"] == True:
        logger.info("ready message is sended")
    else:
        logger.debug("message error")



#classes


class Naming:
    def __init__(self, obj_name, obj_date):
        self.name = str(obj_name)
        self.pddate = obj_date
        self.strdate = obj_date.strftime('%Y-%m-%d_%H:%M:%S')
        self.filename = f"{str(obj_name)}_{obj_date.strftime('%Y-%m-%d_%H-%M-%S')}.pkl"




#time to start this shit

if __name__ == "__main__":
    main()




# old shit
"""
ms = yf.Ticker("MSFT").history(period="max")

print(ms)

#mpf.plot(ms, type="candle", volume = True, style = "mike", mav=(8, 20, 50))

#Start = date.today() - timedelta(365)
#Start.strftime('%Y-%m-%d')

#End = date.today() + timedelta(2)
#End.strftime('%Y-%m-ile)

ms['MA20'] = ms['Close'].rolling(20).mean()
ms['MA50'] = ms['Close'].rolling(50).mean()
ms = ms.dropna()

buy_signals = []
sell_signals = []

for i in range(len(ms)):
    if (ms['MA20'].iloc[i] > ms['MA50'].iloc[i]) and (ms['MA20'].iloc[i-1] < ms['MA50'].iloc[i-1]):
        buy_signals.append(ms.iloc[i]['Close'] * 0.98)
    else:
        buy_signals.append(np.nan)
    if (ms['MA20'].iloc[i] < ms['MA50'].iloc[i]) and (ms['MA20'].iloc[i-1] > ms['MA50'].iloc[i-1]):
        sell_signals.append(ms.iloc[i]['Close'] * 1.02)
    else:
        sell_signals.append(np.nan)

buy_markers = mpf.make_addplot(buy_signals, type='scatter', markersize=120, marker='^')
sell_markers = mpf.make_addplot(sell_signals, type='scatter', markersize=120, marker='v')
ma20 = mpf.make_addplot(ms.MA20, type="line", color="red")
ma50 = mpf.make_addplot(ms.MA50, type="line", color="yellow")

apds = [buy_markers, sell_markers, ma20, ma50]

mpf.plot(ms, type = "candle", style = "binance", addplot = apds)
"""
