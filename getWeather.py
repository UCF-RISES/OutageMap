from util.NetworkFunctions import getWeatherByCoords, roundup, parseDate, parseTime
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
weatherEvents = pd.read_excel("32123.xlsx")

###############################################################
            # NODE WEATHER DATA COLLECTION LOOP
###############################################################

# Loop through weather events
for j in weatherEvents.index:
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
        eventForNode1.append(tempWind * 2.23694)

    # Convert Lists to dataframe
    events = pd.DataFrame(eventForNode)
    events1 = pd.DataFrame(eventForNode1)

    # Save Dataframes to csv's
    pd.DataFrame.to_csv(events, f'./{network}/Rain/nodes/weatherEvent{j+1}.csv')
    pd.DataFrame.to_csv(events1, f'./{network}/Wind/nodes/weatherEvent{j+1}.csv')

###############################################################
            # EDGE WEATHER DATA COLLECTION LOOP
###############################################################

# Set the directories of the node weather data
directories = [f"./{network}/Rain/nodes/", f"./{network}/Wind/nodes/"]

# Grab the names of files in folder
fileNames = [f for f in os.listdir(directories[0]) if os.path.isfile(os.path.join(directories[0], f))]

# Create am edge list from loaded edge csv
edgeList = []
for i in range(len(edges)):
    edgeList.append([int(edges.iloc[[i]]["source"]), int(edges.iloc[[i]]["target"])])

# Loop through each file in folder
for name in fileNames:
    # Load the rain data
    rainDf = pd.read_csv(directories[0] + name)
    rainDf.drop(["Unnamed: 0"], axis=1, inplace=True)

    # Load the wind data
    windDf = pd.read_csv(directories[1] + name)

    # Create dataframes for edges wind and rain
    edgeWindDf = pd.DataFrame(columns=rainDf.columns)
    edgeRainDf = pd.DataFrame(columns=windDf.columns)

    # Loop through each edge
    for source, target in edgeList:
        # Calculate the edge rain and wind data by averaging between the connected nodes
        edgeRain = pd.DataFrame(rainDf.iloc[[source]].values + rainDf.iloc[[target]].values, columns=rainDf.columns) / 2
        edgeWind = pd.DataFrame(windDf.iloc[[source]].values + windDf.iloc[[target]].values, columns=windDf.columns) / 2

        # Append the wind and rain data to their respective csv
        edgeWindDf = pd.concat([edgeWindDf, edgeWind], ignore_index=True)
        edgeRainDf = pd.concat([edgeRainDf, edgeRain], ignore_index=True)

    # Rename the dataframe
    edgeRain = pd.DataFrame(edgeRainDf)
    edgeWind = pd.DataFrame(edgeWindDf)

    # Save each dataframe in their own csv file
    pd.DataFrame.to_csv(edgeRain, f'./{network}/Rain/edges/{name}')
    pd.DataFrame.to_csv(edgeWind, f'./{network}/Wind/edges/{name}')
