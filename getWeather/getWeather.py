from NetworkFunctions import getWeatherByCoords, roundup, parseDate, parseTime
import pandas as pd
import numpy as np
import os

###############################################################
            # NETWORK AND WEATHER PARAMETERS
###############################################################

# Folder name corresponding to network data
network = 'P3R'

# Importing Nodes and Edges of Network
nodes = pd.read_csv(f"{network}/nodeList.csv")
edges = pd.read_csv(f"{network}/edgeList.csv")

# Weather Event to collect data for
weatherEvents = pd.read_excel("ExtremeWeatherEventsSFO.xlsx")

###############################################################
            # NODE WEATHER DATA COLLECTION LOOP
###############################################################

# Loop through weather events
for j in weatherEvents.index:
    print(f"{j}th event")
    print(roundup(weatherEvents['BEGIN_TIME'][j]))

    # Determine start and end date of event    
    begin = f"{parseDate(weatherEvents['BEGIN_DATE'][j])} {parseTime(roundup(weatherEvents['BEGIN_TIME'][j]))}"
    end = f"{parseDate(weatherEvents['END_DATE'][j])} {parseTime(roundup(weatherEvents['END_TIME'][j]))}"

    # Initialize Node Event Lists
    eventForNode = []
    eventForNode1 = []

    # Loop through each node
    for i in nodes.index:
        print(f"{i}th node for {j}th event")
        
        # Grab node coordinates
        long, lat = eval(nodes["coords"][i])
        
        # Query NLDAS2 for Weather Data
        try:
            timeframe = getWeatherByCoords(long, lat, begin, end)
        except:
            timeframe = getWeatherByCoords(long, lat, begin, end)
        
        # Convert uv wind components to wind speed
        tempWind = np.sqrt(np.square(timeframe["wind_u"]) + np.square(timeframe["wind_v"]))    
        
        # Append the rain to node event lists
        eventForNode.append(timeframe["prcp"])
        
        # Append the wind to node event lists
        eventForNode1.append(tempWind)

    # Convert Lists to dataframe
    events = pd.DataFrame(eventForNode)
    events1 = pd.DataFrame(eventForNode1)

    # Save Dataframes to csv's
    pd.DataFrame.to_csv(events, f'../P3R/Rain/nodes/weatherEvent{j+2}.csv')
    pd.DataFrame.to_csv(events1, f'../P3R/Wind/nodes/weatherEvent{j+2}.csv')


###############################################################
            # EDGE WEATHER DATA COLLECTION LOOP
###############################################################
# COLIN: PLEASE UPDATE THE REST OF THE SCRIPT ACCORDINGLY

directories = [f"../{network}/Rain/nodes/", f"../{network}/Wind/nodes/"]
fileNames = [f for f in os.listdir(directories[0]) if os.path.isfile(os.path.join(directories[0], f))]

edgeList = []
for i in range(len(edges)):
    edgeList.append([int(edges.iloc[[i]]["source"]), int(edges.iloc[[i]]["target"])])

for name in fileNames:
    rainDf = pd.read_csv(directories[0] + name)
    windDf = pd.read_csv(directories[1] + name)
    rainDf.drop(["Unnamed: 0"], axis=1, inplace=True)

    edgeWindDf = pd.DataFrame(columns=rainDf.columns)
    edgeRainDf = pd.DataFrame(columns=windDf.columns)
    for source, target in edgeList:
        edgeRain = pd.DataFrame(rainDf.iloc[[source]].values + rainDf.iloc[[target]].values, columns=rainDf.columns) / 2
        edgeWind = pd.DataFrame(windDf.iloc[[source]].values + windDf.iloc[[target]].values, columns=windDf.columns) / 2

        edgeWindDf = pd.concat([edgeWindDf, edgeWind], ignore_index=True)
        edgeRainDf = pd.concat([edgeRainDf, edgeRain], ignore_index=True)

    edgeRain = pd.DataFrame(edgeRainDf)
    edgeWind = pd.DataFrame(edgeWindDf)

    pd.DataFrame.to_csv(edgeRain, f'../{network}/Rain/edges/{name}')
    pd.DataFrame.to_csv(edgeWind, f'../{network}/Wind/edges/{name}')
