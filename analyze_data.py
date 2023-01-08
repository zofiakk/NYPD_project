import itertools
import pandas as pd
from tabulate import tabulate


def get_per_capita(data: pd.DataFrame) -> pd.DataFrame:
    """Function to calculate per capita data for emissions and gdp for each year

    :param data: Dataframe with all the necessary data without per capita columns
    :type data: pd.DataFrame
    :return: DataFrame with added per capita columns
    :rtype: pd.DataFrame
    """
    # nan/x -> nan

    data['Total per capita'] = data.apply(
        lambda row: row["Total"] / row["Population"], axis=1)
    data['Total and bunker per capita'] = data.apply(
        lambda row: (row["Total"] + row["Bunker fuels (Not in Total)"]) / row["Population"], axis=1)
    data['GDP per capita'] = data.apply(
        lambda row: row['GDP'] / row["Population"], axis=1)
    print(tabulate(data, headers='keys', tablefmt='psql'))
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


def find_5_highest(data_processed: pd.DataFrame, column_names: dict, sort_by: str):
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
    """
    years = set(data_processed["Year"])
    # Create empty dataFrame which will store results
    highest_values = pd.DataFrame(
        columns=create_multiindex(list(column_names.keys())), index=years)
    highest_values.index.names = ['Year']
    print(highest_values)
    for year in years:
        # Select countries with highest values per capita for each year
        year_data = data_processed[data_processed["Year"] == year]
        largest = year_data[sort_by].nlargest(5)

        # Fill new table with highest values
        for index, index_val in enumerate(largest.index):
            group_name = highest_values.columns.levels[0][index]
            for key, value in column_names.items():
                new_value = data_processed.loc[index_val][value]
                highest_values.loc[year][group_name, key] = new_value
    # print(highest_emission.to_markdown())
    h = [highest_values.index.names[0] + '/' + highest_values.columns.names[0]
         ] + list(map('\n'.join, highest_values.columns.tolist()))
    print(tabulate(highest_values, headers=h, tablefmt='psql'))


def find_co2_changes(data_processed: pd.DataFrame):
    years = set(data_processed["Year"])
    # Choose the last 10 years or the maximum number of years that there is data for
    if len(years) < 10:
        print(
            f"There is not enough data to calculate the change in the last 10 years. \
                Will use provided {len(years)} years instead.")
        years_subset = list(years)
    else:
        years_subset = list(years)[-10:]
    print(years_subset, years_subset[::len(years_subset)-1])
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
            if difference <= min_change:
                if difference == min_change:
                    min_country.append(country)
                else:
                    min_country = [country]
                    min_change = difference
            elif difference >= max_change:
                if difference == max_change:
                    max_country.append(country)
                else:
                    max_country = [country]
                    max_change = difference
            # diff = sec- fir (>0 = bigger usage)
    print(min_country, min_change,  max_country, max_change)
