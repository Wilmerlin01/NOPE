import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
import statsmodels.tsa.stattools as ts
import datetime

def main() :

    # get dataframe from CSV
    df = scrapeCSV()

    nope_threshold = 50
    change_value = 0.1

    days, in_play_days, result = test_days_EOD_reversal(df, nope_threshold, change_value)
    print("Days: ",days)
    print("In play days: ", in_play_days) 
    sum_of_wins = sum(result)
    
    print("Wins: ", sum_of_wins)
    print("Accuracy Rate: ", round(sum_of_wins/in_play_days*100,2), "%")
    
# NOTE: lines 45, 51-52 should be commented out if you're checking for only positive NOPE plays
def test_days_EOD_reversal(sheet, threshold, change, time_for_reversion = '10:30:00'):

    # Setting up initial variables
    result = []
    days = 0
    in_play_days = 0
    
    prevTime = '00:00:00'
    EOD = True
    in_play = 0
    prev_spy_price = 0
    curDate = datetime.datetime(2020, 1, 1)
     
    for row in sheet.itertuples() :
            
        # If it is the end of the day, move on to next row
        if (row.time == '16:00:00') :
            days += 1
            EOD = True
            if(abs(row.NOPE_busVolume*100)>=threshold) :
            # if (row.NOPE_busVolume*100 >= threshold) :
                # Store in_play = 1 if positive, -1 if negative
                in_play_days += 1
                if(row.NOPE_busVolume>0) :
                    in_play = 1
                else :
                    in_play = -1
                prev_spy_price = row.active_underlying_price
            else : in_play = 0
            continue
        
        # If the time is out of our zone, move on to next row
        if (row.time > '16:00:00') :
            continue
            
        # If it is the new day, set curDate and flip EOD
        if (EOD) :
            curDate = row.date
            EOD = False
            prevTime = '00:00:00'    
    
        # If the date is wrong or time is not consecutive, throw exception
        if (row.date!=curDate or prevTime>row.time):
            throwException()
        
        # If in play and timeframe, check for reversion
        if (in_play != 0 and (row.time <= time_for_reversion)) :
        
            # If gains are made, store win and no longer in play
            if (in_play == 1 and (prev_spy_price-row.active_underlying_price)> change) :
                result.append(1)
                in_play = 0
                continue
            # This should never run if you are checking for only positive NOPE plays
            if (in_play == -1 and (row.active_underlying_price-prev_spy_price)> change) :
                result.append(1)
                in_play = 0
                continue
            if (row.time == time_for_reversion and in_play !=0) :
                result.append(0)
                in_play = 0
                continue
            
    return days, in_play_days, result
    
def throwException() :
    print("Your CSV has jumping times!")
    exit()

def scrapeCSV() :
    # Reading in files
    DATA_PATH = '../processed_data/'

    all_data = pd.read_csv(DATA_PATH + 'allDataCombined.csv')
    price_data = pd.read_csv(DATA_PATH + 'priceData.csv')
    df = pd.merge(all_data, price_data, on="timestamp")

    # Parsing in files
    df['date'] = df['timestamp'].apply(lambda x: parser.parse(x).date())
    df['time'] = df['timestamp'].apply(lambda x: parser.parse(x).strftime("%H:%M:%S"))
    
    return df

main()
