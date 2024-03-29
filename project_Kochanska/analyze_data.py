"""Analyze data

This script analyzes data stored in one Dataframe and saves the results
to csv file.

This file contains the following functions:

    * get_per_capita - returns Dataframe with added per capita columns
    * create_multiindex - returns pandas Multiindex
    * find_5_highest - return Dataframe with data about countries with
    highest data in provided category
    * find_co2_changes - return Dataframe with data about countries which
    had biggest and smallest changes in co2 emission
    * save_results - Saves obtained results to  csv file
"""
import itertools
import os
from typing import List, Union
import pandas as pd

def get_per_capita(data: pd.DataFrame) -> pd.DataFrame:
    """Function to calculate per capita data for emissions and gdp for each year

    :param data: Dataframe with all the necessary data without per capita columns
    :type data: pd.DataFrame
    :return: DataFrame with added per capita columns
    :rtype: pd.DataFrame
    """
    data['Total per capita'] = data.apply(
        lambda row: row["Total"] / row["Population"], axis=1)
    data['Total including bunker'] = data.apply(
        lambda row: row["Total"] + row["Bunker fuels (Not in Total)"], axis=1)
    data['Total and bunker per capita'] = data.apply(
        lambda row: row['Total including bunker'] / row["Population"], axis=1)
    data['GDP per capita'] = data.apply(
        lambda row: row['GDP'] / row["Population"], axis=1)
    return data


def create_multiindex(column_names: list) -> pd.MultiIndex:
    """Function which creates new pandas MultiIndex with
    5 main groups (one for each country) and len(column names)
    columns in each of them

    :param column_names: names of columns
    :type column_names: list
    :return: Multiindex for new dataFrame
    :rtype: pd.MultiIndex
    """
    array = list(itertools.chain.from_iterable(
        [len(column_names) * [f"Country {index + 1}"] for index in range(5)])
    ), 5 * column_names
    multi_index = pd.MultiIndex.from_arrays(array, names=['Country', 'Data'])
    return multi_index

# "Country" : "Country Name", "Total emission" : "Total", "Emission per capita" : "Total per capita"


def find_5_highest(data_processed: pd.DataFrame, column_names: dict, sort_by: str) -> pd.DataFrame:
    """Function which based on one dataframe creates a new one
    with 5 countries for each year which have the highest values
    of one column passed as argument

    :param data_processed: Processed pandas DataFrame with per capita data
    :type data_processed: pd.DataFrame
    :param column_names: Names of new and old columns which will be used
    :type column_names: dict
    :param sort_by: Name of column based on which data will be sorted and
    only 5 highest values will be used
    :type sort_by: str
    :rtype: pd.DataFrame
    """
    years = set(data_processed["Year"])
    # Create empty dataFrame which will store results
    highest_values = pd.DataFrame(
        columns=create_multiindex(list(column_names.keys())), index=pd.Index(years))
    for year in years:
        # Select countries with highest values per capita for each year
        year_data = data_processed[data_processed["Year"] == year]
        largest = year_data[sort_by].nlargest(5)
        # Fill new table with highest values
        for index, index_val in enumerate(largest.index):
            group_name = highest_values.columns.levels[0][index] # type: ignore
            for key, value in column_names.items():
                new_value = data_processed.loc[index_val][value]
                if not isinstance(new_value, str):
                    new_value = new_value.round(5)
                highest_values.loc[year][group_name, key] = new_value
    return highest_values


def find_co2_changes(data_processed: pd.DataFrame)-> Union[tuple[pd.DataFrame, List[int]],
                                                           tuple[None, None]]:
    """Function which analyzes the data and looks for countries with biggest decrease
    and growth in CO2 emission in the last 10 (or less) years

    :param data_processed: Processed pandas DataFrame
    :type data_processed: pd.DataFrame
    :return: Dataframe with the name of the countries and list of years which had been analyzed
    :rtype: Union[tuple[pd.DataFrame, List[int]], tuple[None, None]]
    """
    years = set(data_processed["Year"])
    if len(years) == 1:
        print("Only one year provided. No changes can be calculated")
        return None, None
    # Choose the last 10 years or the maximum number of years that there is data for
    if len(years) < 10:
        print(
            "There is not enough data to calculate the change in the last 10 years. " \
                f"Will use provided {len(years)} years instead.")
        years_subset = list(years)
    else:
        years_subset = list(years)[-10:]
    max_change, min_change = 0, 0
    max_country, min_country = [], []
    # Iterate through all of the countries
    for country in set(data_processed["Country Name"]):
        # Choose the rows about the country and two concerning years
        rows = data_processed[(data_processed["Country Name"] == country) &
                              (data_processed["Year"].isin(years_subset[::len(years_subset)-1]))]
        # Make sure that there is data from both of the concerning years
        if len(rows) == 2:
            difference = rows["Total and bunker per capita"].diff().values[-1]
            # Use lists to allow for the possibility that two countries
            # have exactly the same change in emission per capita
            if difference and difference <= min_change:
                if difference == min_change:
                    min_country.append(country)
                else:
                    min_country = [country]
                    min_change = difference
            elif difference and difference >= max_change:
                if difference == max_change:
                    max_country.append(country)
                else:
                    max_country = [country]
                    max_change = difference
    changes = pd.DataFrame({"Growth in emission": ', '.join(max_country),
                            "Growth": [max_change],
                            "Decrease in emission": ', '.join(min_country),
                            "Decrease": [min_change]},
                           index=[1])
    return changes,  years_subset[::len(years_subset)-1]


def save_results(filename: str, data_list: List[Union[pd.DataFrame, None]], title_list: List[str]):
    """Function which saves Dataframe's to one csv file

    :param filename: Name of the output csv file
    :type filename: str
    :param data_list: List of Dataframe's which will be written to the file
    :type data_list: List[pd.DataFrame]
    :param title_list: List of Titles of the corresponding dataframe's
    :type title_list: List[str]
    """
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'a', encoding='UTF-8', newline='') as file:
        for title, dataframe in zip(title_list, data_list):
            if title and dataframe is not None:
                file.write(title)
                dataframe.to_csv(file, float_format='%.5f')
                file.write("\n")
