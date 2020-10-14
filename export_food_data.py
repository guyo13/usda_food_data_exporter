#!/usr/bin/env python
import pandas as pd

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
    nutrient_table = nutrient_table if isinstance(nutrient_table, pd.DataFrame) else  pd.read_csv(f'{DATASET_DIR}/{NUTRIENT_FILE}')
    return nutrient_table.to_dict(orient='index')

def export_foods_with_nutrient_data(base_filename="exported_foods"):
    # Read CSV Files
    food_table = get_food_table(usecols=["description", "data_type"])
    nutrient_table = get_nutrients_table(usecols=["name", "unit_name"])
    nutri_value_table = get_nutri_data_table()

    # Get Nutrients dict
    nutri_dict = get_nutrient_dict(nutrient_table)

    # Get column names for output
    columns = ["fdc_id", "description", "data_type"] + get_nutrient_names(nutrient_table)

    # Create output DF
    out_df = pd.DataFrame(columns=columns)
    out_df.set_index("fdc_id")

    # Iterate Foods
    for idx, food_row in food_table.iterrows():
        print(f'Working on {idx}')
        data = nutri_value_table.query(f'fdc_id == {idx}')
        output_row = {
            "fdc_id": idx,
            "description": food_row["description"],
            "data_type": food_row["data_type"]
            }
        for _idx, nutrient_row in data.iterrows():
            nutrient_id = nutrient_row["nutrient_id"]
            nutrient_name = nutri_dict[nutrient_id]["name"]
            output_row[nutrient_name] = nutrient_row["amount"]
        out_df = out_df.append(output_row, ignore_index=True)
        break
    out_df.to_csv(f'{base_filename}.csv')
    #out_df.to_pickle(f'{base_filename}.pickle')



if __name__ == "__main__":
    export_foods_with_nutrient_data()
