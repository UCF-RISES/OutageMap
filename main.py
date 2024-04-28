from util.mainHelper import assign_values_to_ranges, createTables, generateProb, probOfNodeAndParent, plotTreeWithProb
import pandas as pd
import numpy as np
from collections import defaultdict
import networkx as nx

nodeFeatures = ["elevation nodes", "vegetation"]
edgeFeatures = ["elevation edges", "length"]

numOfBins=10
network = "P3R"

# For outage
# If decreasng the left number make outage map more severe, increase the right number
meanWI = { 
    "elevation nodes": [20, 1],
    "vegetation": [20, 5],
    "elevation edges": [30,1],
    "length": [20, 5], 
}

# For outage
stdWI = {
    "elevation nodes": [1, 1],
    "vegetation": [1.5, 1.8],
    "elevation edges": [3, 3],
    "length": [4,4], 
}

forecastedRange = {}

nodes = pd.read_csv(f"./{network}/nodeList.csv")
edges = pd.read_csv(f"./{network}/edgeList.csv")
forecastedFactors = [["length", edges], ["elevation edges", edges], ["elevation nodes", nodes], ["vegetation", nodes]]

for name, component in forecastedFactors:
    names = name.split()
    vals =np.round(component[names[0]].values,1)
    bins = assign_values_to_ranges(vals,num_bins=numOfBins)
    levels = []
    total = np.array([])
    for index, [ranges, count] in enumerate(bins):
        total = np.concatenate((total, (index + 1) * np.ones((1, count))), axis=1) if len(total) > 0 else (index + 1) * np.ones((1, count))
        levels.append(list(ranges))

    forecastedRange[name] = levels

meanRange, stdRange = createTables(numOfBins + 1, stdWI, meanWI)
weatherImpactEdges = pd.read_csv(f"./{network}/WI/edges/weatherEvent30.csv")
weatherImpactNodes = pd.read_csv(f"./{network}/WI/nodes/weatherEvent30.csv")

edgeList = []
graph = defaultdict(list)
for i in range(len(edges)):
    edgeList.append((int(edges.iloc[[i]]["source"]), int(edges.iloc[[i]]["target"])))
    graph[int(edges.iloc[[i]]["source"])].append([int(edges.iloc[[i]]["target"]), i])

G = nx.DiGraph()
G.add_nodes_from(range(len(nodes)))
G.add_edges_from(sorted(edgeList))
probNodes = []
for i in range(0, len(nodes)):
    currWeatherImpactN = weatherImpactNodes.iloc[[i]]
    currProb = []

    for j in range(2):
        bounds = {}
        for feature in nodeFeatures:
            bounds[feature] = eval(currWeatherImpactN[feature][i])[j]
        currProb.append(generateProb(nodes.iloc[[i]], None, nodeFeatures, edgeFeatures, meanRange, stdRange, forecastedRange, bounds, None, numOfBins))
    
    probNodes.append(currProb)

probEdges = []
for i in range(0, len(edges)):
    currWeatherImpactE = weatherImpactEdges.iloc[[i]]
    currProb = []

    for j in range(2):
        bounds = {}
        for feature in edgeFeatures:
            bounds[feature] = eval(currWeatherImpactE[feature][i])[j]
        currProb.append(generateProb(None, edges.iloc[[i]], nodeFeatures, edgeFeatures, meanRange, stdRange, forecastedRange, None, bounds, numOfBins))
    
    probEdges.append(currProb)

prob = probOfNodeAndParent(probNodes, probEdges, graph)

meanProb = [(low + high) / 2 for low, high in prob]

pos = {i: eval(nodes.iloc[[i]]["coords"][i]) for i in range(len(nodes))}

plotTreeWithProb(G, meanProb, f"Mean of Outage Probability Range Map for {network}", pos)
