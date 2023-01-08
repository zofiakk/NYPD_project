import argparse
import sys
import analyze_data
import read_data


def main():
    parser = argparse.ArgumentParser(prog='NYPD final project 2022/23',
                                     description='Program to analyze gdp, populations and co2 emission data',
                                     epilog="Zofia Kochanska, zk406116@students.mimuw.edu.pl")
    parser.add_argument('-gdp', '--gdp_file', action='store', dest='gdp',
                        help='Name of the file with gdp data in csv format', required=True)
    parser.add_argument('-pop', '--populations_file', action='store', dest='populations',
                        help='Name of the file with populations data in csv format', required=True)
    parser.add_argument('-co2', '--co2_file', action='store', dest='co2',
                        help='Name of the input file with the message in csv format', required=True)
    parser.add_argument('-y1', '--start_year', action='store', dest='y1', type=int,
                        help='')
    parser.add_argument('-y2', '--end_year', action='store',
                        dest='y2', type=int, help='')
    args = parser.parse_args()

    if not args.co2.endswith(".csv") \
            or not args.gdp.endswith(".csv") \
            or not args.populations.endswith(".csv"):
        print("Error, all of the input files need to be in csv format (see help; -h).")
        sys.exit(-1)

    if args.y1 and args.y2:
        if args.y1 >= args.y2:
            print("Error value for y1 variable needs to be smaller than y2 variable")
            sys.exit(-1)

    co2 = read_data.read_file_to_df(args.co2, skip=False)
    populations = read_data.read_file_to_df(args.populations)
    gdp = read_data.read_file_to_df(args.gdp)


    gdp_subset, populations_subset, co2_subset, common_years = read_data.check_data(
        gdp, populations, co2, [args.y1, args.y2])

    joined_data = read_data.join_data(gdp_subset, populations_subset, co2_subset, common_years)
    
    data_processed = analyze_data.get_per_capita(joined_data)
    # Emission
    analyze_data.find_5_highest(data_processed=data_processed,
                                       column_names={"Country" : "Country Name",
                                                     "Total emission" : "Total",
                                                     "Emission per capita" : "Total per capita"},
                                       sort_by="Total per capita")
    # GDP
    analyze_data.find_5_highest(data_processed=data_processed,
                                       column_names={"Country" : "Country Name",
                                                     "GDP" : "GDP",
                                                     "GDP per capita" : "GDP per capita"},
                                       sort_by="GDP per capita")
    
    analyze_data.find_co2_changes(data_processed=data_processed)


if __name__ == '__main__':
    main()
