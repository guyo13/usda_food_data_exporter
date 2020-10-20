#!/usr/bin/env python

# Copyright (c) 2020, Guy Or Please see the AUTHORS file for details.
# All rights reserved. Use of this source code is governed by a GNU GPL
# license that can be found in the LICENSE file.

import pandas as pd
import time
from os import getcwd, makedirs
from os.path import join as join_path
from os.path import exists, basename, dirname, isdir, abspath
from sys import exit

FOOD_DATASET_FILE = "food.csv"
FOOD_NUTRIENT_DATASET_FILE = "food_nutrient.csv"
NUTRIENT_FILE = "nutrient.csv"
BRANDED_FOOD_FILE = "branded_food.csv"

DEFAULT_FOOD_DATASET_PATH = join_path(getcwd(), FOOD_DATASET_FILE)
DEFAULT_FOOD_NUTRIENT_DATASET_PATH = join_path(getcwd(),FOOD_NUTRIENT_DATASET_FILE)
DEFAULT_NUTRIENT_PATH = join_path(getcwd(),NUTRIENT_FILE)
DEFAULT_BRANDED_PATH = join_path(getcwd(), BRANDED_FOOD_FILE)

DEFAULT_BRANDED_COLS = ["brand_owner", "ingredients", "market_country"]
DEFAULT_EXPORT_BASE_NAME = "exported_foods"
SUPPORTED_EXPORT_FILE_FORMATS = {"csv", "json", "excel", "sql", "pickle"}
FOOD_TYPES = {
              'agricultural_acquisition',
              'branded_food',
              'foundation_food',
              'sr_legacy_food',
              'sub_sample_food',
              'survey_fndds_food'
              }

def get_food_table(low_memory=False, usecols=None, path=DEFAULT_FOOD_DATASET_PATH):
    """ Returns a DataFrame with data from the USDA FoodData food.csv file-
        specified by path. Indexed by 'fdc_id' column.

        Params:
        low_memory Boolean (Default False) - DataFrame argument
        usecols Iterable<String> (Default None) - DataFrame argument, indicates the columns to keep.
                                                  If not None and 'fdc_id' not in it, will add 'fdc_id'
        path String (Default is food.csv file in CWD) - The path to the foods.csv file
    """
    if usecols is not None:
        if "fdc_id" not in usecols:
            usecols.append("fdc_id")
        return pd.read_csv(path, low_memory=low_memory, index_col="fdc_id", usecols=usecols)
    else:
        return pd.read_csv(path, low_memory=low_memory, index_col="fdc_id")

def get_nutrients_table(low_memory=False, usecols=None, path=DEFAULT_NUTRIENT_PATH):
    """ Returns a DataFrame with data from the USDA FoodData nutrient.csv file-
        specified by path. Indexed by 'id' column.

        Params:
        low_memory Boolean (Default False) - DataFrame argument
        usecols Iterable<String> (Default None) - DataFrame argument, indicates the columns to keep.
                                                  If not None and 'id' not in it, will add 'id'
        path String (Default is nutrient.csv file in CWD) - The path to the nutrient.csv file
    """
    if usecols is not None:
        if "id" not in usecols:
            usecols.append("id")
        return pd.read_csv(path, low_memory=low_memory, index_col="id", usecols=usecols)
    else:
        return pd.read_csv(path, low_memory=low_memory, index_col="id")

def get_nutri_data_table(low_memory=False, path=DEFAULT_FOOD_NUTRIENT_DATASET_PATH):
    """ Returns a DataFrame with data from the USDA FoodData food_nutrient.csv file-
        specified by path.

        Params:
        low_memory Boolean (Default False) - DataFrame argument
        path String (Default is food_nutrient.csv file in CWD) - The path to the food_nutrient.csv file
    """
    return pd.read_csv(path, low_memory=low_memory)

def get_branded_food_table(low_memory=False, path=DEFAULT_BRANDED_PATH, usecols=None):
    """ Returns a DataFrame with data from the USDA FoodData branded_food.csv file-
        specified by path. Indexed by 'fdc_id' column.

        Params:
        low_memory Boolean (Default False) - DataFrame argument
        usecols Iterable<String> (Default None) - DataFrame argument, indicates the columns to keep.
                                                  If not None and 'fdc_id' not in it, will add 'fdc_id'
        path String (Default is branded_food.csv file in CWD) - The path to the branded_food.csv file
    """
    if usecols is not None:
        if "fdc_id" not in usecols:
            usecols.append("fdc_id")
        return pd.read_csv(path, low_memory=low_memory, index_col="fdc_id", usecols=usecols)
    else:
        return pd.read_csv(path, low_memory=low_memory, index_col="fdc_id")

