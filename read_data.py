import sys
import pandas as pd


def main():
    """_summary_
    """
    gdp_path = 'API_NY.GDP.MKTP.CD_DS2_en_csv_v2_4751562/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_4751562.csv'
    populations_path = "API_SP.POP.TOTL_DS2_en_csv_v2_4751604/API_SP.POP.TOTL_DS2_en_csv_v2_4751604.csv"
    co2_path = "co2-fossil-by-nation_zip/data/fossil-fuel-co2-emissions-by-nation_csv.csv"

    gdp = read_file_to_df(gdp_path)
    populations = read_file_to_df(populations_path)
    co2 = read_file_to_df(co2_path, skip=False)

    gdp, populations, co2, common_years = check_data(gdp, populations,
                                                     co2,  [1999, 2010])
    print(common_years)
    all_data = join_data(gdp, populations, co2, [1999, 2010])


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
            for index, _ in enumerate(year):
                if index >= 4:
                    year[index] = int(year[index])
            data_frame.columns = year
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
        print("Parse error")
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
    common_years.sort(key=int)
    # Select boundary years if they are not provided
    if years[0] is None:
        years[0] = min(common_years)
    if years[1] is None:
        years[1] = max(common_years)
    # Create the list of years which will be used
    chosen_years = [year for year in common_years
                    if int(year) >= years[0] and int(year) <= years[1]]
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
        aggregate_function = {"Country Name": 'first', "Year": 'first'}
        for i in list(data.columns):
            if i not in ["Country Name", "Year"]:
                aggregate_function[i] = 'sum'
        new_data = data.groupby(['Year', 'Country Name'], as_index=False).aggregate(
            aggregate_function).reindex(columns=data.columns)
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
    # Joined shape (795, 12) (1094, 10) (1330, 3) (1330, 3)
    # Change country names according to the provided dictionary
    co2_subset['Country Name'] = co2_subset['Country Name'].replace(
        list(countries_dict.keys()), list(countries_dict.values()))
    populations_subset['Country Name'] = populations_subset['Country Name'].replace(
        list(countries_dict.keys()), list(countries_dict.values()))
    gdp_subset['Country Name'] = gdp_subset['Country Name'].replace(
        list(countries_dict.keys()), list(countries_dict.values()))

    # Merge data about the same countries
    co2_subset = join_same_countries(co2_subset, data_type=1)
    populations_subset = join_same_countries(populations_subset, data_type=0)
    gdp_subset = join_same_countries(gdp_subset, data_type=0)
    
    gdp_countries = set(gdp_subset["Country Name"].str.upper())
    population_countries = set(
        populations_subset["Country Name"].str.upper())
    co2_countries = set(co2_subset["Country Name"])
    population_countries = list(population_countries)
    population_countries = [
        i for i in population_countries if "INCOME" not in i]
    population_countries = [i for i in population_countries if "ASIA" not in i]
    population_countries = [i for i in population_countries if "EURO" not in i]
    population_countries = [i for i in population_countries if "IDA" not in i]
    population_countries = [
        i for i in population_countries if "AFRICA" not in i]
    population_countries = [
        i for i in population_countries if "AMERICA" not in i]
    population_countries = [
        i for i in population_countries if "MEMBERS" not in i]
    population_countries = [
        i for i in population_countries if "DIVIDEND" not in i]
    population_countries = [
        i for i in population_countries if "DEVEL" not in i]
    population_countries = [
        i for i in population_countries if "DEBTED" not in i]

    not_in_co2 = []
    for i in population_countries:
        if i not in co2_countries:
            not_in_co2.append(i)
    print(not_in_co2, len(not_in_co2), len(
        population_countries), len(co2_countries))
    not_in_pop = []
    for i in co2_countries:
        if i not in population_countries:
            not_in_pop.append(i)
    print(not_in_pop, len(not_in_pop), len(
        population_countries), len(co2_countries))
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
    gdp_population['Country Name'] = gdp_population['Country Name'].str.upper()
    # Merge all of the dataframe's together
    joined_data = pd.merge(co2_subset, gdp_population,
                           on=["Country Name", "Year"])
    joined_data['Population'].replace(to_replace = 0, value = float('nan'), inplace=True)
    print("Joined shape", joined_data.shape, co2_subset.shape,
          gdp_subset_melt.shape, populations_subset_melt.shape)
    print(len(set(joined_data["Country Name"])))
    return joined_data


if __name__ == '__main__':
    main()
