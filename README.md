# What is OutageMap and who is it for

## Installing OutageMap
OutageMap was designed using Python and Anaconda. 

If you do not have an existing Anaconda installation, go to https://www.anaconda.com/products/individual, click on skip registration, and then click the green download button.

Open the Anaconda Prompt and navigate to `OutageMap/Conda Environment Setup` where the enviroment `.yml` file is currently stored and run the following command:
``` shell
	conda env create -f environment.yml
```
This creates the Python environment named `OutageMap1`, with all the packages needed to run the software.

3. To activate the environment, run:
``` shell
	conda activate OutageMap1
```
## Running the Example

### Collecting the Network Data
Inside the repo folder, navigate to the P3R folder and then the DSS folder. Upon downloading the repository, the OpenDSS files used for the simulation presented in the paper are already given. 

To redownload them, you can use the following:
1. If you do not have one, create a free AWS account and download the AWS CLI interface from: https://awscli.amazonaws.com/AWSCLIV2.msi. Check to make sure AWS was installed correctly by running the following in a `Command Prompt`:
    ``` shell
    aws --version 
    ```
2. In the same `Command Prompt` navigate to the `P3R/DSS` and run the command 
    ```shell
    mkdir P3R && cd P3R && mkdir profiles && mkdir scenarios && cd scenarios && mkdir base_timeseries && cd base_timeseries && mkdir opendss && cd opendss && cd ../../..
    ```
    to create the folders and empty subdirectories.

3. Run each command to download the files
    ```shell
    aws s3 cp s3://oedi-data-lake/SMART-DS/v1.0/2018/SFO/P3R/scenarios/base_timeseries/opendss/ ./scenarios/base_timeseries/opendss --recursive --no-sign-request
    ```

    ```shell
    aws s3 cp s3://oedi-data-lake/SMART-DS/v1.0/2018/SFO/P3R/profiles/ ./profiles --recursive --no-sign-request
    ```

4. Once the data has completed downloading, you may close the command prompt and run OpenDSS. If you do not have OpenDSS you may download it from https://sourceforge.net/projects/electricdss/.

5. In OpenDSS, go to `File->Open` and then open the following file: 
    `P3R\scenarios\base_timeseries\opendss\p3rhs0_1247\p3rhs0_1247--p3rdt1052\Master.dss`

    Once the file opens, comment out the last 6 lines by placing an `!` at the front of each line, and then save the file. 

6. After saving the file, find the Compile File Listed button (gray button near top middle) to initialize the network. OpenDSS will compile the network and will display results and statistics on the side when it is completed. 

7. Press `Show->Buses`. This will show a Bus List text file that can be closed after opening. 

8. Press `Show->Elements`. This will show a Element List text file that can be closed after opening. 

9. Inside `P3R\scenarios\base_timeseries\opendss\p3rhs0_1247\p3rhs0_1247--p3rdt1052`, 
you should now see two new files
    - feeder_p3rdt1052-p3rhs0_1247x_Buses.txt
    - feeder_p3rdt1052-p3rhs0_1247x_Elements.txt

    For the final step, we now want to copy the files:
    -   feeder_p3rdt1052-p3rhs0_1247x_Buses.txt
    -   feeder_p3rdt1052-p3rhs0_1247x_Elements.txt
    -	Lines.dss
    -	LineCodes.dss
    -	Loads.dss
    -	Transformers.dss

    from
    `P3R\DSS\P3R\scenarios\base_timeseries\opendss\p3rhs0_1247\p3rhs0_1247--p3rdt1052` 
    to `P3R\DSS`.


### Extracting Data from OpenDSS files
To extract the data from the OpenDSS files into Python, run `importData.py`
### Collection of Extreme Weather Events

The collection of extreme weather events starts on NOAA’s Storm Event Database. As stated in the paper, the chosen event for this tutorial is a “bomb cyclone” event that occurred on March 21st, 2023 in the Greater San Francisco Area. 

We start by heading to the site at https://www.ncdc.noaa.gov/stormevents/. 
1. We then choose California in the “Select State or Area” and press Search. 

2. The next page is a advanced search tool. We set  
    - Set the start and end data to 03/21/2023 and 03/22/2023
    - San Francisco for the County 
    - all events for event type 
    
    and then press search. 
    
