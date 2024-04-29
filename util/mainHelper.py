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

def assign_values_to_ranges(values, levels=10):
    """
    Assign values to ranges (bins) based on the specified number of bins.
    
    Parameters:
        values (List[float]): List of numerical values to be binned.
        levels (int): Number of bins (or severity levels) to divide the values into.
    Returns:
        List[Tuple[Tuple[float, float], int]]: A list of tuples where each tuple represents a bin range and the count of values falling within that bin.
    """
    if values is None:
        return []
    
    min_val = min(values)
    max_val = max(values)
    range_size = (max_val - min_val) / levels
    
    # Initialize bins
    bins = [(min_val + i * range_size, min_val + (i + 1) * range_size) for i in range(levels)]
    bin_counts = [0] * levels
    
    # Assign values to bins
    for value in values:
        if value == max_val:
            # Handle edge case where value is the maximum value
            bin_index = levels - 1
        else:
            bin_index = int((value - min_val) / range_size)
        bin_counts[bin_index] += 1
    
    # Combine bins and counts
    bins_with_counts = [(bins[i], bin_counts[i]) for i in range(levels)]
    
    return bins_with_counts

def createLevels(minValue, maxValue, levels):
    """
    Function to generate a list of evenly spaced severity levels between a specified minimum and maximum value
    Args:
        minValue (float): Lowest severity level value.
        maxValue (float): Highest severity level value.
        levels (int): Total number of severity levels to generate between the min and max values.
    Returns:
        List[float]: List of calculated severity levels.
    """
    step = (maxValue - minValue) / (levels - 1)
    return [minValue + step * i for i in range(levels)]

def createTables(stdRange, meanRange, levels):
    """
    Function to create tables for the mean and standard deviation of the impact of damaging weather conditions based on specified ranges and severity levels.

    Args:
        stdRange (Dict[str, List[float]]): Dictionary mapping features to a list with minimum and maximum standard deviation values.
        meanRange (Dict[str, List[float]]): Dictionary mapping features to a list with minimum and maximum mean impact values.
        levels (int): Number of severity levels to be used for both standard deviation and mean values.
    Returns:
        mean (Dict[str, List[float]]): Keys are the names of features. Value is list of severity levels for mean for damaging weather impact.
        std (Dict[str, List[float]]): Keys are the names of features. Value is list of severity levels for mean for damaging weather impact.
    """
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

def findLevel(observedVal, featureName, forecastedRange, levels):
    """
    Function to identify the severity level of an observed value for a given feature based on predefined ranges

    Args:
        observedVal (float): The observed value for the feature.
        featureName (str): Name of the feature.
        forecastedRange (Dict[str, List[Tuple[float, float]]]): Dictionary mapping feature names to lists of tuples, each tuple representing a range for a severity level.
        levels (int): Total number of severity levels.
    Returns:
        int: The severity level that the observed value falls into.
    """

    for index, interval in enumerate(forecastedRange[featureName]):
        low, high = interval
        if (low <= observedVal and observedVal <= high) or (high <= observedVal and observedVal <= low):
            return index + 1
    
    return levels

def inclusionExclusion(pr):
    """
    Function to calculate the probability of the union of events using the inclusion-exclusion principle based on provided probabilities of individual events.

    Args:
        pr (List[float]): List of probabilities for individual events.
    Returns:
        float: Probability of the union of the events after applying the inclusion-exclusion principle.
    """

    union = 0
    for i in range(1, len(pr) + 1):
        comb = combinations(pr, i)
        sum_of_probs = sum([prod(combination) for combination in comb])
        union += sum_of_probs if i % 2 != 0 else -sum_of_probs
    return union

def prod(iterable):
    """
    Function that computes the product of all elements in a given list, primarily used within the inclusionExclusion function.

    Args:
        iterable (Iterable[float]): Iterable of floats whose product is to be calculated.
    Returns:
        float: The product of the elements.
    """

    result = 1
    for i in iterable:
        result *= i
    return result


