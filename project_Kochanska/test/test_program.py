"""Test program

This script contains tests for checking the program which analyzes the
emission, gdp and population data.

This file contains 9 test
"""
import csv
import os
import pytest
import pandas as pd
import numpy as np
import project_Kochanska.read_data as read_data
import project_Kochanska.analyze_data as analyze_data


def write_file(file_name: str, header: bool, empty: bool = False) -> str:
    """Function which writes data to csv files used in testing reading them

    :param file_name: Name of new file
    :type file_name: str
    :param header: Whether the header lines should be included
    :type header: bool
    :param empty: Whether the file should be empty, defaults to False
    :type empty: bool, optional
    :return: Name of the output file
    :rtype: str
    """
    # If the header should be included
    if header:
        header_lines = [["skip"], ["skip"], ["Country Name", "Country Code", "Indicator Name",
                                             "Indicator Code", "2003", "2004"]]
        data = [["Aruba", "ABW", "GDP (current US$)", "NY.GDP.MKTP.CD", "1", "1"],
                ["Africa", "AFE", "GDP (current US$)", "NY.GDP.MKTP.CD", "1", "1"],
                ["Afghanistan", "AFG", "GDP (current US$)", "NY.GDP.MKTP.CD", "1", "1"]]
    else:
        header_lines = ["Year", "Country", "Total", "Solid Fuel", "Liquid Fuel",
                        "Gas Fuel", "Cement", "Gas Flaring", "Per Capita",
                        "Bunker fuels (Not in Total)"]
        data = [[2013, "SPAIN", 1, 1, 1, 1, 1, 0, 1.39, 1],
                [2014, "SPAIN", 1, 1, 1, 1, 1, 0, 1.38, 1]]
    # If the file should be empty
    if empty:
        header_lines = []
        data = []
    # Write the lines to csv file
    with open(file_name, 'w', encoding='UTF-8', newline='') as file:
        writer = csv.writer(file)
        if header:
            writer.writerows(header_lines)
        else:
            writer.writerow(header_lines)
        writer.writerows(data)
    return file_name

# Create Dataframe's used in testing
emission_df = pd.DataFrame(np.array([[1999, 'UNITED KINGDOM', 2552, 2552, 0, 0, 0, 0, 0.0, 0],
                                     [1000, 'UNITED KINGDOM', 2553, 2553, 0, 0, 0, 0, 0.0, 0],
                                     [2013, "SPAIN", 1, 1, 35077, 16341, 1868, 0, 1.39, 9324],
                                     [2014, "SPAIN", 1, 1, 35189, 14781, 1984, 0, 1.38, 9892]]),
                           columns=['Year', 'Country Name', 'Total', 'Solid Fuel', 'Liquid Fuel',
                                    'Gas Fuel', 'Cement', 'Gas Flaring', 'Per Capita',
                                    'Bunker fuels (Not in Total)'])
emission_df['Year'] = emission_df['Year'].astype('int')

gdp_df = pd.DataFrame(np.array([["Aruba", "ABW", "GDP (current US$)", "NY.GDP.MKTP.CD", "", ""],
                                ["Africa ", "AFE", "GDP (current US$)", "NY.GDP.MKTP.CD", "1", "1"],
                                ["Afghanistan", "AFG", "GDP", "NY.GDP.MKTP.CD", "1","1"]]),
                      columns=["Country Name", "Country Code", "Indicator Name", "Indicator Code",
                               2013, 2014])

pop_df = pd.DataFrame(np.array([["Aruba", "ABW", "Population, total", "SP.POP.TOTL", "1", "1"],
                                ["Afghanistan", "AFG", "Population", "SP.POP.TOTL", "1", "1"]]),
                      columns=["Country Name", "Country Code", "Indicator Name", "Indicator Code",
                               2013, 2014])

joined_df = pd.DataFrame(np.array([[2013, "A", 10, 0, 0, 0, 0, 0, 1, 0, 100, 10],
                                   [2013, "B", 10, 0, 0, 0, 0, 0, 1, 0, 100, 10]]),
                         columns=['Year', 'Country Name', 'Total', 'Solid Fuel', 'Liquid Fuel',
                                  'Gas Fuel', 'Cement', 'Gas Flaring', 'Per Capita',
                                  'Bunker fuels (Not in Total)', 'GDP', 'Population'])
