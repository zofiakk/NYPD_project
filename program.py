"""Program

This script analyzes the data in the provided files and returns the results
of them in the form of joined csv file.

This script requires that `pandas` be installed within the Python
environment this script is being used in.

This file can also be imported as a module and contains one function:
    * main - the main function of the script which calls other modules

"""
import argparse
import sys
import analyze_data
import read_data


def main():
    """Function which joins all parts of the analysis
    of the emission, gdp and population data.
    It starts with accepting command line arguments
    and ends with saving obtained results to a csv file
    """
    parser = argparse.ArgumentParser(prog='NYPD final project 2022/23',
                                     description='Program to analyze gdp, '\
                                         'population and co2 emission data',
                                     epilog="Zofia Kochanska, zk406116@students.mimuw.edu.pl")
    parser.add_argument('-gdp', '--gdp_file', action='store', dest='gdp',
                        help='Name of the file with gdp data in csv format', required=True)
    parser.add_argument('-pop', '--populations_file', action='store', dest='populations',
                        help='Name of the file with population data in csv format', required=True)
    parser.add_argument('-co2', '--co2_file', action='store', dest='co2',
                        help='Name of the input file with the message in csv format', required=True)
    parser.add_argument('-y1', '--start_year', action='store', dest='y1', type=int,
                        help='Start of date range for the analysis. ' \
                            'If none provided first common year will be used')
    parser.add_argument('-y2', '--end_year', action='store', dest='y2', type=int,
                        help='End of date range for the analysis. '\
                            'If none provided last common year will be used')
    parser.add_argument('-f', '--output_file', dest='out', default='results.csv',
                        help='Name of output csv file to which results will be written. '\
                            'Defaults to "results.csv"')
    args = parser.parse_args()

    if not args.co2.endswith(".csv") \
            or not args.gdp.endswith(".csv") \
            or not args.populations.endswith(".csv"):
        print("Error, all of the input files need to be in csv format (see help; -h).")
        sys.exit(-1)

    if args.y1 and args.y2:
        if args.y1 > args.y2:
            print("Error value for y1 variable needs to be smaller than  or equal y2 variable")
            sys.exit(-1)
    if args.out:
        if args.out.count(".") != 1:
            args.out = args.out.split(".")[0] + ".csv"
            print(
                f"Output file name seems to be incorrect. It will be replaced with {args.out}")
        if not args.out.endswith(".csv"):
            args.out = args.out.split(".")[0] + ".csv"
            print(
                f"Name of output file needs to end with .csv. It will be replaced with {args.out}")

    # Read files to Dataframe's
    co2 = read_data.read_file_to_df(args.co2, skip=False)
    populations = read_data.read_file_to_df(args.populations)
    gdp = read_data.read_file_to_df(args.gdp)

    # Check given data
    gdp_subset, populations_subset, co2_subset, common_years = read_data.check_data(
        gdp, populations, co2, [args.y1, args.y2])

    # Join separate Dataframe's
    joined_data = read_data.join_data(
        gdp_subset, populations_subset, co2_subset, common_years)

    # Get per capita values
    data_processed = analyze_data.get_per_capita(joined_data)

    # Find countries with 5 highest values for:
    # Emission
    emission = analyze_data.find_5_highest(data_processed=data_processed,
                                           column_names={"Country": "Country Name",
                                                         "Total emission": "Total including bunker",
                                                         "Emission per capita":
                                                            'Total and bunker per capita'},
                                           sort_by='Total and bunker per capita' )
    # GDP
    gdp = analyze_data.find_5_highest(data_processed=data_processed,
                                      column_names={"Country": "Country Name",
                                                    "GDP": "GDP",
                                                    "GDP per capita": "GDP per capita"},
                                      sort_by="GDP per capita")

    # Identify countries with biggest changes in CO2 emission
    changes, years = analyze_data.find_co2_changes(data_processed=data_processed)

    if years is None:
        title= ""
    else:
        title = "Countries with biggest changes in CO2 emission between " \
            f"{years[0]} and {years[1]} \n"

    # Save Dataframe's to file
    analyze_data.save_results(args.out, [emission, gdp, changes],
                              ["5 countries with biggest CO2 emission per capita \n",
                                  "5 countries with highest gdp per capita \n",
                                  title])


if __name__ == '__main__':
    main()