# Deprecated
def get_nutrient_names(nutrient_table=None, path=DEFAULT_NUTRIENT_PATH):
    """ Returns a list of nutrient names, based on the nutrient.csv file
        
        Params:
        nutrient_table DataFrame (Default None) - A DataFrame containing data from
                                                  nutrient.csv file, if None, will
                                                  create one based on path
        path String (Default is nutrient.csv file in CWD) - The path to the nutrient.csv file
    """
    nutrient_table = nutrient_table if isinstance(nutrient_table, pd.DataFrame) else get_nutrients_table(path=path) 
    res = nutrient_table["name"].to_list()
    return res

def get_nutrient_dict(nutrient_table=None, path=DEFAULT_NUTRIENT_PATH):  
    """ Returns a dict mapping of nutrient ids to names and measure unit,
        based on the nutrient.csv file
        
        Params:
        nutrient_table DataFrame (Default None) - A DataFrame containing data from
                                                  nutrient.csv file, if None, will
                                                  create one based on path
        path String (Default is nutrient.csv file in CWD) - The path to the nutrient.csv file
    """
    nutrient_table = nutrient_table if isinstance(nutrient_table, pd.DataFrame) else get_nutrients_table(usecols=["name", "unit_name"], path=path)
    return nutrient_table.to_dict(orient='index')



def get_foods_with_nutrient_data(
        food_db_path=DEFAULT_FOOD_DATASET_PATH,
        food_nutrient_db_path=DEFAULT_FOOD_NUTRIENT_DATASET_PATH,
        nutrient_table_path=DEFAULT_NUTRIENT_PATH,
        branded_food_table_path=DEFAULT_BRANDED_PATH,
        translate_nutrients=True,
        excluded_data_types=None,
        branded_food_data=False,
        branded_food_columns=DEFAULT_BRANDED_COLS,
        ):
    print("Reading food nutrient data...")
    food_nutrients = get_nutri_data_table(path=food_nutrient_db_path)
    food_nutrients.sort_values(
                           "fdc_id",
                           inplace=True,
                           ignore_index=True)

    food_nutrients = food_nutrients.pivot(
                                        index="fdc_id",
                                        columns="nutrient_id",
                                        values="amount")

    print("Reading food data...")
    foods = get_food_table(usecols=["description", "data_type", "publication_date"], path=food_db_path)
    if excluded_data_types != None:
        foods = foods[ ~foods["data_type"].isin(excluded_data_types) ]

    print("Processing...")
    final = pd.concat([foods, food_nutrients], axis=1, join='inner')
    if translate_nutrients:
        print("Translating nutrient ids to nutrient names")
        nutri_dict = get_nutrient_dict(path=nutrient_table_path)
        final.rename(inplace=True,
                     axis=1,
                     mapper= lambda x: nutri_dict[x]["name"] if isinstance(x, int) else x)
    if branded_food_data:
        print("Adding data from branded foods...")
        bfoods = get_branded_food_table(usecols=branded_food_columns, path=branded_food_table_path)
        final = pd.concat([final, bfoods], axis=1, join='outer')
    print("Finished Processing")
    return final

def export_files(df, export_file_name=DEFAULT_EXPORT_BASE_NAME, export_formats=[]):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df argument must be a pandas DataFrame!")
    if export_file_name is None:
        raise ValueError("export_file_name must be a valid path!")

    # Get Parent dir and conver to absolute path
    parent = abspath(dirname(export_file_name))
    # Create parent dir if necessary
    if not exists(parent):
        makedirs(parent)
    # Create absolute base path to be used below
    base_path = join_path(parent, basename(export_file_name))
    for fmt in export_formats:
        if fmt == "csv":
            filename = f'{base_path}.csv'
            print(f'Writing CSV to {filename}')
            df.to_csv(filename)
            print(f'CSV Data Export finished.\nWritten to: {filename}')
        elif fmt == "json":
            filename = f'{base_path}.json'
            print(f'Writing JSON to {filename}')
            #TODO - Allow more formats
            df.to_json(filename, orient="index")
            print(f'JSON Data Export finished.\nWritten to: {filename}')
        elif fmt == "excel":
            filename = f'{base_path}.xlsx'
            print(f'Writing Excel to {filename}')
            df.to_excel(filename)
            print(f'Excel Data Export finished.\nWritten to: {filename}')
        elif fmt == "sql":
            filename = f'{base_path}.sql'
            print(f'Writing SQL to {filename}')
            df.to_sql(filename)
            print(f'SQL Data Export finished.\nWritten to: {filename}')
        elif fmt == "pickle":
            filename = f'{base_path}.pickle'
            print(f'Writing Pickle to {filename}')
            df.to_pickle(filename)
            print(f'Pickle Data Export finished.\nWritten to: {filename}')
        else:
            raise ValueError(f'Unsupported format "{fmt}"')