def generateProb(node, edge, nodeFeatures, edgeFeatures, meanRange, stdRange, forecastedRange, impactWeatherN, impactWeatherE, levels):
    """
    Function that calculates the probability of an outage based on the forecasted impact of weather conditions on nodes and edges within a network.

    Args:
        node (pd.DataFrame or None): Data frame containing features and values for a specific node.
        edge (pd.DataFrame or None): Data frame containing features and values for a specific edge.
        nodeFeatures (List[str]): List of feature names relevant to nodes.
        edgeFeatures (List[str]): List of feature names relevant to edges.
        meanRange (Dict[str, List[float]]): Dictionary mapping feature names to their mean impact values across severity levels.
        stdRange (Dict[str, List[float]]): Dictionary mapping feature names to their standard deviation values across severity levels.
        forecastedRange (Dict[str, List[List[float]]]): Dictionary mapping feature names to their forecasted value ranges across severity levels.
        impactWeatherN (Dict[str, List[float]]): Dictionary containing the impact levels of weather on node features.
        impactWeatherE (Dict[str, List[float]]): Dictionary containing the impact levels of weather on edge features.
        levels (int): Number of severity levels between the lowest and highest values.
    Returns:
        float: Calculated probability of outage for the node or edge.
    """

    prob = []
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
    """
    Function that aggregates the probabilities of outages for nodes and their parent nodes in the network graph, taking into account the dependencies due to network topology.

    Args:
        probN (List[List[float]]): List containing probabilities of outage for nodes.
        probE (List[List[float]]): List containing probabilities of outage for edges.
        graph (defaultdict[list]): Graph structure representing the network, where keys are parent node indices and values are lists of child node and edge index pairs.
    Returns:
        List[List[float]]: Aggregated probabilities of outages for nodes considering their parent node dependencies.
    """

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
    """
    Function to visualize the network graph with nodes colored based on their probability of outage, providing a visual tool for assessing network vulnerability.

    Args:
        tree (nx.DiGraph): Directed graph representing the network topology.
        probabilities (List[float]): List of probabilities associated with each node in the graph.
        title (str): Title for the plotted graph.
        pos (Dict[int, Tuple[float, float]]): Dictionary mapping node indices to their positions for plotting.
    Returns:
        Displays a visual representation of the network graph with nodes colored according to their outage probabilities.
    """
        
    fig, ax = plt.subplots(constrained_layout = True)
    
    green_red_colormap = LinearSegmentedColormap.from_list('GreenRed', ['green', 'red'])

    nodeColors = [green_red_colormap(prob) for prob in probabilities]
    nx.draw(tree, pos=pos, ax=ax, with_labels=False , node_color=nodeColors, node_size=80, arrowsize=7, arrowstyle='fancy', arrows=False, font_size=12)

    scalarmappaple = plt.cm.ScalarMappable(cmap=green_red_colormap, norm=plt.Normalize(vmin=0, vmax=1))
    cbar = fig.colorbar(scalarmappaple, ax=ax)
    
    cbar.set_label('Probability of an Outage')
    
    plt.title(title)
    plt.show()

def weatherImpact(alpha, observed):
    """
    Function to computes the weather impact on network components based on observed data and predefined severity levels.

    Args:
        alpha (Dict[str, List[float]]): Dictionary containing coefficients that define how different features influence the impact of weather.
        observed (List[float]): List of observed values for the weather conditions.
    Returns:
        Dict[str, float]: Dictionary mapping each feature to its calculated weather impact based on the observed values.
    """
    
    observed_array = np.array(observed)
    weatherImpact = dict(alpha)
    for feature in alpha:
        alpha_feature_array = np.array(alpha[feature])
        product = np.dot(alpha_feature_array, observed_array)
        weatherImpact[feature] = product
    return weatherImpact