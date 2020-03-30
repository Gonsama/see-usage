import os
import json
import csv
import re
import requests
from fnmatch import fnmatch
import math

def get_csv_rows_nb(path):
    """return number of rows of a file whose path is given"""
    try:
        f = open(path, "r")
        #minus 1 bcs first line is column names        
        size = sum(1 for line in f) - 1
        f.close()
        return size
    except IOError:
        print ("File " + path + " do not exist. You should use the script to get the reuse-core before proceeding. ")
        exit()

def get_csv_rows(path):
    """return rows of csv file whose path is given"""
    try:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            csv_data = list(reader) 
            #first row must be deleted because it represents the column names
            csv_data.pop(0)                
            f.close()
            return csv_data
    except IOError:
        print ("File " + path + " do not exist. You should use the script to export library usage before proceeding. ")
        exit()

def get_clients_from_usage(path):
    """return the list of clients in library_usage file given"""
    csv_data = get_csv_rows(path)    
    clients = [x[0] + ":" + x[1] + ":" + x[2] for x in csv_data]
    return clients

def get_members_from_usage(path):
    """return the list of clients in library_usage file given"""
    csv_data = get_csv_rows(path)    
    api_members = [x[3] + ":" + x[4] + ":" + x[5] for x in csv_data]
    return api_members

def get_unique_used_members(path):
    """return number of unique api members in csv file whose path is given""" 
    api_members = get_members_from_usage(path)
    unique_api_members = set(api_members)           
    return len(unique_api_members)

def get_unique_clients(path):
    """return number of unique clients in csv file whose path is given"""  
    clients = get_clients_from_usage(path)
    unique_clients = set(clients)           
    return len(unique_clients)

def get_nb_occurences(element,data):
    """return the number of times element appears in data"""
    occurences = 0
    for x in data:
        if x == element:
            occurences +=1
    return occurences

def get_reusability_index(members):
    """returns the reusability index of data specified by argument which represents the members used by a client"""
    #if a member is present multiple times, we can be sure they are used by different clients because there is no redundancy in the data
    unique_members = set(members)
    #this dict contains data such that key = unique members and value = number of times it is used by different clients      
    nb_usages = {}
    for member in unique_members:
        usages = get_nb_occurences(member,members)
        nb_usages[member] = usages
    #now that the dict is filled, we have to find the max value n such that n members are used by at least n different clients
    minimum=1
    maximum=len(unique_members)
    reusability_index = 0
    while(not minimum > maximum):
        middle = minimum + int(((maximum - minimum) / 2))
        counter = 0
        for key,value in nb_usages.items():
            if value >= middle:
                counter += 1
        if counter >= middle:
            reusability_index = middle
            minimum = middle + 1
        else:
            maximum = middle - 1
    return reusability_index

def get_diversity_value(data, formula):
    """return a number between 0 and 1 representing the evenness of the data computed with formula"""
    unique_data = set(data)
    n = len(unique_data)
    N = len(data)
    #There is no diversity if there is only 1 species        
    if n == 1:
        return 0    
    if formula == "pielou":
        pielou_index = get_pielou_index(data,unique_data,n,N)
        return pielou_index
    elif formula == "simpson":
        simpson_index = get_simpson_index(data,unique_data,n,N)       
        return simpson_index
    elif formula == "theil":
        theil_index = get_theil_index(data,unique_data,n,N)       
        return theil_index
    elif formula == "gini":
        gini_index = get_gini_index(data,unique_data,n,N)       
        return gini_index

def get_pielou_index(data,unique_data,n,N):
    total_sum = 0
    for element in unique_data:
        nb_element = get_nb_occurences(element,data)
        proportion = float(nb_element) / N
        total_sum += float(proportion) * math.log10(proportion)
    H = -total_sum
    evenness = H / math.log10(n)
    return evenness

def get_simpson_index(data,unique_data,n,N):
    total_sum = 0
    for element in unique_data:
        nb_element = get_nb_occurences(element,data)
        numerator = float(nb_element) * (nb_element - 1)
        denominator = N * (N - 1)
        total_sum += (numerator / denominator)
    simpson_index = 1 - total_sum        
    return simpson_index

