import os
import csv
import utils
import argparse

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]


#command-line arguments
parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--N", type=int, default=10, help="Show first N libraries")
args = parser.parse_args()

#elements of list are tuple (l,n) where l is library name, u is number of usages and c is number of unique clients
top_libraries = []

libraries = get_immediate_subdirectories("./csv-data")
for library in libraries:
    #getting path to subdirectories containing a library-usage.csv file
    root_directory = "./csv-data/" + library
    pattern = "*library-usage.csv"
    all_versions_path = utils.get_paths_containing_pattern(root_directory, pattern)
    nb_usages = 0
    nb_clients = 0
    for version_path in all_versions_path:
        nb_usages += utils.get_csv_rows_nb(version_path + "/library-usage.csv")
        nb_clients += utils.get_unique_clients(version_path + "/library-usage.csv")
    top_libraries.append((library ,nb_usages, nb_clients))
    print (len(top_libraries))
    print ((library ,nb_usages, nb_clients))

top_libraries_sorted = sorted(top_libraries, key=lambda tup: tup[1, reverse=True])
limit = args.N
if limit > len(top_libraries_sorted):
    limit = len(top_libraries_sorted)

for i in range(limit - 1):
    print (top_libraries_sorted[i])
