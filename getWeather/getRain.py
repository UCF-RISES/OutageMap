from NetworkFunctions import getWeatherByCoords
import pandas as pd
import numpy as np
from datetime import datetime
import math

def roundup(x):
    return int(math.ceil(x / 100.0)) * 100

def parseDate(date):
    datetime_obj = datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')

    date_str = datetime_obj.strftime('%Y-%m-%d')

    return date_str

def parseTime(time):
    time = str(time)
    if len(time) != 4:
        time = ("0" * (4 - len(time))) + time
    return time

nodes = pd.read_csv("../P3R/nodeList.csv")
edges = pd.read_csv("../P3R/edgeList.csv")
weatherEvents = pd.read_excel("../ExtremeWeatherEventsSFO.xlsx")

for j in weatherEvents.index:
    print(f"{j}th event")
    print(roundup(weatherEvents['BEGIN_TIME'][j]))
    begin = f"{parseDate(weatherEvents['BEGIN_DATE'][j])} {parseTime(roundup(weatherEvents['BEGIN_TIME'][j]))}"
    end = f"{parseDate(weatherEvents['END_DATE'][j])} {parseTime(roundup(weatherEvents['END_TIME'][j]))}"

    eventForNode = []

    for i in nodes.index:
        print(f"{i}th node for {j}th event")
        long, lat = eval(nodes["coords"][i])
        print(long)
        print(lat)
        print(begin)
        print(end)
        try:
            timeframe = getWeatherByCoords(long, lat, begin, end)
        except:
            timeframe = getWeatherByCoords(long, lat, begin, end)
        eventForNode.append(timeframe["prcp"])

    events = pd.DataFrame(eventForNode)
    pd.DataFrame.to_csv(events, f'../P3R/Rain/nodes/weatherEvent{j+1}.csv')