3. The results should indicate 7 events that occurred during March 21st all relating to strong or high wind events. To download this data, we click `CSV Download`.

Next, we open the downloaded CSV to modify the contents through the following:

1. We only need one entry to define the event, so we take the end date and time of the last row, and move it to the first row. Rows 3-8 can be deleted after.

2. The next step is to convert the time zone from PST to UTC since NLDAS2 requires UTC time. To do so, we change the start time to `1900`, the end date to be `3/22/2023` and the end time to be `0500`. 

3. Once these changes have been made, the file can be saved in the OutageMap directory and closed.

To import the weather event from the CSV into Python, run `getWeather.py`

### Conversion of Weather Features to Weather Impact Score
To scale the data and convert to a weather impact score, run `findWeatherImpact.py`. 

### Generating the Outage Data
To generate the outage data, run `main.py`.

# File Explanations
## `importData.py`
Lines 11-16 define the paths to the OpenDSS files.
### Data Extraction: 
Lines 19-31 deal with extraction of DSS data from text file formats using re.search function:
-	Bus Data: The readBusData function retrieves the bus name, coordinates, base voltage, and the number of connected nodes from the bus feeder text file.
-	Transformer Data: The readTransformerData function extracts key transformer attributes such as the transformer's name, number of phases, windings, normal high voltage capacity (NormHKVA), winding numbers (Wdg), connection types (ConnType), voltage levels (kV), capacity (kVA), and connected buses from Transformers.dss.
-	Line Code Data: In the readLineCodeData function, parameters such as the line code's name, number of phases, fault rate, resistance matrix (R), reactance matrix (X), capacitance matrix (C), and normal ampacity are parsed from LineCodes.dss.
-	Line Data: The readLineData function extracts information such as the line's name, length, connected buses, number of phases, switch status, enabled status, and the line code from Lines.dss.
-	Load Data: The readLoadData function obtains the load's name, connection type, bus, voltage levels (kV, Vminpu, Vmaxpu), power (kW, kvar), and number of phases from Loads.dss.
Organizing Data: Lines 36-75 focus on organizing the extracted data into lists for each network component. These lists are then used to construct graph components representing nodes and edges.
-	Node Data: Nodes are created with attributes such as name, voltage, and coordinates, along with geographical data like elevation and vegetation type, which are obtained using HyRiver functions. Elevation data is obtained from HyRiver’s Py3DEP, which utilizes USGS’s 3DEP data. Vegetation data is obtained from HyRiver’s PyGeoHydro, which utilizes the NLCD 2021 for land cover/ land use data.
-	Edge Data: Edges represent connections between nodes, incorporating attributes like length, type, elevation and operational status. The midpoint of the edge is used to determine the edge elevation. By averaging the coordinates of two connected nodes, one can utilize the same function for finding the node elevation to find the elevation at the midpoint.
### Graph Construction and Visualization: 
The nodes and edges are then aggregated into a graph, specifically the Multi-DiGraph structure, using the Python package NetworkX. This approach allows for detailed attributes to be associated with each node and edge element, facilitating complex network analyses and visualizations. Using ‘nx.draw_networkx’, the graph of the distribution network can be visualized to show the connectivity and layout of network components.
### Exporting Data: 
After visualizing the graph, the last step is to export the data. Although NetworkX allows for the edge list of the graph to be exported directly, the node list must be created manually. To achieve this, as nodes are added to the graph, their information is simultaneously appended to a dictionary called nodeDict. Once the edge and node lists, which contains the attributes for each node and edge, are obtained, they can then be converted to Pandas Dataframes and subsequently exported as CSV files for future use.

## `getWeather.py`
To import the weather event into Python, we utilize the getWeather.py script. The inputs to this script (lines 13-20) are the node and edge lists, along with the storm event csv file. The script is set up so that multiple events can be defined in one csv file, but for the purpose of this tutorial, we only have one event so the loop in lines 27 will only have one iteration. Starting from line 27, we open the csv file and grab the start and end dates and times. Then the loop starting from line 37 loops through each node in the node list. First the coordinates of the node are extracted, then the getWeatherByCoords function is called to grab the hourly wind and rain data at the specific coordinate. The wind data is given as uv components and is transformed to wind speed and converted to mph from m/s through line 51-56.
The next portion of the code determines the weather for the edges by taking the average weather data between two nodes. Lines 70 through 73 grab the node weather data from the event. Lines 76-78 create a simple edge list to reference when calculating the average weather. Lines 83-87 grab the wind and rain data for the nodes, and lines 90-91 initialize dataframes for the edge weather. Lines 94-101 calculate the average wind and rain values between two nodes and adds them to the edge data frames. Lines 104 – 109 rename the edgelist dataframe and then save it to a CSV file.


