import os
import sys

import requests
import pandas as pd
import numpy as np
import mplfinance as mpf
import pandas_datareader as pdr

from loguru import logger



# set up logger

logger.add("sp500.log", format="{time:HH:mm:ss}\n{level}\n{message}\n")


# set up default values



longest_moving_avarage = 50

deep_of_research = 5 * 365 #output sheet will cover this time (days)

last_research_day = pd.Timestamp.today() #research starts today

#after droping NaN cells of MA, sheet mast be {deep_of_research} cells deep
first_research_day = last_research_day - pd.Timedelta(days = deep_of_research + longest_moving_avarage - 1);

current_script_name = os.path.basename(__file__).replace(".py", "");

file_name = f"{current_script_name}_{last_research_day.strftime('%Y-%m-%d')}.pkl"; 


# main  # this is the main function, must be clean and easy to understand. logging or/and comments after every step

@logger.catch
def core():

    print("") #to create a little bit of space after calling this bot
    logger.info(f"script starts"); #for logs.

    logger.info(f"range of research: {first_research_day} to {last_research_day}");

    #link to csv file of sp500 companies, mb i can save it, or make function to read old csv, if site is unavaleble
    working_list_of_symbols = list(pd.read_csv("https://datahub.io/core/s-and-p-500-companies/r/constituents.csv").set_index("Symbol").sort_index().index);


    list_of_df, undefind_symbols = list_of_df_creater(working_list_of_symbols, last_research_day, first_research_day);


    output_sheet = pd.concat(list_of_df, axis=1, keys = [i.name  for i in list_of_df])
    logger.info(f"new file name: {file_name}");


    pd.to_pickle(output_sheet, file_name);


    if 0 < len(undefind_symbols) < 15:
        logger.warning(f"This symbols are not found: {', '.join(undefind_symbols)}.")
    elif len(undefind_symbols) >= 15:
        logger.warning(f"{len(undefind_symbols)} symbols are not found.")


    log_and_exit(f"all done! {file_name} saved", is_error=False)

# modules


def list_of_df_creater(some_list_of_symbols, last_date, first_date):

    response_df_list = []
    skipped_symbols = []
    some_list_len = len(some_list_of_symbols)


    for i in some_list_of_symbols:
        try:
            symbol = str(i)
            i = pdr.DataReader(i, data_source="yahoo", start=first_date, end=last_date)
            i["MA20"] = i["Close"].rolling(20).mean()
            i["MA50"] = i["Close"].rolling(50).mean()
            i = i.dropna()
            i.name = symbol
            response_df_list.append(i)

            mini_logger(f"Symbol {i.name} added ({some_list_of_symbols.index(i.name) + 1}/{some_list_len})")


        except (IOError, KeyError):
            skipped_symbols.append(i)
            logger.warning(f"symbol {i} error, skipped")

    return response_df_list, skipped_symbols



# mini logger is overwritable, use to show progress stage
def mini_logger(some_string):
    print("  " * len(some_string), end="\r")
    print(some_string, end="\r")



# send ready message to telegram, returns bool of seccess
def log_and_exit(some_message, is_error):

    api_key = os.getenv("tg_api_lazy_bot")

    recipient = os.getenv("chat_ing")

    if is_error == True:
        text_message = f"{script_name} finished with error {some_message}"
        logger.error(some_message)

    if is_error == False:
        text_message = some_message
        logger.success(some_message)

    url = f"https://api.telegram.org/bot{api_key}/sendMessage?chat_id={recipient}&text={text_message}"
    res = requests.get(url).json()

    if res["ok"] == True:
        logger.info("message sent")
    else:
        logger.error("message not sent")

    exit()


""" for next version
def new_one ():

    for i in range(len(ms)):
        if (ms['MA20'].iloc[i] > ms['MA50'].iloc[i]) and (ms['MA20'].iloc[i-1] < ms['MA50'].iloc[i-1]):
            buy_signals.append(ms.iloc[i]['Close'] * 0.98)
        else:
            buy_signals.append(np.nan)
            if (ms['MA20'].iloc[i] < ms['MA50'].iloc[i]) and (ms['MA20'].iloc[i-1] > ms['MA50'].iloc[i-1]):
                sell_signals.append(ms.iloc[i]['Close'] * 1.02)
            else:
                sell_signals.append(np.nan)
"""


#classes


class Naming:
    def __init__(self, obj_name, obj_date):
        self.name = str(obj_name)
        self.pddate = obj_date
        self.strdate = obj_date.strftime('%Y-%m-%d_%H:%M:%S')
        self.filename = f"{str(obj_name)}_{obj_date.strftime('%Y-%m-%d_%H-%M-%S')}.pkl"




#time to start this shit

if __name__ == "__main__":
    core()







""" OLD SHIT

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

def file_checker(some_file) -> bool:

    if os.path.exists(some_file) and os.path.splitext(some_file)[1] in (".pkl", ".csv"):
        return True
    else:
        return False


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
