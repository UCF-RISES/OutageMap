import numpy as np
import pandas as pd
import os
from util.mainHelper import weatherImpact

n=2
network = "P3R"
directories = [f"./{network}/Rain/nodes/", f"./{network}/Wind/nodes/"]
fileNames = [f for f in os.listdir(directories[0]) if os.path.isfile(os.path.join(directories[0], f))]

for name in fileNames:
    alpha = {
    # Nodes
    "elevation nodes": [0.8, 0.2],
    "vegetation": [0.7, 0.3]
    }
    rainDf = pd.read_csv(directories[0] + name)
    windDf = pd.read_csv(directories[1] + name)

    rainDf.drop(["Unnamed: 0"], axis=1, inplace=True)
    windDf.drop(["Unnamed: 0"], axis=1, inplace=True)

    maxValuesRain = rainDf.max(axis=1)
    maxValuesWind = windDf.max(axis=1)

    minValuesRain = rainDf.min(axis=1)
    minValuesWind = windDf.min(axis=1)

    weatherVector = np.zeros((2, 767, n))

    weatherVector[0,:] = np.linspace(minValuesWind, maxValuesWind, num=n).T
    weatherVector[1,:] = np.linspace(minValuesRain, maxValuesRain, num=n).T

    wi1 = weatherImpact(alpha, weatherVector[:,:,0])
    wi2 = weatherImpact(alpha, weatherVector[:,:,1])

    wi = {
        "elevation nodes": [],
        "vegetation": []
    }

    for feature in wi:
        for low, high in zip(wi1[feature], wi2[feature]):
            wi[feature].append((low, high))


    events = pd.DataFrame(wi)
    pd.DataFrame.to_csv(events, f'./{network}/WI/nodes/{name}')

# Edges
directories = [f"./{network}/Rain/edges/", f"./{network}/Wind/edges/"]
fileNames = [f for f in os.listdir(directories[0]) if os.path.isfile(os.path.join(directories[0], f))]

for name in fileNames:
    alpha = {
    # Edges
    "elevation edges": [0.8, 0.2],
    "length": [0.7, 0.3], 
    }

    rainDf = pd.read_csv(directories[0] + name)
    windDf = pd.read_csv(directories[1] + name)

    rainDf.drop(["Unnamed: 0.1"], axis=1, inplace=True)
    windDf.drop(["Unnamed: 0.1"], axis=1, inplace=True)
    rainDf.drop(["Unnamed: 0"], axis=1, inplace=True)
    windDf.drop(["Unnamed: 0"], axis=1, inplace=True)

    maxValuesRain = rainDf.max(axis=1)
    maxValuesWind = windDf.max(axis=1)

    minValuesRain = rainDf.min(axis=1)
    minValuesWind = windDf.min(axis=1)

    weatherVector = np.zeros((2, 766, n))

    weatherVector[0,:] = np.linspace(minValuesWind, maxValuesWind, num=n).T
    weatherVector[1,:] = np.linspace(minValuesRain, maxValuesRain, num=n).T

    wi1 = weatherImpact(alpha, weatherVector[:,:,0])
    wi2 = weatherImpact(alpha, weatherVector[:,:,1])

    wi = {
        "elevation edges": [],
        "length": []
    }

    for feature in wi:
        for low, high in zip(wi1[feature], wi2[feature]):
            wi[feature].append((low, high))

    events = pd.DataFrame(wi)
    pd.DataFrame.to_csv(events, f'./{network}/WI/edges/{name}')