def get_theil_index(data,unique_data,n,N):
    total_sum = 0
    mean_occurences = float(N) / n
    for element in unique_data:
        nb_element = get_nb_occurences(element,data)
        ratio = float(nb_element) / mean_occurences
        total_sum += ratio * math.log10(ratio)
    theil_index = float(total_sum) / n
    normalized_theil_index = theil_index / math.log(n)
    return theil_index

def get_gini_index(data,unique_data,n,N):
    mean_occurences = float(N) / n
    double_sum = 0
    for x in unique_data:
        x_occurences = get_nb_occurences(x,data)
        for y in unique_data:
            y_occurences = get_nb_occurences(y,data)
            double_sum += abs(x_occurences - y_occurences)
    gini_index = (float(1) / (2 * n * n * mean_occurences)) * double_sum
    return gini_index

def get_paths_containing_pattern(root_directory, pattern):
    """getting path to subdirectories containing pattern"""
    subdirectories_path = []
    for path, subdirs, files in os.walk(root_directory):
        for name in files:
            if fnmatch(name, pattern):
                subdirectories_path.append(path)
    return subdirectories_path

def get_timestamp_from_json(json_data):
    """return timestamp of library specified by json data"""
    #format is dict containing 2 keys response and responseheader, the values are also dict
    response_data = json_data["response"]
    docs_data = response_data["docs"]
    #if no timestamp
    if len(docs_data) == 0:
        return -1
    else:
        return docs_data[0]["timestamp"]

def get_timestamp(path):
    """return timestamp of library specified by path, returns -1 if no timestamp"""

    #look for properties file first, if it doesn't exist request REST api for the properties
    if os.path.isfile(path + "/properties.json"):
        print (path + "/properties.json exist")
        with open(path + "/properties.json") as json_file:
            json_data = json.load(json_file)
            return get_timestamp_from_json(json_data)
    else:
        print (path + "/properties.json do not exist" )


    #properties file doesnt exist

    # example of split path : ['csv-data', 'commons-cli', 'commons-cli', '1.3']
    split_path = re.split(':|/',path) 

    url = 'https://search.maven.org/solrsearch/select?q=g:"' + split_path[1] + '"%20AND%20a:"' + split_path[2] + '"%20AND%20v:"' + split_path[3] + '"&wt=json'

    print ("Requesting properties from REST api ...")    

    try:
        myResponse = requests.get(url)
    except requests.exceptions.RequestException as e:
        print (e)
        return -1

    # For successful API call, response code will be 200 (OK)
    if(myResponse.ok):

        print ("Response to get properties of " + path + " is OK")

        # Loading the response data into a dict variable
        # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
        json_data = json.loads(myResponse.content)
        
        #write data in file for next times
        with open( path + '/properties.json', 'w') as outfile:
            json.dump(json_data, outfile)        

        return get_timestamp_from_json(json_data)
    else:
        # If response code is not ok (200)
        print ("Response to get properties of " + path + " is not OK")
        myResponse.raise_for_status()
        return -1

def get_sorted_versions_path_timestamp(root_directory, regex):
    """returns all versions (path, timestamp) tuple that are not matching regex in a list of tuples"""
    regex = re.compile(regex)
    versions_tuple = []
    for x in os.walk(root_directory): 
        #libraries with 0 usages not considered either
        if x[0] != root_directory and not regex.search(x[0]) and get_csv_rows_nb(x[0] + "/library-usage.csv") != 0:
            timestamp = get_timestamp(x[0])
            if timestamp != -1:        
                versions_tuple.append((x[0],timestamp))
    #sort list so that versions are in ascending order
    versions_tuple = sorted(versions_tuple, key=lambda tup: tup[1])
    return versions_tuple

def get_x_axis_data(sot, versions_tuple):
    """returns a tuple where the first element is the values of the x_axis to be plotted (list) and second element is the title of the x_axis"""
    if sot:
        x_axis = []
        for i in range(len(versions_tuple)-1,-1,-1):
            #rare case where two versions have the same timestamp
            if len(x_axis) >= 1 and versions_tuple[i][1] == x_axis[0]: 
                x_axis.insert(0,versions_tuple[i][1] - 1)
            else:
                x_axis.insert(0,versions_tuple[i][1])
        x_axis_title = "time"
    else:
        #space between versions will be equal
        #split path to versions to get only versions
        x_axis = [path.split("/")[2] for path,t in versions_tuple]
        x_axis_title = "library version"
    return (x_axis, x_axis_title)
