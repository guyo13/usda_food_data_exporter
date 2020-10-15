# FoodData Exporter
`fooddata_exporter.py` is a Python module and CLI program that allows users to access, combine and export
data from the USDA FoodData database (csv format).

This project is part of <a href="https://www.freemacrotracker.com" target="_blank">Free Macro Tracker</a> project,
the Open-source diet consultant that respects your privacy.

## Capabilities

* Combining data from the `food.csv` table with data from `nutrient.csv` and `food_nutrient.csv` tables to create the nutritional value of the product
* Optionally Exclude data based on `data_type` column
* Export combined results into popular formats including csv, json, excel, sql and more

## Getting the data
Go to USDA donwload section: https://fdc.nal.usda.gov/download-datasets.html

Under the "Full Download of All Data Types" section select the latest CSV link

## Installing requirements

FoodData Exporter depends on <a href="https://pandas.pydata.org/pandas-docs/stable/index.html" target="_blank">Pandas</a>, install it by executing:

`pip install pandas`

or use the supplied requirements file:

`pip install -r requirements.txt`

It is suggested to use a virtual env and install the requirements there. If you wish do so by executing:

On linux and macOS - `python -m venv venv && . venv/bin/activate && pip install -r requirements.txt`

On Windows and for futher details about virtual env see- https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/ 

## Usage

`fooddata_exporter.py` need the path to three csv files: `food.csv`, `food_nutrient.csv` and `nutrient.csv` (optional, needed when using the --use-nutrient-names option).

You can specify them using the `--food-db-path`, `--food-nutrient-db-path` and `--nutrient-table-path` respectively. Otherwise the program assumes those files are in your current working directory.

### Accessing the help menu
`python fooddata_exporter.py -h` will print the help menu where you can find all the different arguments and their supported values.

### Noteworthy options

`--export-file-name` - The file name of the output. For each format exported will append `.<format name>` to this path.

`--export-format <format>` - Specifies an export format. You can specify this multiple times for exporting into multiple formats.

`--exclude-data-type <type>` - Excludes a food data source("data_type") from the result. You can specify this multiple times to exclude multiple sources.

`--use-nutrient-names` - Use nutrient names from `nutrient.csv` in the result's header/keys instead of nutrient ids.

## Example Usage

### Combine data and export nutritional values with nutrient names
```
python fooddata_exporter.py --use-nutrient-names --export-format csv --export-file-name ./exported/food_database
```

### Export to multiple formats
```
python fooddata_exporter.py --export-format csv --export-format json --export-file-name ./exported/food_database
```

### Exclude Agricultural data and Sub Sampling data from results
```
python fooddata_exporter.py --exclude-data-type sub_sample_food --exclude-data-type agricultural_acquisition --export-file-name ./exported/food_database
```

## Issues and Contributions

If you find a bug, have a feature request or have a question, you are welcome to open an Issue on the <a href="https://github.com/guyo13/usda_food_data_exporter/issues" target="_blank">Issue Tracker</a>

If you want to contribute, open a pull request on <a href="https://github.com/guyo13/usda_food_data_exporter" target="_blank">GitHub</a>.

All outside contributions are licensed to the author under the MIT license.

## License
FoodData Exporter is licensed under the GNU General Public License version 3
for the benefit of all and the advancement of Open Source Nutrition.

For further details see the included LICENSE file and gpl-3.0 file.

See <a href="http://www.gnu.org/licenses/gpl-3.0.en.html" target="_blank">GNU GPL</a> website if you are interested in the Free Software Foundation
