#!/usr/bin/env python
import pandas as pd
import time

DATASET_DIR = "FoodData_Central_csv_2020-04-29"
FOOD_DATASET_FILE = "food.csv"
BRANDED_FOOD_DATASET_FILE = "branded_food.csv"
FOOD_NUTRIENT_DATASET_FILE = "food_nutrient.csv"
NUTRIENT_FILE = "nutrient.csv"


def get_food_table(low_memory=False, usecols=None):
    if usecols is not None:
        if "fdc_id" not in usecols:
            usecols.append("fdc_id")
        return pd.read_csv(f'{DATASET_DIR}/{FOOD_DATASET_FILE}', low_memory=low_memory, index_col="fdc_id", usecols=usecols)
    else:
        return pd.read_csv(f'{DATASET_DIR}/{FOOD_DATASET_FILE}', low_memory=low_memory, index_col="fdc_id")

def get_nutrients_table(low_memory=False, usecols=None):
    if usecols is not None:
        if "id" not in usecols:
            usecols.append("id")
        return pd.read_csv(f'{DATASET_DIR}/{NUTRIENT_FILE}', low_memory=low_memory, index_col="id", usecols=usecols)
    else:
        return pd.read_csv(f'{DATASET_DIR}/{NUTRIENT_FILE}', low_memory=low_memory, index_col="id")

def get_nutri_data_table(low_memory=False):
    return pd.read_csv(f'{DATASET_DIR}/{FOOD_NUTRIENT_DATASET_FILE}', low_memory=low_memory)

def get_nutrient_names(nutrient_table=None):
    nutrient_table = nutrient_table if isinstance(nutrient_table, pd.DataFrame) else  pd.read_csv(f'{DATASET_DIR}/{NUTRIENT_FILE}')
    res = nutrient_table["name"].to_list()
    return res

def get_nutrient_dict(nutrient_table=None):  
    nutrient_table = nutrient_table if isinstance(nutrient_table, pd.DataFrame) else get_nutrients_table(usecols=["name", "unit_name"])
    return nutrient_table.to_dict(orient='index')

def get_foods_with_nutrient_data(translate_nutrients=True):
    print("Reading food nutrient data...")
    food_nutrients = get_nutri_data_table()
    food_nutrients.sort_values(
                           "fdc_id",
                           inplace=True,
                           ignore_index=True)

    food_nutrients = food_nutrients.pivot(
                                        index="fdc_id",
                                        columns="nutrient_id",
                                        values="amount")

    print("Reading food data...")
    foods = get_food_table(usecols=["description", "data_type"])
    print("Processing...")
    final = pd.concat([foods, food_nutrients], axis=1, join='inner')
    if translate_nutrients:
        print("Translating nutrient ids to nutrient names")
        nutri_dict = get_nutrient_dict()
        final.rename(inplace=True,
                     axis=1,
                     mapper= lambda x: nutri_dict[x]["name"] if isinstance(x, int) else x)
    return final

def main(base_filename="exported_foods", describe=True, translate_nutrients=True):
    start = time.time()
    df = get_foods_with_nutrient_data(translate_nutrients=translate_nutrients)
    csv_filename = f'{base_filename}.csv'
    print(f'Writing CSV file to {csv_filename}')
    df.to_csv(csv_filename)
    if describe:
        df.describe()
    print(f'Data Export finished.\nWritten to: {csv_filename}')
    end = time.time()
    print(f'Finished in {end-start} seconds')
    
if __name__ == "__main__":
    main()
