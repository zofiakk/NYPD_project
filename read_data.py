"""Read data

This script is used to read and clean provided files. As a result it
returns one joined dataframe with all of the information.

This file contains the following functions:

    * read_file_to_df - returns pandas Dataframe
    * select_years - returns Dataframe's filtered to contain only some years
    * join_same_countries- return Dataframe's with merged rows when their
    content pertains the same year and country
    * check_countries - returns Dataframe's with modified country names
    * check_data - returns cleaned up Dataframe's
    * join_data - returns joined Dataframe with all of the information
"""
import sys
from typing import Any
import pandas as pd


def read_file_to_df(file_path: str, skip: bool = True) -> pd.DataFrame:
    """Function to read csv files to pandas DataFrames

    :param file_path: Path to csv input file
    :type file_path: str
    :param skip: Weather to skip first two non-empty lines (header), defaults to True
    :type skip: bool, optional
    :return: Dataframe with loaded data
    :rtype: pd.DataFrame
    """
    try:
        # Files with header lines
        if skip:
            data_frame = pd.read_csv(file_path, header=2, sep=",")
            data_frame = data_frame.iloc[:, :-1]
            year = list(data_frame.columns)
            year[4:] = list(map(int, year[4:]))  # type: ignore
            data_frame.columns = pd.Index(year)
        # Files with no header
        else:
            data_frame = pd.read_csv(file_path, sep=",")
            data_frame = data_frame.rename(columns={"Country": "Country Name"})
    except FileNotFoundError:
        print("File not found.")
        sys.exit(-1)
    except pd.errors.EmptyDataError:
        print("No data")
        sys.exit(-1)
    except pd.errors.ParserError:
        print("Parser error")
        sys.exit(-1)
    return data_frame


def select_years(gdp: pd.DataFrame, populations: pd.DataFrame, co2: pd.DataFrame,
                 years: list) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list]:
    """Function which looks for the chosen years in all of the dataframe's
    and subsets them to only data derived from them

    :param gdp: DataFrame with gdp information
    :type gdp: pd.DataFrame
    :param populations: DataFrame with population information
    :type populations: pd.DataFrame
    :param co2: DataFrame with emission information
    :type co2: pd.DataFrame
    :param years: Years to be chosen, if None provided all common years will be chosen
    :type years: list
    :return: Subsets of the provided dataframe's and list of used years
    :rtype: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list]
    """
    # Get list of all of the common years and sort it
    common_years = list(set(gdp.columns[4:]).intersection(
        co2["Year"], populations.columns[4:]))
    if len(common_years) == 0:
        print("Error, provided files have no common years")
        sys.exit(-1)
    # Select boundary years if they are not provided
    if years[0] is None:
        years[0] = min(common_years)  # type: ignore
    if years[1] is None:
        years[1] = max(common_years)  # type: ignore
    # Create the list of years which will be used
    chosen_years = [year for year in common_years
                    if year >= years[0] and year <= years[1]] # type: ignore
    if len(chosen_years) == 0:
        print("Error, provided files have no data for chosen years")
        sys.exit(-1)
    # Subset the dataframe's
    gdp_subset = gdp[['Country Name']+chosen_years]
    populations_subset = populations[['Country Name']+chosen_years]
    co2_subset = co2[co2["Year"].isin(chosen_years)]
    return gdp_subset, populations_subset, co2_subset, chosen_years


def join_same_countries(data: pd.DataFrame, data_type: int) -> pd.DataFrame:
    """Function which merges rows with data about the same
    country and the same year

    :param data: Dataframe with many rows about one country
    :type data: pd.DataFrame
    :param data_type: Which type of data is being merged (co2=1 or others)
    :type data_type: int
    :return: Dataframe with merged rows
    :rtype: pd.DataFrame
    """
    # For co2 data
    if data_type == 1:
        aggregate_function: dict[Any, str] = {
            "Country Name": 'first', "Year": 'first'}
        for i in list(data.columns):
            if i not in ["Country Name", "Year"]:
                aggregate_function[i] = 'sum'
        new_data = data.groupby(['Year', 'Country Name'], as_index=False).aggregate(
            aggregate_function).reindex(columns=data.columns)
    # For other data types
    else:
        aggregate_function = {"Country Name": 'first'}
        for i in list(data.columns):
            if i != "Country Name":
                aggregate_function[i] = 'sum'
        new_data = data.groupby(['Country Name'], as_index=False).aggregate(
            aggregate_function).reindex(columns=data.columns)
    return new_data