joined_df.loc[:, joined_df.columns != 'Country Name'] = \
    joined_df.loc[:, joined_df.columns != 'Country Name'].astype('int')


per_capita_df = pd.DataFrame(np.array([[2013, "A", 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 1000, 1000],
                                       [2013, "B", 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 100, 1000],
                                       [2013, "C", 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 100, 100],
                                       [2013, "D", 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 100, 100],
                                       [2013, "E", 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 10, 10],
                                       [2013, "F", 10, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 1, 1],
                                       [2013, "G", 10, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 1, 1],
                                       [2014, "A", 10, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 100, 1],
                                       [2014, "B", 10, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 100, 10000, 1]
                                       ]),
                         columns=['Year', 'Country Name', 'Total', 'Solid Fuel', 'Liquid Fuel',
                                  'Gas Fuel', 'Cement', 'Gas Flaring', 'Per Capita',
                                  'Bunker fuels (Not in Total)', 'GDP', 'Population',
                                  'Total per capita', 'Total including bunker',
                                  'Total and bunker per capita', 'GDP per capita'])
per_capita_df['Year'] = pd.to_numeric(per_capita_df['Year'], errors='coerce')
per_capita_df['GDP per capita'] = pd.to_numeric(per_capita_df['GDP per capita'], errors='coerce')
per_capita_df['Total and bunker per capita'] = pd.to_numeric(
    per_capita_df['Total and bunker per capita'], errors='coerce')


def test_read_file_to_df():
    """Function which tests if program correctly reads
    csv files and identifies their potential problems
    """
    # Check if program raises errors for non-existent files
    if not os.path.isfile("non_existent_file"):
        with pytest.raises(SystemExit) as exit_info:
            read_data.read_file_to_df("non_existent_file")
        assert exit_info.value.code == -1

    # Check if program raises errors for empty files
    if not os.path.isfile("empty_file"):
        with pytest.raises(SystemExit) as exit_info:
            read_data.read_file_to_df(write_file(
                "empty_file", False, empty=True,))
            os.remove("empty_file")
            assert exit_info.value.code == -1
        os.remove("empty_file")

    # Check if program raises errors for files in wrong format
    with pytest.raises(SystemExit) as exit_info:
        read_data.read_file_to_df("read_data.py")
        assert exit_info.value.code == -1

    # Check if program correctly reads files with no headers
    emission = read_data.read_file_to_df(
        write_file("test_emission.csv", False), skip=False)
    os.remove("test_emission.csv")
    assert isinstance(emission, pd.DataFrame)
    assert emission.shape == (2, 10)

    # Check if program correctly reads files with headers
    gdp = read_data.read_file_to_df(write_file(
        "test_gdp.csv", header=True, empty=False))
    os.remove("test_gdp.csv")
    assert isinstance(gdp, pd.DataFrame)
    assert gdp.shape == (3, 5)


def test_select_years():
    """Function which checks is program correctly selects data
    from common years and if the restrictions are present uses them
    """
    # Check for years which result in no data
    with pytest.raises(SystemExit) as exit_info:
        read_data.select_years(gdp_df, pop_df, emission_df, years=[1800, 1801])
        assert exit_info.value.code == -1
    # Check if program acts correctly when no years are provided
    assert read_data.select_years(gdp_df, pop_df, emission_df,
                                  years=[None, None])[3] == [2013, 2014]
    assert read_data.select_years(gdp_df, pop_df, emission_df,
                                  years=[None, None])[2]["Year"].to_list() == [2013, 2014]
    # Check if program acts correctly when years are provided
    assert read_data.select_years(gdp_df, pop_df, emission_df,
                                  years=[2013, 2013])[3] == [2013]
    assert read_data.select_years(gdp_df, pop_df, emission_df,
                                  years=[2013, 2013])[2]["Year"].to_list() == [2013]