## `findWeatherImpact.py`

Once the weather event has been downloaded and imported into Python, we need to scale the data and convert to a weather impact score. We will use findWeatherImpact.py to calculate it. We start by setting the network and paths in lines 6-9. Lines 12-13 call on createLevelsAlt in mainHelper.py to generate severity levels for the weather values. Lines 16 loops through each weather event that was imported. Lines ?? set the alpha values for node features. Lines 23-27 read in the weather data and remove and the unnamed column in the file. From the weather event, the minimum and maximum values are found then used to create the upper and lower bounds of the forecasted interval. Lines 36-38 create the vectors to store the upper and lower bounded weather impact scores in. Lines 41 through 46 loops through each node to normalize its lower and upper bound weather values to be within the range of [0, 1]. Lines 49-50 set the weather impact interval at for all features at each node. Lines 53-54 calculate the weather impact my multiplying alpha transpose with the weather score. Lines 56-69 formats the weather impact for high and low scenarios, stores the data in a pandas data frame then converts the data frame to a csv and saves it. Lines 71-133 repeat the exact same process for the edges in the network.

## `main.py`
### Initialization
After all the network and weather impact data has been acquired, the outage data generation can begin using main.py. Lines 8-11 define the feature labels for nodes and edges, the number of severity levels, and the network to be used. Lines 16-44 define the upper and lower bound mean and covariance values used. For this tutorial we are simulating Scenario 1 so the parameters of Scenario 2 are commented out. 
Lines 46-65 load in the node and edge list csvs, initialize forecasted factors and range dictionaries, and construct the graph using the node and edge data. 
### Severity Level Conversion
Lines 68 begins a loop to go through each feature of each component and create the associated severity levels. This function callas on assign_values_to_ranges which takes the minimum and maximum values from a given range, finds the step size based on number of desired levels, and creates bins (with count) that represent the set of severity levels. Specifically Line 71 of main calls the inv parameter of the function since we are considering lower elevation to be more severe. 
### Conditional Probability (Fragility Curves)
Lines 83 creates the lookup table for the mean and standard deviation ranges through createTables. Lines 86-87 loads in the weather impact data generated from the previous section. 
Lines 90-111 calculate the conditional probability of damage for nodes and edges. It loops through each node or edge, finds the weather impact interval associated with the graph component features, then calls generateProb to calculate. 
generateProb starts by checking if the node is valid and initializes lists to store severity levels, impact means, and squared standard deviations. Then a loop is called to cycle through each feature of the component, finds it severity level using findLevel, which facilitates the lookup table. From the severity level, the mean and standard deviation values can be found and stored. Once every feature has been looped through, the feature vector (random variable), the mean vector and covariance matrix can be created. Then these variables are passed to the mvncdf function to find the conditional probability. The resulting probability is returned from the function.
### Joint Probability of Service Outage
Once the conditional probabilities of damage have been determined, then the joint probability of service outage at each node can be calculated. The list of conditional probabilities for the nodes and edge, along with the graph structure are passed to probOfNodeAndParent. 
probOfNodeAndParent starts by creating initializing a new list to store the joint probabilities. This is done by copying the node probability list. Starting from the root node, a queue is then initialized for breadth first search of the graph, processing each nodes child sequentially.  ally. For each parent-child pair, it updates the child's probability by applying the inclusion-exclusion principle on the probabilities of the parent, child, and their connecting edge. The updated probability list is returned.
### Visualizing the Results
After probOfNodeAndParent is returned, we now have the joint probability of service outage (in the form of a interval) for all the nodes in the network. To visualize the results, we take the mean of the interval, and utilize the plotTreeWithProb function. plotTreeWithProb creates a figure of the graph using networkx and defines a color map corresponding to the probability of service outage. In the colormap, green means a low probability and red indicates a high probability. Each node is then colored according to their probability and the figured is displayed.
