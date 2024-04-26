import pandas as pd
import os

network = "P3R"

directories = [f"../{network}/Rain/nodes/", f"../{network}/Wind/nodes/"]
fileNames = [f for f in os.listdir(directories[0]) if os.path.isfile(os.path.join(directories[0], f))]
nodes = pd.read_csv(f"../{network}/nodeList.csv")
edges = pd.read_csv(f"../{network}/edgeList.csv")

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
