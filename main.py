import os
import re

import pandas as pd
import numpy as np
import mplfinance as mpf
import pandas_datareader as pdr

from loguru import logger
from datetime import date, timedelta



# set up default values

last_trading_day = None



# set up logging

logger.add("logs.log", format="{time}\n\n{level}\n\n{message}\n\n", level="DEBUG", serialize=True)


# main

# thats the main function, must be clean and easy to understand. logging after every step


@logger.catch
def main():

    print("") #to create a little bit of space after calling this bot

    input_name = "sp500.pkl" # input("name of file: ")
    if not os.path.exists(input_name):
        logger.error(f"\nfile {input_name} doesnt exists\n")
        exit()
    logger.info(f"\nfile {input_name} found\n");

    working_file = Naming(input_name, obj_type="file");
    logger.info(f"\nfile name parsed seccessful\n");

    working_list_of_symbols = symbol_extracter(working_file); #from input file extract column or index that contains symbols
    logger.info(f"\nlist of symbols discovered\n");

    raw_working_day = get_last_trading_day(working_list_of_symbols); #need to find other way to discover last working day
    logger.info(f"\nlast working date discovered\n");

    working_day = Naming(raw_working_day, obj_type="date");
    logger.info(f"\ndate recognised seccessful: {working_day.printdate}\n");

    output_sheet, undefind_symbols = new_sheet_creater(working_list_of_symbols, working_day);
    logger.info(f"\nnew sheet created\n");

    new_sheet_name = f"{working_file.filename}_{working_day.filedate}.pkl";
    logger.info(f"\nnew file name: {new_sheet_name}\n");

    pd.to_pickle(output_sheet, new_sheet_name);
    logger.info(f"\nsheet saved\n");

    if 0 < len(undefind_symbols) < 15:
        logger.warning(f"\nThis symbols are not found: {', '.join(undefind_symbols)}.\n")
    elif len(undefind_symbols) >= 15:
        logger.warning(f"\n{len(undefind_symbols)} are not found.\n")

    exit()


# modules
def symbol_extracter(some_file):                        #lets make some sheet

    if some_file.ext == ".pkl":
        some_sheet = pd.read_pickle(some_file.fullname)
    elif some_file.ext == ".csv":
        some_sheet = pd.read_csv(some_file.fullname)
    else:
        logger.error(f"\nwrong file {some_file.fullname} extention\n")
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
            logger.warning(f"\nsymbol {i} error, skipped\n")

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
            logger.debug(f"\nsimbol {i} error, skipped\n")
            continue

    if response_day == None:
        logger.error(f"Date of trading undefind")
        exit()

    return response_day




def mini_logger(some_string): #this logger overwrite itself, unlike loguru
    print("  " * len(some_string), end="\r")
    print(some_string, end="\r")



#classes


class Naming:
    def __init__(self, obj_name, obj_type):
        if obj_type == "date":
            self.filedate = Naming.date_naming(obj_name)
            self.printdate = str(obj_name)
            self.pddate = obj_name

        elif obj_type == "file":
            self.fullname = os.path.basename(obj_name)
            self.filename = os.path.splitext(self.fullname)[0]
            self.ext = os.path.splitext(obj_name)[1]
            self.path = os.path.abspath(obj_name)

        else:
            logger.error("class Naming got wrong input")
            exit()

    def date_naming(pd_date_type):
        if re.fullmatch(r"^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d$", str(pd_date_type)):
            formated_date = str(pd_date_type).replace(" ", "_").replace(":", "-")
            return formated_date

        else:
            logger.error(f"\n{pd_date_type} not matches to regex\n")
            exit()




if __name__ == "__main__":
    main()


"""


class Date_naming:
    def __init__(self, pd_date):
        self.reqname = pd_date
        self.tofilename = Date_naming.date_formating(pd_date)





# old shit

ms = yf.Ticker("MSFT").history(period="max")

print(ms)

#mpf.plot(ms, type="candle", volume = True, style = "mike", mav=(8, 20, 50))

#Start = date.today() - timedelta(365)
#Start.strftime('%Y-%m-%d')

#End = date.today() + timedelta(2)
#End.strftime('%Y-%m-%d')

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