def test_join_same_countries():
    """Tests if function correctly merges the rows
    with data the same year and country to avoid duplicates
    """
    # Check if function works for the co2 data
    co2_df_duplicate = pd.concat([emission_df]*2, ignore_index=True)
    assert read_data.join_same_countries(
        co2_df_duplicate, data_type=1).shape == emission_df.shape
    # Check if function works for other types of data
    pop_df_duplicate = pd.concat([pop_df]*2, ignore_index=True)
    assert read_data.join_same_countries(
        pop_df_duplicate, data_type=0).shape == pop_df.shape


def test_check_countries():
    """Tests if function correctly changes countries
    names to allow for a better joining of dataframe's
    """
    gdp_changed, pop_changed, co2_changed = read_data.check_countries(
        gdp_df, pop_df, emission_df, {"Aruba": "Aruba new", "SPAIN": "SPAIN NEW"})
    assert "Aruba new" in gdp_changed["Country Name"].to_list()
    assert "Aruba new" in pop_changed["Country Name"].to_list()
    assert "SPAIN NEW" in co2_changed["Country Name"].to_list()


def test_join_data():
    """Checks if program correctly joins 3 dataframe's
    """
    joined_data = read_data.join_data(
        gdp_df, pop_df, emission_df, [2013, 2014])
    assert list(joined_data.columns) == ['Year', 'Country Name', 'Total', 'Solid Fuel',
                                         'Liquid Fuel', 'Gas Fuel', 'Cement', 'Gas Flaring',
                                         'Per Capita', 'Bunker fuels (Not in Total)', 'GDP',
                                         'Population']


def test_get_per_capita():
    """Check if program adds columns with per capita values
    """
    per_capita_data = analyze_data.get_per_capita(joined_df)
    assert len(list(per_capita_data.columns)) == 16
    assert per_capita_data["GDP per capita"].to_list() == [10.0, 10.0]
    assert per_capita_data['Total and bunker per capita'].to_list() == [1.0, 1.0]


def test_create_multiindex():
    """Check if function correctly creates pandas Multiindex
    """
    assert isinstance(analyze_data.create_multiindex(["Test"]), pd.MultiIndex)
    assert len(analyze_data.create_multiindex(["Test"]).levels[0]) == 5


def test_find_5_highest():
    """Check if program correctly identifies countries
    with highest co2 emission and gdp per capita
    """
    # Check if function correctly identifies countries with highest gdp per capita
    highest_gdp = analyze_data.find_5_highest(per_capita_df,
                                              column_names={"Country": "Country Name",
                                                            "GDP": "GDP",
                                                            "GDP per capita": "GDP per capita"},
                                              sort_by="GDP per capita")
    assert highest_gdp.iloc[0].to_list() == ['A', '0', 1000, 'B', '0', 1000, 'C', '0', 100, 'D',
                                             '0', 100, 'E', '0', 10]

    # Check if function correctly identifies countries with highest co2 emission per capita
    highest_co2 = analyze_data.find_5_highest(per_capita_df,
                                              column_names={"Country": "Country Name",
                                                         "Total emission": "Total including bunker",
                                                         "Emission per capita":
                                                             'Total and bunker per capita'},
                                              sort_by='Total and bunker per capita')
    assert highest_co2.iloc[0].to_list() == ['A', '10', 1000, 'B', '10', 100, 'C', '10', 100,
                                             'D', '10', 100, 'E', '10', 10]


def test_find_co2_changes():
    """Check if program correctly identifies countries with
    biggest increase and decrease in co2 emission
    """
    # Check if program correctly return None when only one year is included
    one_year = per_capita_df.drop(per_capita_df.tail(3).index)
    assert analyze_data.find_co2_changes(one_year) == (None, None)

    # Check if function correctly identifies countries
    result_df, _ = analyze_data.find_co2_changes(per_capita_df)
    assert result_df.iloc[0].to_list() == ['B', 9900.0, 'A', -900.0]

    # Check if program correctly identifies multiple same changes in emission
    per_capita_df.loc[len(per_capita_df)] = [2014,  # type: ignore
                                             "C", 10, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 100, 10000, 1]
    result_double_df = analyze_data.find_co2_changes(per_capita_df)[0]
    assert result_double_df.iloc[0].to_list() in [['C, B', 9900.0, 'A', -900.0],
                                                  ['B, C', 9900.0, 'A', -900.0]]
    