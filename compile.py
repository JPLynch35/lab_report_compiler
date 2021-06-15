import csv
import fileinput
import os
from os import listdir
import shutil

def delete_existing_file(file_path):
  if os.path.exists(file_path):
    os.remove(file_path)

def csv_file_list(directory, file_type):
  filenames = listdir(directory)
  return [ filename for filename in filenames if filename.endswith( file_type ) ]

def primary_file_path():
  primary_file_name = csv_file_list('./primary', 'csv')[0] # [0] because only single file expected
  return './primary/' + primary_file_name

def secondary_file_paths():
  secondary_file_names = csv_file_list('./secondaries', 'csv')
  return ['./secondaries/' + secondary_file_name for secondary_file_name in secondary_file_names]

def results_file_path():
  results_file_name = 'results.csv'
  return './' + results_file_name

def compiled_secondaries_file_path():
  compiled_secondaries_file_name = 'compiled_secondaries.csv'
  return './' + compiled_secondaries_file_name

def copy_file(from_file_path, to_file_path):
  shutil.copyfile(from_file_path, to_file_path)

def remove_file(file_path):
  os.remove(file_path)

def sort_file(file_path, match_header_name):
  temp_file_path = file_path + '.bak'
  with open(file_path, 'r') as file:
    data = csv.DictReader(file)
    sorted_data = sorted(data, key=lambda row: row[match_header_name], reverse=True)
    headers = data.fieldnames
    with open(temp_file_path, 'w') as temp_sorted_file:
      data = csv.DictWriter(temp_sorted_file, fieldnames=headers)
      data.writeheader()
      data.writerows(sorted_data)
  copy_file(temp_file_path, file_path)
  remove_file(temp_file_path)

def results_file_headers(fieldnames):
  return fieldnames + [header + ' (Secondary)' for header in fieldnames]

def create_results_file():
  with open(primary_file_path(), 'r') as primary_file:
    primary_data = csv.DictReader(primary_file)
    headers = results_file_headers(primary_data.fieldnames)
    with open(results_file_path(), 'w') as results_file:
      data = csv.DictWriter(results_file, fieldnames=headers)
      data.writeheader()
      data.writerows(primary_data)

def create_empty_secondaries_file():
  sample_secondary_file_path = secondary_file_paths()[0]
  with open(sample_secondary_file_path, 'r') as sample_secondary_file:
    data = csv.DictReader(sample_secondary_file)
    headers = data.fieldnames
    with open(compiled_secondaries_file_path(), 'w') as compiled_secondaries_file:
      data = csv.DictWriter(compiled_secondaries_file, fieldnames=headers)
      data.writeheader()

def populate_compiled_secondaries_file(secondary_file_path):
  with open(secondary_file_path, 'r') as secondary_file:
    secondary_data = csv.DictReader(secondary_file)
    headers = secondary_data.fieldnames
    with open(compiled_secondaries_file_path(), 'a') as compiled_secondaries_file:
      data = csv.DictWriter(compiled_secondaries_file, fieldnames=headers)
      data.writerows(secondary_data)

def create_compiled_secondaries_file():
  for secondary_file_path in secondary_file_paths():
    populate_compiled_secondaries_file(secondary_file_path)

def convert_to_string(row):
  data = (str(value.replace(',', ';')) for value in row.values())
  return ",".join(data)

def combine_results_and_secondaries_rows(results_row, secondaries_row):
  for secondaries_header in secondaries_row.keys():
    results_row[secondaries_header + ' (Secondary)'] = secondaries_row[secondaries_header]
  return results_row

def add_secondaries_data_to_results(secondaries_row, match_header_name):
  with fileinput.input(results_file_path(), inplace=True, mode='r') as results_csv_file:
    results_data = csv.DictReader(results_csv_file)
    print(",".join(results_data.fieldnames))
    for results_row in results_data:
      if results_row[match_header_name] == secondaries_row[match_header_name]:
        results_row = combine_results_and_secondaries_rows(results_row, secondaries_row)
      converted_row = convert_to_string(results_row)
      print(converted_row)

def add_compiled_secondaries_to_results(match_header_name):
  with open(compiled_secondaries_file_path()) as compiled_secondaries_file:
    secondaries_data = csv.DictReader(compiled_secondaries_file)
    next(secondaries_data) # skip headers
    for secondaries_row in secondaries_data:
      add_secondaries_data_to_results(secondaries_row, match_header_name)

# settings
match_header_name = 'ID'
# results prepping
delete_existing_file(results_file_path())
create_results_file()
sort_file(results_file_path(), match_header_name)
# secondaries prepping
delete_existing_file(compiled_secondaries_file_path())
create_empty_secondaries_file()
create_compiled_secondaries_file()
sort_file(compiled_secondaries_file_path(), match_header_name)
# results compiling
add_compiled_secondaries_to_results(match_header_name)
sort_file(results_file_path(), match_header_name + ' (Secondary)')
# cleanup
remove_file(compiled_secondaries_file_path())

# setup instructions
# 
# place compile script in folder (name does not matter)
# place folder named 'primary' at same level as compile script
# place folder named 'secondaries' at same level as compile script
# update 'match_header_name' to name of column to match on
