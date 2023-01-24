
# NYPD_project

NYPD 2022/23 final project

This repository contains files allowing to analyze CO2 emission and GDP per capita.
Results of those analyses are then saved to csv file.


## Installation

Install this project with pip while in the folder with "setup.py" file

```bash
  pip install .
```
    
## Usage
All of the command line options are described in help. Below there is an example running the package:

```bash
project_Kochanska -gdp gdp.csv -pop pop.csv -co2 emissions.csv -y1 2010 -y2 2014 -f results.csv
```
where:
* `gdp, pop and co2` - should contain respective csv file
* `y1 and y2` - years which should be chosen for the analysis
* `f` - name of output csv file, to which results will be saved

Another example of running the program is below:

```bash
python -m project_Kochanska.program -gdp gdp.csv -pop pop.csv -co2 emissions.csv -y1 2002 -y2 2014 -f results.csv
```

To run tests simply use following command

```bash
pytest project_Kochanska
```

## Author

Zofia Kochańska

