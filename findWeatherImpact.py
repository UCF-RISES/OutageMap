import numpy as np
import pandas as pd
import os
from util.mainHelper import weatherImpact,createLevelsAlt,findWeatherLevel

n=2  # Number of weather scenarios to simulate
network = "P3R"  # Network identifier
directories = [f"./{network}/Rain/nodes/", f"./{network}/Wind/nodes/"]  # Directories containing data
fileNames = [f for f in os.listdir(directories[0]) if os.path.isfile(os.path.join(directories[0], f))]  # List of filenames in the first directory

# Normalization Levels for Weather Data
windSeverityLevels = createLevelsAlt(0,120,10)
rainSeverityLevels = createLevelsAlt(0,6,10)

# Process files for nodes
for name in fileNames:
    alpha = {
        "elevation nodes": [0.75, 0.25],
        "vegetation": [0.6, 0.4]
    }
    rainDf = pd.read_csv(directories[0] + name)  # Load rain data
    windDf = pd.read_csv(directories[1] + name)  # Load wind data

    rainDf.drop(["Unnamed: 0"], axis=1, inplace=True)  # Remove extra index column if present in rain data
    windDf.drop(["Unnamed: 0"], axis=1, inplace=True)  # Remove extra index column if present in wind data

    # Calculate max and min values for rain and wind datasets
    maxValuesRain = np.array(rainDf.max(axis=1))
    maxValuesWind = np.array(windDf.max(axis=1))
    minValuesRain = np.array(rainDf.min(axis=1))
    minValuesWind = np.array(windDf.min(axis=1))
    
    # Initialize arrays to store scores and vectors in
    weatherVector = np.zeros((2, 767, n))
    score_wind = np.zeros((2, 767))
    score_rain = np.zeros((2, 767))

    # Loop through each node to find the normalized weather value
    for i in range(767):
        score_wind[0,i] = findWeatherLevel(minValuesWind[i],windSeverityLevels)
        score_wind[1,i] = findWeatherLevel(maxValuesWind[i],windSeverityLevels)

        score_rain[0,i] = findWeatherLevel(minValuesRain[i],rainSeverityLevels)
        score_rain[1,i] = findWeatherLevel(maxValuesRain[i],rainSeverityLevels)

    # Create the normalized weather vector
    weatherVector[0,:] = np.linspace(score_wind[0,:], score_wind[1,:], num=n).T
    weatherVector[1,:] = np.linspace(score_rain[0,:], score_rain[1,:], num=n).T
    
    # Compute weather impact for both interpolated points
    wi1 = weatherImpact(alpha, weatherVector[:,:,0])
    wi2 = weatherImpact(alpha, weatherVector[:,:,1])

    # Create dictionary to hold final weather impact ranges
    wi = {
        "elevation nodes": [],
        "vegetation": []
    }

    # Combine data for low and high scenarios
    for feature in wi:
        for low, high in zip(wi1[feature], wi2[feature]):
            wi[feature].append(((np.round(low,3), np.round(high,3))))

    # Create DataFrame and save to CSV
    events = pd.DataFrame(wi)
    pd.DataFrame.to_csv(events, f'./{network}/WI/nodes/{name}')

# Process files for edges (similar steps as nodes)
directories = [f"./{network}/Rain/edges/", f"./{network}/Wind/edges/"]
fileNames = [f for f in os.listdir(directories[0]) if os.path.isfile(os.path.join(directories[0], f))]

# Process files for edges
for name in fileNames:
    alpha = {
        "elevation edges": [0.72, 0.28],
        "length": [0.88, 0.12], 
    }

    rainDf = pd.read_csv(directories[0] + name)
    windDf = pd.read_csv(directories[1] + name)

    # Removing both types of unnamed columns that might have been erroneously created
    rainDf.drop(["Unnamed: 0.1", "Unnamed: 0"], axis=1, inplace=True)
    windDf.drop(["Unnamed: 0.1", "Unnamed: 0"], axis=1, inplace=True)
    
    # Calculate max and min values for rain and wind datasets
    maxValuesRain = rainDf.max(axis=1)
    maxValuesWind = windDf.max(axis=1)
    minValuesRain = rainDf.min(axis=1)
    minValuesWind = windDf.min(axis=1)
    
    # Initialize arrays to store scores and vectors in
    weatherVector = np.zeros((2, 766, n))
    score_wind = np.zeros((2, 766))
    score_rain = np.zeros((2, 766))

    # Loop through each edge to find the normalized weather value
    for i in range(766):
        score_wind[0,i] = findWeatherLevel(minValuesWind[i],windSeverityLevels)
        score_wind[1,i] = findWeatherLevel(maxValuesWind[i],windSeverityLevels)

        score_rain[0,i] = findWeatherLevel(minValuesRain[i],rainSeverityLevels)
        score_rain[1,i] = findWeatherLevel(maxValuesRain[i],rainSeverityLevels)

    # Create the normalized weather vector
    weatherVector[0,:] = np.linspace(score_wind[0,:], score_wind[1,:], num=n).T
    weatherVector[1,:] = np.linspace(score_rain[0,:], score_rain[1,:], num=n).T
    
    # Compute weather impact for both interpolated points
    wi1 = weatherImpact(alpha, weatherVector[:,:,0])
    wi2 = weatherImpact(alpha, weatherVector[:,:,1])

    # Create dictionary to hold final weather impact ranges
    wi = {
        "elevation edges": [],
        "length": []
    }

    # Combine data for low and high scenarios
    for feature in wi:
        for low, high in zip(wi1[feature], wi2[feature]):
            wi[feature].append((np.round(low,3), np.round(high,3)))

    # Create DataFrame and save to CSV
    events = pd.DataFrame(wi)
    pd.DataFrame.to_csv(events, f'./{network}/WI/edges/{name}')
