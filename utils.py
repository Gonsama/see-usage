import os
import json
import csv
import re
import requests

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

def get_unique_used_members(path):
    """return number of unique api_members in file whose path is given"""
    try:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            csv_data = list(reader) 
            #first row must be deleted because it represents the column names
            csv_data.pop(0)      
            api_members = [x[3] + ":" + x[4] + ":" + x[5] for x in csv_data]
            unique_api_members = set(api_members)           
            f.close()
            return len(unique_api_members)
    except IOError:
        print ("File " + path + " do not exist. You should use the script to export library usage before proceeding. ")
        exit()

def get_timestamp_from_json(json_data):
    """return timestamp of library specified by json data"""
    #format is dict containing 2 keys response and responseheader, the values are also dict
    response_data = json_data["response"]
    docs_data = response_data["docs"]
    #if no timestamp
    if len(docs_data) == 0:
        return 0
    else:
        return docs_data[0]["timestamp"]

def get_timestamp(path):
    """return timestamp of library specified by path"""

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
        return 0

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
        return 0 

