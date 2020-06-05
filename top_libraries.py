import os
import csv
import utils
import argparse

def get_libraries_path(root_path):
    libraries_path = []
    for x in os.walk(root_path):
        #searching for repertories containing a library-usage file
        if (os.path.exists(x[0] + os.path.sep + "library-usage.csv")):
            split_path = x[0].split(os.path.sep)
            split_path.pop()
            libraries_path.append(os.path.sep.join(split_path))
    return list(set(libraries_path))

#command-line arguments
parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--root", type=str, required=True, help="path of the root directory containing every libraries")
parser.add_argument("--N", type=int, default=10, help="Show first N libraries")
args = parser.parse_args()

#elements of list are tuple (l,n) where l is library name, u is number of usages and c is number of unique clients
top_libraries = []

print ("Looking for every libraries which contains usage data")

#path of the different libraries (no duplicates)
libraries = get_libraries_path(args.root)

print ("Counting usages and clients for every library in no order (order will be at the end)")
for library in libraries:
    pattern = "*library-usage.csv"
    all_versions_path = utils.get_paths_containing_pattern(library, pattern)
    nb_usages = 0
    nb_clients = 0
    for version_path in all_versions_path:
        nb_usages += utils.get_csv_rows_nb(version_path + os.path.sep + "library-usage.csv")
        nb_clients += utils.get_unique_clients(version_path + os.path.sep + "library-usage.csv")
    top_libraries.append((library ,nb_usages, nb_clients))
    print (str(len(top_libraries)) + ": " + str((library ,nb_usages, nb_clients)))

top_libraries_sorted = sorted(top_libraries, key=lambda tup: tup[1],reverse=True)
limit = args.N
if limit > len(top_libraries_sorted):
    limit = len(top_libraries_sorted)

print ("The top " + str(limit) + " libraries are :")

for i in range(limit):
    print (top_libraries_sorted[i])