def main(
        food_db_path=DEFAULT_FOOD_DATASET_PATH,
        food_nutrient_db_path=DEFAULT_FOOD_NUTRIENT_DATASET_PATH,
        nutrient_table_path=DEFAULT_NUTRIENT_PATH,
        export_file_name=DEFAULT_EXPORT_BASE_NAME,
        branded_food_table_path=DEFAULT_BRANDED_PATH,
        export_formats=["csv"],
        translate_nutrients=True,
        excluded_data_types=[],
        branded_food_data=False,
        branded_food_columns=DEFAULT_BRANDED_COLS,
        ):

    # Validate arguments
    if export_formats is None or len(export_formats) == 0:
        export_formats=["csv"],
    for val in export_formats:
        if val not in SUPPORTED_EXPORT_FILE_FORMATS:
            print(f'Unsupported output format "{val}".\n Currently supported formats: {SUPPORTED_EXPORT_FILE_FORMATS}')
            return
    if excluded_data_types is not None and len(excluded_data_types) > 0:
        excluded_data_types = [ dtype for dtype in excluded_data_types if dtype in FOOD_TYPES]
    else:
        excluded_data_types = None

    # Get Start Time    
    start = time.time()
    
    # Get the proccessed DataFrame
    df = get_foods_with_nutrient_data(
            food_db_path=food_db_path,
            food_nutrient_db_path=food_nutrient_db_path,
            nutrient_table_path=nutrient_table_path,
            branded_food_table_path=branded_food_table_path,
            translate_nutrients=translate_nutrients,
            excluded_data_types=excluded_data_types,
            branded_food_data=branded_food_data,
            branded_food_columns=branded_food_columns,
           )
    # Export to selected formats
    export_files(df,
                export_file_name=export_file_name,
                export_formats=export_formats
                )

    # Get End Time and print Duration
    end = time.time()
    print(f'Finished in {end-start} seconds')
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='USDA FoodData data combining and export tool')
    # Paths to DB files
    parser.add_argument('--food-db-path', metavar="FOOD DB FILE PATH",
                        dest='food_db_path', action='store', default=DEFAULT_FOOD_DATASET_PATH,
                        help='The path to the foods.csv file')
    parser.add_argument('--food-nutrient-db-path', metavar="FOOD NUTRIENT DB FILE PATH",
                        dest='food_nutrient_db_path', action='store', default=DEFAULT_FOOD_NUTRIENT_DATASET_PATH,
                        help='The path to the food_nutrient.csv file')
    parser.add_argument('--nutrient-table-path', metavar="NUTRIENT TABLE FILE PATH",
                        dest='nutrient_table_path', action='store', default=DEFAULT_NUTRIENT_PATH,
                        help='The path to the nutrient.csv file')
    parser.add_argument('--branded-food-table-path', metavar="BRANDED FOOD TABLE FILE PATH",
                        dest='branded_food_table_path', action='store', default=DEFAULT_BRANDED_PATH,
                        help='The path to the branded_food.csv file')
    # Export options
    parser.add_argument('--export-file-name', metavar="EXPORTED FILE BASE PATH",
                        dest='export_file_name', action='store', default=DEFAULT_EXPORT_BASE_NAME,
                        help='The path and base name to export into. For each format exported a file will be generated with the relevant format suffix')
    parser.add_argument('--export-format', metavar="EXPORTED DATA FILE FORMAT",
                        dest='export_formats', action='append', default=[],
                        help=f'The file formats to generate an export for. Can specify multiple times. Currently supported formats: {SUPPORTED_EXPORT_FILE_FORMATS}')
    # Data Options
    parser.add_argument('--use-nutrient-names',
                        dest='use_nutrient_names',
                        action='store_true',
                        help='Use nutrient names instead of IDs in the results')
    parser.add_argument('--exclude-data-type', metavar="EXCLUDED DATA TYPE",
                        dest='excluded_data_types', action='append', default=[],
                        help=f'Excludes an USDA FoodData data type from the result. Can specify multiple times, no data type excluded by default. FoodData types: {FOOD_TYPES}')
    parser.add_argument('--include-branded-data',
                        dest='include_branded_data',
                        action='store_true',
                        help='Include extra data about branded foods (from branded_foods.csv)')
    parser.add_argument('--branded-data-columns', metavar="COLUMN NAME 1[,COLUMN NAME 2,....]",
                        dest='branded_data_columns', action='store', default=",".join(DEFAULT_BRANDED_COLS),
                        help=f'A comma-separated list of columns to include from branded_foods.csv. By default {",".join(DEFAULT_BRANDED_COLS)}') 
    args = vars(parser.parse_args())
    main(
        food_db_path=args["food_db_path"],
        food_nutrient_db_path=args["food_nutrient_db_path"],
        nutrient_table_path=args["nutrient_table_path"],
        export_file_name=args["export_file_name"],
        export_formats=args["export_formats"],
        branded_food_table_path=args["branded_food_table_path"],
        translate_nutrients=args["use_nutrient_names"],
        excluded_data_types=args["excluded_data_types"],
        branded_food_data=args["include_branded_data"],
        branded_food_columns=args["branded_data_columns"].split(","),
    )
