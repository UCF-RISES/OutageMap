import numpy as np
import pandas as pd
import os
from util.mainHelper import weatherImpact

n=2  # Number of weather scenarios to simulate
network = "P3R"  # Network identifier
directories = [f"./{network}/Rain/nodes/", f"./{network}/Wind/nodes/"]  # Directories containing data
fileNames = [f for f in os.listdir(directories[0]) if os.path.isfile(os.path.join(directories[0], f))]  # List of filenames in the first directory

# Process files for nodes
for name in fileNames:
    alpha = {
        "elevation nodes": [0.8, 0.2],
        "vegetation": [0.7, 0.3]
    }
    rainDf = pd.read_csv(directories[0] + name)  # Load rain data
    windDf = pd.read_csv(directories[1] + name)  # Load wind data

    rainDf.drop(["Unnamed: 0"], axis=1, inplace=True)  # Remove extra index column if present in rain data
    windDf.drop(["Unnamed: 0"], axis=1, inplace=True)  # Remove extra index column if present in wind data

    # Calculate max and min values for rain and wind datasets
    maxValuesRain = rainDf.max(axis=1)
    maxValuesWind = windDf.max(axis=1)
    minValuesRain = rainDf.min(axis=1)
    minValuesWind = windDf.min(axis=1)

    weatherVector = np.zeros((2, 767, n))
    weatherVector[0,:] = np.linspace(minValuesWind, maxValuesWind, num=n).T
    weatherVector[1,:] = np.linspace(minValuesRain, maxValuesRain, num=n).T

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
            wi[feature].append((low, high))

    # Create DataFrame and save to CSV
    events = pd.DataFrame(wi)
    pd.DataFrame.to_csv(events, f'./{network}/WI/nodes/{name}')

# Process files for edges (similar steps as nodes)
directories = [f"./{network}/Rain/edges/", f"./{network}/Wind/edges/"]
fileNames = [f for f in os.listdir(directories[0]) if os.path.isfile(os.path.join(directories[0], f))]

for name in fileNames:
    alpha = {
        "elevation edges": [0.8, 0.2],
        "length": [0.7, 0.3], 
    }

    rainDf = pd.read_csv(directories[0] + name)
    windDf = pd.read_csv(directories[1] + name)

    # Removing both types of unnamed columns that might have been erroneously created
    rainDf.drop(["Unnamed: 0.1", "Unnamed: 0"], axis=1, inplace=True)
    windDf.drop(["Unnamed: 0.1", "Unnamed: 0"], axis=1, inplace=True)

    maxValuesRain = rainDf.max(axis=1)
    maxValuesWind = windDf.max(axis=1)
    minValuesRain = rainDf.min(axis=1)
    minValuesWind = windDf.min(axis=1)

    weatherVector = np.zeros((2, 766, n))
    weatherVector[0,:] = np.linspace(minValuesWind, maxValuesWind, num=n).T
    weatherVector[1,:] = np.linspace(minValuesRain, maxValuesRain, num=n).T

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
            wi[feature].append((low, high))

    # Create DataFrame and save to CSV
    events = pd.DataFrame(wi)
    pd.DataFrame.to_csv(events, f'./{network}/WI/edges/{name}')
