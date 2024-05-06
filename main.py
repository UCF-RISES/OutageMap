from util.mainHelper import assign_values_to_ranges, createTables, generateProb, probOfNodeAndParent, plotTreeWithProb
import pandas as pd
import numpy as np
from collections import defaultdict
import networkx as nx

# Feature descriptions and network identifier
nodeFeatures = ["elevation nodes", "vegetation"]
edgeFeatures = ["elevation edges", "length"]
numOfBins=10
network = "P3R"


# Mean and standard deviation of weather impacts (WI) for outage probability
meanWI = { 
    "elevation nodes": [0.6/2, 0.25/2],
    "vegetation": [0.75/2, 0.35/2],
    "elevation edges": [0.7/2, 0.31/2],
    "length": [0.8/2, 0.32/2], 
}

stdWI = {
    "elevation nodes": [0.1, 0.05],
    "vegetation": [0.1, 0.05],
    "elevation edges": [0.1, 0.05],
    "length": [0.1, 0.05], 
}
# Initialize forecasted range dictionary
forecastedRange = {}

# Load node and edge data from CSV files
nodes = pd.read_csv(f"./{network}/nodeList.csv")
edges = pd.read_csv(f"./{network}/edgeList.csv")

forecastedFactors = [["length", edges], ["elevation edges", edges], ["elevation nodes", nodes], ["vegetation", nodes]]

# Prepare graph structure
edgeList = []
graph = defaultdict(list)
for i in range(len(edges)):
    edgeList.append((int(edges.iloc[[i]]["source"]), int(edges.iloc[[i]]["target"])))
    graph[int(edges.iloc[[i]]["source"])].append([int(edges.iloc[[i]]["target"]), i])

# Initialize directed graph and add nodes and edges
G = nx.DiGraph()
G.add_nodes_from(range(len(nodes)))
G.add_edges_from(sorted(edgeList))

# Process each forecasted factor to determine the forecasted ranges
for name, component in forecastedFactors:
    names = name.split()
    vals = np.round(component[names[0]].values,1)
    bins = assign_values_to_ranges(vals, numOfBins)
    levels = []
    total = np.array([])
    for index, [ranges, count] in enumerate(bins):
        total = np.concatenate((total, (index + 1) * np.ones((1, count))), axis=1) if len(total) > 0 else (index + 1) * np.ones((1, count))
        levels.append(list(ranges))
    forecastedRange[name] = levels

# Create tables for mean and standard deviation ranges
meanRange, stdRange = createTables(stdWI, meanWI, numOfBins + 1)

# Load weather impact data for nodes and edges
weatherImpactEdges = pd.read_csv(f"./{network}/WI/edges/weatherEvent1.csv")
weatherImpactNodes = pd.read_csv(f"./{network}/WI/nodes/weatherEvent1.csv")

# Calculate probabilities for nodes based on weather impact
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

# Calculate probabilities for edges based on weather impact
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

# Calculate combined probabilities for nodes and their parent nodes
prob = probOfNodeAndParent(probNodes, probEdges, graph)

# Calculate the mean probability for visualization
meanProb = [(low + high) / 2 for low, high in prob]

# Set positions for nodes based on their coordinates
pos = {i: eval(nodes.iloc[[i]]["coords"][i]) for i in range(len(nodes))}

# Plot the graph with probabilities
plotTreeWithProb(G, meanProb,"", pos)
