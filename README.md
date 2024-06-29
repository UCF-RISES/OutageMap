# OutageMap
OutageMap is an open-source software that can be used to generate weather related outage data for a given power distribution network. The framework uses a set of fragility curves to describe the extent of weather impacts on physical features, which can be applied in a straightforward way to real-world networks and extreme weather conditions once data of the actual physical networks and their past impact outcomes becomes available

This is the code repository for the following paper. To use this repo, please cite:

Kenneth McDonald, Colin Le, and Zhihua Qu. "Open-Source Modeling of Extreme Weather Impact on Distribution Networks." Accepted to Open Source Modeling and Simulation of Energy Systems (OSMSES), 2024.

## Installing OutageMap
OutageMap was designed using Python 3.11.9 and Anaconda. 

First, clone or download the repository.

If you do not have an existing Anaconda installation, go to https://www.anaconda.com/products/individual, click on skip registration, and then click the green download button.

In the windows search bar, type and select Anaconda Prompt. Open the prompt and navigate to `OutageMap/Conda Environment Setup` using `cd` commands. This is where the enviroment `.yml` file is currently stored. Once in the directory run the following command:
``` shell
conda env create -f environment.yml
```
This creates the Python environment named `OutageMap`, with all the packages needed to run the software.

 To activate the environment, run:
``` shell
conda activate OutageMap
```

Move back to the main directory `OutageMap` using 
```shell
cd ..
```
## Running the Example

### Collecting the Network Data
Inside the repo folder, navigate to the P3R folder and then the DSS folder. Upon downloading the repository, the OpenDSS files used for the simulation presented in the paper are already given. 

To redownload them, you can use the following:
1. If you do not have one, create a free AWS account and download the AWS CLI interface from: https://awscli.amazonaws.com/AWSCLIV2.msi. Check to make sure AWS was installed correctly by running the following in a `Command Prompt`:
    ``` shell
    aws --version 
    ```
2. In the same `Command Prompt` navigate to the `OutageMap/P3R/DSS` and run the command 
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

    Once the data has completed downloading, you may close the command prompt.

4. Navigate to  `OutageMap/P3R/DSS/P3R/scenarios/base_timeseries/opendss/p3rhs0_1247/p3rhs0_1247--p3rdt1052` and you should now see the files
    -   Buscoords.dss   
    -   Capacitors.dss 
    -	Lines.dss
    -	LineCodes.dss
    -	Loads.dss
    -   Loadshapes.dss
    -   Master.dss
    -	Transformers.dss

    For the final step, we now want to copy these files, along with the folder labeled `OutageMap/P3R/DSS/P3R/profiles` to `OutageMap/P3R/DSS/profiles`. Then folder `OutageMap/P3R/DSS/P3R` can be removed. 

5. Open `OutageMap/P3R/DSS/Loadshapes.dss` in Notepad, press `Ctrl+F` and replace every occurence of `../../../../../profiles` to `profiles`.

### Extracting Data from OpenDSS files
To extract the data from the OpenDSS circuit into Python, run `OutageMap/importData.py` by calling the command 
```shell
python importData.py
```
Upon successful execution, you should obtain the graph of the network below
![Alt text](imgs/importedPlot.png?raw=true "Title")

### Collection of Extreme Weather Events
To import the weather event from the CSV into Python, run `OutageMap/getWeather.py` by calling the command:
```shell
python getWeather.py
```
The steps to obtained the weather event CSV are detailed in `Extreme Weather Events from NOAA`.

### Conversion of Weather Features to Weather Impact Score
To scale the data and convert to a weather impact score, run `OutageMap/findWeatherImpact.py` by calling the command: 
```shell
python findWeatherImpact.py
```

### Generating the Outage Data
To generate the outage data, run `OutageMap/main.py` by calling the command:
```shell
python main.py
```
Upon successful execution, you should obtain the outage map below
![Alt text](imgs/scenario1_outageMapNew.png?raw=true "Title")

## Other Information

### Extreme Weather Events from NOAA
The collection of extreme weather events starts on NOAA’s Storm Event Database. As stated in the paper, the chosen event for this tutorial is a “bomb cyclone” event that occurred on March 21st, 2023 in the Greater San Francisco Area. 

We start by heading to the site at https://www.ncdc.noaa.gov/stormevents/. 
1. We then choose California in the “Select State or Area” and press Search. 

2. The next page is a advanced search tool. We set  
    - Set the start and end data to 03/21/2023 and 03/22/2023
    - San Francisco for the County 
    - All events for event type 
    
    and then press search. 

3. The results, as shown below, indicate 7 events that occurred during March 21st all relating to strong or high wind events. To download this data, we click `CSV Download`, which is encased in a black box in image below.

![Alt text](imgs/StormDataResults.png?raw=true "Title")

Next, we open the downloaded CSV to modify the contents through the following:

1. We only need one entry to define the event, so we take the end date and time of the last row, and move it to the first row. Rows 3-8 can be deleted after.

2. The next step is to convert the time zone from PST to UTC since NLDAS2 requires UTC time. To do so, we change the start time to `1900`, the end date to be `3/22/2023` and the end time to be `0500`. 

3. Once these changes have been made, the file can be saved in the OutageMap directory and closed.
