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
    data_reader = csv.DictReader(file)
    sorted_data = sorted(data_reader, key=lambda row: row[match_header_name], reverse=True)
    headers = data_reader.fieldnames
    with open(temp_file_path, 'w') as temp_sorted_file:
      data_writer = csv.DictWriter(temp_sorted_file, fieldnames=headers)
      data_writer.writeheader()
      data_writer.writerows(sorted_data)
  copy_file(temp_file_path, file_path)
  remove_file(temp_file_path)

def sort_file_by_two_columns(file_path, match_header_name):
  temp_file_path = file_path + '.bak'
  with open(file_path, 'r') as file:
    data_reader = csv.DictReader(file)
    presorted_data = sorted(data_reader, key=lambda row: row[match_header_name])
    match_secondary_header_name = match_header_name + ' (Secondary)'
    sorted_data = sorted(presorted_data, key=lambda row: row[match_secondary_header_name], reverse=True)
    headers = data_reader.fieldnames
    with open(temp_file_path, 'w') as temp_sorted_file:
      data_writer = csv.DictWriter(temp_sorted_file, fieldnames=headers)
      data_writer.writeheader()
      data_writer.writerows(sorted_data)
  copy_file(temp_file_path, file_path)
  remove_file(temp_file_path)

def results_file_headers(fieldnames):
  return fieldnames + [header + ' (Secondary)' for header in fieldnames]

def create_results_file():
  with open(primary_file_path(), 'r') as primary_file:
    data_reader = csv.DictReader(primary_file)
    headers = results_file_headers(data_reader.fieldnames)
    with open(results_file_path(), 'w') as results_file:
      data_writer = csv.DictWriter(results_file, fieldnames=headers)
      data_writer.writeheader()
      data_writer.writerows(data_reader)

def create_empty_secondaries_file():
  sample_secondary_file_path = secondary_file_paths()[0]
  with open(sample_secondary_file_path, 'r') as sample_secondary_file:
    data_reader = csv.DictReader(sample_secondary_file)
    headers = data_reader.fieldnames
    with open(compiled_secondaries_file_path(), 'w') as compiled_secondaries_file:
      data_writer = csv.DictWriter(compiled_secondaries_file, fieldnames=headers)
      data_writer.writeheader()

def populate_compiled_secondaries_file(secondary_file_path):
  with open(secondary_file_path, 'r') as secondary_file:
    data_reader = csv.DictReader(secondary_file)
    headers = data_reader.fieldnames
    with open(compiled_secondaries_file_path(), 'a') as compiled_secondaries_file:
      data_writer = csv.DictWriter(compiled_secondaries_file, fieldnames=headers)
      data_writer.writerows(data_reader)

def create_compiled_secondaries_file():
  for secondary_file_path in secondary_file_paths():
    populate_compiled_secondaries_file(secondary_file_path)

def convert_to_string(row):
  data = (str(value.replace(',', ';')) for value in row.values())
  return ",".join(data)

def primary_file_empty_rows():
  with open(primary_file_path(), 'r') as primary_file:
    primary_reader = csv.DictReader(primary_file)
    headers = primary_reader.fieldnames
  return ['-,' for header in headers]

def convert_to_unmatched_string(headers, secondaries_row):
  combined_row = dict((column,'-') for column in headers)
  for secondaries_header in secondaries_row.keys():
    combined_row[secondaries_header + ' (Secondary)'] = secondaries_row[secondaries_header]
  return combined_row

def combine_results_and_secondaries_rows(results_row, secondaries_row):
  for secondaries_header in secondaries_row.keys():
    results_row[secondaries_header + ' (Secondary)'] = secondaries_row[secondaries_header]
  return results_row

def add_secondaries_data_to_results(secondaries_row, match_header_name):
  with fileinput.input(results_file_path(), inplace=True, mode='r') as results_file:
    data_reader = csv.DictReader(results_file)
    print(",".join(data_reader.fieldnames))
    match_found = False
    for results_row in data_reader:
      if results_row[match_header_name] == secondaries_row[match_header_name]:
        match_found = True
        results_row = combine_results_and_secondaries_rows(results_row, secondaries_row)
      converted_row = convert_to_string(results_row)
      print(converted_row)
    return match_found

def add_secondaries_data_to_results_as_unmatched(secondaries_row):
  with open(results_file_path(), 'r') as results_file:
    data_reader = csv.reader(results_file)
    for headers in data_reader:
        break
  converted_row = convert_to_unmatched_string(headers, secondaries_row)
  with open(results_file_path(), 'a', newline='') as results_file:
    data_writer = csv.DictWriter(results_file, fieldnames=headers)
    data_writer.writerow(converted_row)

def add_compiled_secondaries_to_results(match_header_name):
  with open(compiled_secondaries_file_path()) as compiled_secondaries_file:
    secondaries_data = csv.DictReader(compiled_secondaries_file)
    next(secondaries_data) # skip headers
    for secondaries_row in secondaries_data:
      if not add_secondaries_data_to_results(secondaries_row, match_header_name):
        add_secondaries_data_to_results_as_unmatched(secondaries_row)

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
sort_file_by_two_columns(results_file_path(), match_header_name)
# cleanup
remove_file(compiled_secondaries_file_path())

# setup instructions
# 
# place compile script in folder (name does not matter)
# place folder named 'primary' at same level as compile script
# place folder named 'secondaries' at same level as compile script
# update 'match_header_name' to name of column to match on
