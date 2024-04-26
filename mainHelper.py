import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from itertools import combinations
from scipy.stats import norm, multivariate_normal
import networkx as nx
import matplotlib.pyplot as plt 
import warnings
from collections import deque
warnings.filterwarnings('ignore')

def assign_values_to_ranges(values, num_bins=10):
    """
    Assign values to ranges (bins) based on the specified number of bins.
    
    Parameters:
    - values: List of numerical values.
    - num_bins: Number of bins to divide the values into.
    
    Returns:
    - A list of tuples representing the range of each bin and the count of values in each bin.
    """
    if values is None:
        return []
    
    min_val = min(values)
    max_val = max(values)
    range_size = (max_val - min_val) / num_bins
    
    # Initialize bins
    bins = [(min_val + i * range_size, min_val + (i + 1) * range_size) for i in range(num_bins)]
    bin_counts = [0] * num_bins
    
    # Assign values to bins
    for value in values:
        if value == max_val:
            # Handle edge case where value is the maximum value
            bin_index = num_bins - 1
        else:
            bin_index = int((value - min_val) / range_size)
        bin_counts[bin_index] += 1
    
    # Combine bins and counts
    bins_with_counts = [(bins[i], bin_counts[i]) for i in range(num_bins)]
    
    return bins_with_counts

def createLevels(minValue, maxValue, levels):
    step = (maxValue - minValue) / (levels - 1)
    return [minValue + step * i for i in range(levels)]

def createTables(levels, stdRange, meanRange):
    mean, std = {}, {}
    for category, values in stdRange.items():
        minValue = values[0]
        maxValue = values[1]
        std[category] = {i+1: val for i, val in enumerate(createLevels(minValue, maxValue, levels)[1:])}
    for category, values in meanRange.items():
        minValue = values[0]
        maxValue = values[1]
        mean[category] = {i+1: val for i, val in enumerate(createLevels(minValue, maxValue, levels)[1:])}
    
    return mean, std

def findLevel(observedVal, featureName, forecastedRange, numOfBins):
    for index, interval in enumerate(forecastedRange[featureName]):
        low, high = interval
        if (low <= observedVal and observedVal <= high) or (high <= observedVal and observedVal <= low):
            return index + 1
    
    return numOfBins

def inclusionExclusion(pr_list):
    union_prob = 0
    for i in range(1, len(pr_list) + 1):
        comb = combinations(pr_list, i)
        sum_of_probs = sum([prod(combination) for combination in comb])
        union_prob += sum_of_probs if i % 2 != 0 else -sum_of_probs
    return union_prob

def prod(iterable):
    result = 1
    for i in iterable:
        result *= i
    return result


def generateProb(node, edge, nodeFeatures, edgeFeatures, meanRange, stdRange, forecastedRange, impactWeatherN, impactWeatherE, levels):
    prob = []
    test = [0, 715, 762, 714]
    if node is not None and not node.empty:
        listLevel = []
        listIM = []
        listSTD = []
        for feature in nodeFeatures:
            differiate = feature.split(" ")
            level = findLevel(float(node[differiate[0]]), feature, forecastedRange,levels)
            impactMean = meanRange[feature][level]
            impactStd = stdRange[feature][level]

            listLevel.append(float(impactWeatherN[feature]))
            listIM.append(impactMean)
            listSTD.append(impactStd ** 2)

        featureVector = np.array(listLevel)
        meanVector = np.array(listIM)
        sigma = np.diag(listSTD)


        mvn = multivariate_normal(mean=meanVector, cov=sigma)
        cdf_value = mvn.cdf(featureVector)
        prob.append(cdf_value)

    if edge is not None and not edge.empty:
        listLevel = []
        listIM = []
        listSTD = []
        for feature in edgeFeatures:
            differiate = feature.split(" ")
            level = findLevel(float(edge[differiate[0]]), feature, forecastedRange, levels)
            impactMean = meanRange[feature][level]
            impactStd = stdRange[feature][level]

            listLevel.append(float(impactWeatherE[feature]))
            listIM.append(impactMean)
            listSTD.append(impactStd ** 2)

        featureVector = np.array(listLevel)
        meanVector = np.array(listIM)
        sigma = np.diag(listSTD)

        mvn = multivariate_normal(mean=meanVector, cov=sigma)
        cdf_value = mvn.cdf(featureVector)
        prob.append(cdf_value)

    return prob[0]

def probOfNodeAndParent(probN, probE, graph):
    newProb = [[low, high] for low, high in probN]
    queue = deque()
    queue.append(0)
    while queue:
        parent = queue.popleft()
        for child, edge in graph[parent]:
            for j in range(2):
                newProb[child][j] = inclusionExclusion([newProb[parent][j], newProb[child][j], probE[edge][j]])
            queue.append(child)
    return newProb

def plotTreeWithProb(tree, probabilities, title, pos):
    fig, ax = plt.subplots(constrained_layout = True)
    
    green_red_colormap = LinearSegmentedColormap.from_list('GreenRed', ['green', 'red'])

    nodeColors = [green_red_colormap(prob) for prob in probabilities]
    nx.draw(tree, pos=pos, ax=ax, with_labels=False , node_color=nodeColors, node_size=80, arrowsize=7, arrowstyle='fancy', arrows=False, font_size=12)

    scalarmappaple = plt.cm.ScalarMappable(cmap=green_red_colormap, norm=plt.Normalize(vmin=0, vmax=1))
    cbar = fig.colorbar(scalarmappaple, ax=ax)
    
    cbar.set_label('Probability of an Outage')
    
    plt.title(title)
    plt.show()