def check_countries(gdp_subset: pd.DataFrame, populations_subset: pd.DataFrame,
                    co2_subset: pd.DataFrame, countries_dict: dict) -> tuple[
                        pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Function which changes the country names to allow for better
    merging of the dataframe's and makes sure that there is only one
    row for each country and year after the modifications

    :param gdp_subset: Dataframe with gdp information
    :type gdp_subset: pd.DataFrame
    :param populations_subset: Dataframe with population information
    :type populations_subset: pd.DataFrame
    :param co2_subset: Dataframe with emission information
    :type co2_subset: pd.DataFrame
    :param countries_dict: Dictionary with incorrect country names
    stored as keys and their correct counterparts stored as values
    :type countries_dict: dict
    :return: Dataframe's with changed 'country names' columns
    :rtype: tuple[ pd.DataFrame, pd.DataFrame, pd.DataFrame]
    """
    # Change country names according to the provided dictionary
    co2_subset = co2_subset.replace(
        list(countries_dict.keys()), list(countries_dict.values()))  # type: ignore
    populations_subset = populations_subset.replace(
        list(countries_dict.keys()), list(countries_dict.values()))  # type: ignore
    gdp_subset = gdp_subset.replace(
        list(countries_dict.keys()), list(countries_dict.values()))  # type: ignore

    if gdp_subset is None or co2_subset is None or populations_subset is None:
        print("Error, provided files have no common countries")
        sys.exit(-1)
    # Merge data about the same countries
    co2_subset = join_same_countries(co2_subset, data_type=1)
    populations_subset = join_same_countries(populations_subset, data_type=0)
    gdp_subset = join_same_countries(gdp_subset, data_type=0)
    return gdp_subset, populations_subset, co2_subset


def check_data(gdp: pd.DataFrame, populations: pd.DataFrame, co2: pd.DataFrame,
               years: list) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list]:
    """Function which joins the 'cleaning data' part of the program

    :param gdp: Dataframe with gdp information
    :type gdp: pd.DataFrame
    :param populations: Dataframe with populations information
    :type populations: pd.DataFrame
    :param co2: Dataframe with emissions information
    :type co2: pd.DataFrame
    :param years: years which will be chosen
    :type years: list
    :return: Cleaned dataframe's and list of used years
    :rtype: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list]
    """
    countries_dict = {"Korea, Dem. People's Rep.": "DEMOCRATIC PEOPLE S REPUBLIC OF KOREA",
                      "Korea, Rep.": 'REPUBLIC OF KOREA',
                      "Vietnam": "VIET NAM",
                      "Czechia": "CZECH REPUBLIC",
                      "United States": "UNITED STATES OF AMERICA",
                      "Cameroon": "REPUBLIC OF CAMEROON",
                      "Slovak Republic": "SLOVAKIA",
                      "Bosnia and Herzegovina": 'BOSNIA & HERZEGOVINA',
                      "Venezuela, RB": 'VENEZUELA',
                      "Egypt, Arab Rep.": 'EGYPT',
                      "Lao PDR": 'LAO PEOPLE S DEMOCRATIC REPUBLIC',
                      "Bahamas, The": 'BAHAMAS',
                      "Hong Kong SAR, China": "HONG KONG SPECIAL ADMINSTRATIVE REGION OF CHINA",
                      "Macao SAR, China": "MACAU SPECIAL ADMINSTRATIVE REGION OF CHINA",
                      "Congo, Dem. Rep.": "DEMOCRATIC REPUBLIC OF THE CONGO (FORMERLY ZAIRE)",
                      "Congo, Rep.": "CONGO",
                      "China": 'CHINA',
                      "Tanzania": 'UNITED REPUBLIC OF TANZANIA',
                      "Gambia, The": "GAMBIA",
                      "Timor-Leste": 'TIMOR-LESTE (FORMERLY EAST TIMOR)',
                      "Kyrgyz Republic": 'KYRGYZSTAN',
                      "Bolivia": 'PLURINATIONAL STATE OF BOLIVIA',
                      "South Sudan": 'REPUBLIC OF SOUTH SUDAN',
                      "Sudan": 'SUDAN',
                      "Sao Tome and Principe": 'SAO TOME & PRINCIPE',
                      "Yemen, Rep.": "YEMEN",
                      "St. Lucia": 'SAINT LUCIA',
                      "Turkiye": "TURKEY",
                      "St. Kitts and Nevis": 'ST. KITTS-NEVIS',
                      "Myanmar": 'MYANMAR (FORMERLY BURMA)',
                      "Guinea-Bissau": 'GUINEA BISSAU',
                      "Iran, Islamic Rep.": 'ISLAMIC REPUBLIC OF IRAN',
                      "Cote d'Ivoire": 'COTE D IVOIRE',
                      "Brunei Darussalam": 'BRUNEI (DARUSSALAM)',
                      "St. Vincent and the Grenadines": 'ST. VINCENT & THE GRENADINES',
                      "Micronesia, Fed. Sts.": 'FEDERATED STATES OF MICRONESIA',
                      "Moldova": 'REPUBLIC OF MOLDOVA',
                      "Antigua and Barbuda": 'ANTIGUA & BARBUDA',
                      "Sint Maarten (Dutch part)": 'SAINT MARTIN (DUTCH PORTION)',
                      "Cabo Verde": 'CAPE VERDE',
                      "Faroe Islands": 'FAEROE ISLANDS',
                      "Eswatini": 'SWAZILAND',
                      "Palau": 'PACIFIC ISLANDS (PALAU)',
                      "Monaco": "France",
                      "San Marino": "Italy",
                      "REPUBLIC OF SUDAN": "SUDAN",
                      "TAIWAN": "CHINA",
                      "CHINA (MAINLAND)": "CHINA",
                      'FRANCE (INCLUDING MONACO)': "FRANCE",
                      'ITALY (INCLUDING SAN MARINO)': "ITALY"}
    # Subset correct years from dataframe's
    gdp_subset, populations_subset, co2_subset, common_years = select_years(
        gdp, populations, co2, years)
    # Change countries names to allow for a better merging of dataframe's
    gdp_subset, populations_subset, co2_subset = check_countries(
        gdp_subset, populations_subset, co2_subset, countries_dict=countries_dict)
    # Change country names
    gdp_subset['Country Name'] = gdp_subset['Country Name'].str.upper()
    populations_subset['Country Name'] = populations_subset['Country Name'].str.upper()
    # Look for countries not found in other files
    gdp_countries = set(gdp_subset["Country Name"].to_list())
    pop_countries = set(populations_subset["Country Name"].to_list())
    co2_countries = set(co2_subset["Country Name"].to_list())

    odd_countries = (gdp_countries | pop_countries |
                     co2_countries) - (gdp_countries & pop_countries & co2_countries)
    if len(odd_countries) > 0:
        print(f"{len(odd_countries)} countries have not been found in all of the files. "
              "They will be excluded from the analysis.")
    return gdp_subset, populations_subset, co2_subset, common_years


def join_data(gdp_subset: pd.DataFrame, populations_subset: pd.DataFrame,
              co2_subset: pd.DataFrame, years: list) -> pd.DataFrame:
    """Function which merges provided dataframe's into one

    :param gdp_subset: Dataframe with gdp information
    :type gdp_subset: pd.DataFrame
    :param populations_subset: Dataframe with population information
    :type populations_subset: pd.DataFrame
    :param co2_subset: Dataframe with emissions information
    :type co2_subset: pd.DataFrame
    :param years: Years for which data is provided
    :type years: list
    :return: Merged dataframe with all of the data
    :rtype: pd.DataFrame
    """
    # Change populations and gdp data shape
    gdp_subset_melt = pd.melt(gdp_subset, id_vars=['Country Name'],
                              value_vars=years,
                              var_name='Year', value_name='GDP')
    populations_subset_melt = pd.melt(populations_subset, id_vars=['Country Name'],
                                      value_vars=years,
                                      var_name='Year', value_name='Population')
    # Merge populations and gdp dataframe's
    gdp_population = pd.merge(gdp_subset_melt, populations_subset_melt,
                              on=["Country Name", "Year"])
    # Merge all of the dataframe's together
    joined_data = pd.merge(co2_subset, gdp_population,
                           on=["Country Name", "Year"])
    joined_data['Population'].replace(
        to_replace=0, value=float('nan'), inplace=True)
    return joined_data
