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
    gain_value = 0.2
    stop_value = 0.8

    # days, trades, result, growth = test_intra_day_reversion_with_stop(df, nope_threshold, gain_value, stop_value)
    days, trades, result, growth = test_intra_day_reversion_no_failure(df, nope_threshold, gain_value)
    
    
    display_results(days, trades, result, growth)
    
def test_intra_day_reversion_with_stop(sheet, threshold, gain_value, stop_value, time_too_late = '15:00:00', growth = 1):

    # Setting up return variables
    result = []
    days = 0
    in_play_days = 0
    trades = 0
    
    # Setting up variables for keeping track of time
    prevTime = '00:00:00'
    EOD = True
    curDate = datetime.datetime(2020, 1, 1)
    
    # Setting up reversion variables
    in_play = 0
    entry_spy_price = 0
    new_NOPE_cycle = True
    
    # Iterate through the CSV
    for row in sheet.itertuples() :
    
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
        
        # If it is the end of the day, execute EOD actions
        if (row.time == '16:00:00') :
            days += 1
            EOD = True
            
            # If we are still in_play, we've reached the EOD and reversion has not occurred. Mark failure
            if (in_play != 0) :
                
                # Adjusting growth value for failure
                if(in_play == 1) :
                    growth = growth+(growth*(entry_spy_price-row.active_underlying_price))
                    print("Loss of ", (entry_spy_price-row.active_underlying_price)*100, "%")
                if(in_play == -1):
                    growth = growth+(growth*(row.active_underlying_price-entry_spy_price))
                    print("Loss of ", (row.active_underlying_price-entry_spy_price)*100, "%")
               
                # Marking failure
                result.append(0)
                in_play = 0
            continue
        
        #Check to see if NOPE has reached threshold, if so set in_play. Make sure you're not in a play already
        #Also don't make a new play if close to end of day
        if (abs(row.NOPE_busVolume*100)>=threshold and in_play == 0 and row.time <= time_too_late and new_NOPE_cycle == True) :
            #Set entry price
            entry_spy_price = row.active_underlying_price
            trades += 1
            new_NOPE_cycle=False
            #Set the correct direction)
            if(row.NOPE_busVolume>0) :
                in_play = 1
            else :
                in_play = -1
            continue
            
        #If we are in a reversion        
        if(abs(row.NOPE_busVolume*100)<threshold and new_NOPE_cycle == False) :
            new_NOPE_cycle = True
        
        # Check to see if reversion occurred
        if(in_play != 0) :
            if(in_play == 1 and (entry_spy_price-row.active_underlying_price > gain_value)) :
                result.append(1)
                in_play = 0
                
                # Adjusting growth value for success
                growth = growth+(growth*(entry_spy_price-row.active_underlying_price))
                continue
            if(in_play == -1 and (row.active_underlying_price-entry_spy_price > gain_value)) :
                result.append(1)
                in_play = 0
                
                # Adjusting growth value for success
                growth = growth+(growth*(row.active_underlying_price-entry_spy_price))
                continue
                
        # Check for a stop loss
        if(in_play != 0) :
            if(in_play == 1 and (entry_spy_price-row.active_underlying_price <= -stop_value)) :
                result.append(0)
                in_play = 0
                
                # Adjusting growth value for stop loss
                growth = growth+(growth*(entry_spy_price-row.active_underlying_price))
                print("Loss of ", (entry_spy_price-row.active_underlying_price)*100, "%")
                continue
            if(in_play == -1 and (row.active_underlying_price-entry_spy_price <= -stop_value)) :
                result.append(0)
                in_play = 0
                
                # Adjusting growth value for stop loss
                growth = growth+(growth*(row.active_underlying_price-entry_spy_price))
                print("Loss of ", (row.active_underlying_price-entry_spy_price)*100, "%")
                continue
            
    return days, trades, result, growth

def test_intra_day_reversion_no_failure(sheet, threshold, gain_value, time_too_late = '15:00:00', growth = 1):

    # Setting up return variables
    result = []
    days = 0
    in_play_days = 0
    trades = 0
    
    # Setting up variables for keeping track of time
    prevTime = '00:00:00'
    EOD = True
    curDate = datetime.datetime(2020, 1, 1)
    
    # Setting up reversion variables
    in_play = 0
    entry_spy_price = 0
    new_NOPE_cycle = True
    
    # Iterate through the CSV
    for row in sheet.itertuples() :
    
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
        
        # If it is the end of the day, execute EOD actions
        if (row.time == '16:00:00') :
            days += 1
            EOD = True
            
            # If we are still in_play, we've reached the EOD and reversion has not occurred. Mark failure
            if (in_play != 0) :
                # Marking failure
                result.append(0)
                in_play = 0
            continue
        
        #Check to see if NOPE has reached threshold, if so set in_play. Make sure you're not in a play already
        #Also don't make a new play if close to end of day
        if (abs(row.NOPE_busVolume*100)>=threshold and in_play == 0 and row.time <= time_too_late) :
            #Set entry price
            entry_spy_price = row.active_underlying_price
            trades += 1
            #Set the correct direction)
            if(row.NOPE_busVolume>0) :
                in_play = 1
            else :
                in_play = -1
            continue
        
        # Check to see if reversion occurred
        if(in_play != 0) :
            if(in_play == 1 and (entry_spy_price-row.active_underlying_price > gain_value)) :
                result.append(1)
                in_play = 0
                
                # Adjusting growth value for success
                growth = growth+(growth*(entry_spy_price-row.active_underlying_price))
                continue
            if(in_play == -1 and (row.active_underlying_price-entry_spy_price > gain_value)) :
                result.append(1)
                in_play = 0
                
                # Adjusting growth value for success
                growth = growth+(growth*(row.active_underlying_price-entry_spy_price))
                continue
            
    return days, trades, result, growth

    
def display_results(days, trades, result, growth) :
    print("Days: ",days)
    print("Trades executed: ", trades) 
    sum_of_wins = sum(result)
    
    if(trades != len(result)) :
        print("Total trades does not match up with results")
    
    print("Wins: ", sum_of_wins)
    print("Accuracy Rate: ", round(sum_of_wins/trades*100,2), "%")
    print("Growth value: ", growth)
    return
    
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
