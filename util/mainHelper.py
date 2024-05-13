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

def assign_values_to_ranges(values, levels=10, inv=False):
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
    
    if inv == True:
        min_val = max(values)
        max_val = min(values)
    else:
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
    # Initialize dictionaries to store mean and standard deviation values
    mean, std = {}, {}

    # Calculate the standard deviation levels for each category
    for category, values in stdRange.items():
        # Extract the minimum and maximum values for the category
        minValue, maxValue = values[0], values[1]
        # Create standard deviation levels based on the range and store them in the dictionary
        std[category] = {i+1: val for i, val in enumerate(createLevels(minValue, maxValue, levels)[1:])}

    # Calculate the mean levels for each category
    for category, values in meanRange.items():
        minValue, maxValue = values[0], values[1]
        mean[category] = {i+1: val for i, val in enumerate(createLevels(minValue, maxValue, levels)[1:])}

    # Return the dictionaries containing mean and standard deviation values
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

    # Initialize the variable `union` to accumulate the union probability
    union = 0

    # Loop over all possible non-empty subsets of probabilities
    for i in range(1, len(pr) + 1):
        # Generate all combinations of `i` probabilities from the list `pr`
        comb = combinations(pr, i)
        # Calculate the sum of products of probabilities for each combination
        sum_of_probs = sum([prod(combination) for combination in comb])
        # Add to or subtract from the union based on whether the number of elements in the combination is odd or even
        # This is based on the inclusion-exclusion principle
        union += sum_of_probs if i % 2 != 0 else -sum_of_probs

    # Return the calculated union probability
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

    # Initialize a list to store the probability outcomes
    prob = []

    # Check if the node is valid and not empty
    if node is not None and not node.empty:
        # Initialize lists to store levels, impact means, and squared impact standard deviations
        listLevel, listIM, listSTD = [], [], []
        
        # Iterate through features associated with the node
        for feature in nodeFeatures:
            # Split the feature to access the data from the node
            differiate = feature.split(" ")
            # Find the appropriate level for the current node value
            level = findLevel(float(node[differiate[0]]), feature, forecastedRange, levels)
            # Retrieve the mean and standard deviation impacts for this level
            impactMean = meanRange[feature][level]
            impactStd = stdRange[feature][level]

            # Store the actual observed level, mean impact, and variance (std squared)
            listLevel.append(float(impactWeatherN[feature]))
            listIM.append(impactMean)
            listSTD.append(impactStd ** 2)

        # Convert lists to numpy arrays for vector operations
        featureVector = np.array(listLevel)
        meanVector = np.array(listIM)
        sigma = np.diag(listSTD)  # Create a diagonal covariance matrix from variances

        # Initialize a multivariate normal distribution
        mvn = multivariate_normal(mean=meanVector, cov=sigma)
        # Calculate the cumulative distribution function (CDF) value at the feature vector
        cdf_value = mvn.cdf(featureVector)
        # Append the computed CDF value to the probability list
        prob.append(cdf_value)

    # Check if the edge is valid and not empty
    if edge is not None and not edge.empty:
        # Repeat the same process as for the node, but for the edge
        listLevel, listIM, listSTD = [], [], []
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

    # Return the first element of the probability list (assumes there's at least one element)
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

    # Create a new list of probability ranges by copying from the provided probN list
    newProb = [[low, high] for low, high in probN]

    # Initialize a deque for breadth-first search traversal of the graph
    queue = deque()
    # Start with the root node (assumed to be node 0)
    queue.append(0)
    # Continue until there are no more nodes to process
    while queue:
        #print(queue)
        # Retrieve the next node to process from the queue
        parent = queue.popleft()
        print(parent)
        # Iterate over all children connected to the current parent node
        for child, edge in graph[parent]:
            # Update the probability range for each child node
            for j in range(2):
                # Apply the inclusion-exclusion principle to update probability ranges
                newProb[child][j] = inclusionExclusion([newProb[parent][j], newProb[child][j], probE[edge][j]])
            # Add the child to the queue to process its own children later
            queue.append(child)

    # Return the updated probability ranges for all nodes
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
        
    # Create a figure and an axis with constrained layout for better spacing
    fig, ax = plt.subplots(constrained_layout=True)

    # Create a custom colormap from green to red
    green_red_colormap = LinearSegmentedColormap.from_list('GreenRed', ['green', 'red'])

    # Map each probability to a color in the colormap and store these colors
    nodeColors = [green_red_colormap(prob) for prob in probabilities]
    # Draw the tree graph with customized node colors and styles
    nx.draw(tree, pos=pos, ax=ax,with_labels=False, node_color=nodeColors, node_size=80, 
            arrowsize=7, arrowstyle='fancy', arrows=False, font_size=12)

    # Create a ScalarMappable to interpret the colormap scale properly
    scalarmappaple = plt.cm.ScalarMappable(cmap=green_red_colormap, norm=plt.Normalize(vmin=0, vmax=1))
    # Add a colorbar to the axis using the ScalarMappable, and set its label
    cbar = fig.colorbar(scalarmappaple, ax=ax)
    cbar.set_label('Probability of an Outage')

    # Set the title of the plot
    plt.title(title)
    # Display the plot
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
    
    # Convert the list of observed values into a numpy array for vector operations
    observed_array = np.array(observed)

    # Initialize a dictionary to store the computed weather impacts for each feature
    weatherImpact = dict(alpha)

    # Iterate over each feature present in the alpha dictionary
    for feature in alpha:
        # Convert the coefficients for the current feature into a numpy array
        alpha_feature_array = np.array(alpha[feature])
        # Compute the dot product of the coefficients and the observed values
        product = np.dot(alpha_feature_array, observed_array)
        # Store the resulting product in the weatherImpact dictionary under the current feature
        weatherImpact[feature] = product

    # Return the dictionary containing the weather impacts for each feature
    return weatherImpact

def createLevelsAlt(minVal,maxVal,numLevels):
    """
    Create levels based on minimum, maximum values and number of levels.

    Args:
        minVal (float): Minimum value of the levels.
        maxVal (float): Maximum value of the levels.
        numLevels (int): Number of levels to create.

    Returns:
        list: A list of dictionaries containing 'min' and 'max' values for each level.
    """
    levels = []
    
    # Calculate the step size between levels
    step = (maxVal - minVal) / (numLevels - 1)
    
    # Append the first level, starting from minVal
    levels.append({'min':minVal, 'max':minVal + step})
    
    # Append subsequent levels by incrementing by step size
    for i in range(1,numLevels-1):
        levels.append({'min':levels[i-1]['max'], 'max':levels[i-1]['max'] + step})
    return levels

def findWeatherLevel(weather_value,weather_levels):
    """
    Find the weather level based on the weather value and levels.

    Args:
        weather_value (float): Value representing weather conditions.
        weather_levels (list): List of dictionaries containing 'min' and 'max' values for each weather level.

    Returns:
        float: The score corresponding to the weather level (level index multiplied by 0.1).
    """
    for i in range(len(weather_levels)):
        # Check if the weather_value falls within the min and max of the current level
        if (weather_value >= weather_levels[i]['min']):
            if (weather_value <= weather_levels[i]['max']):
                # Check if the weather_value falls within the min and max of the current level
                score = (i+1)*0.1
                return score

def findFeatureLevel(feature_value,feature_levels):
    """
    Find the feature level based on the feature value and levels.

    Args:
        feature_value (float or numpy.ndarray): Value or array representing the feature.
        feature_levels (list): List of dictionaries containing 'min' and 'max' values for each feature level.

    Returns:
        int: The index of the feature level where the feature_value falls.
    """
    for i in range(len(feature_levels)):
        # Check if the feature_value falls within the min and max of the current level
        # The 'all() == True' check ensures the condition is met for all elements in case of arrays
        if ((feature_value >= feature_levels[i]['min']) and (feature_value <=feature_levels[i]['max'])).all() ==True:
            level = i
            return level
