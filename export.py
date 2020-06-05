import mysql.connector
import os
import csv
import argparse

########################
#Command-line arguments#
########################

parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--host", required=True, type=str, help="Host name of the database")
parser.add_argument("--user", required=True, type=str, help="User name of to connect to the database. The user must have at least reading permission on the db.")
parser.add_argument("--password", required=True, type=str, help="Password of the user specified in --user argument")
parser.add_argument("--dbname", required=True, type=str, help="The name of the database on which the usage data is written")
args = parser.parse_args()


#####################
#Database connection#
#####################

print ("Connecting to database...")

#connecting to the database
db = mysql.connector.connect(
  host=args.host,
  user=args.user,
  passwd=args.password
)

print ("Connected to database")

cursor = db.cursor()

print ("Executing SQL request to get libraries...")

cursor.execute("use " + args.dbname)
cursor.execute("SELECT CONCAT(groupid, ':', artifactid) AS libraries, version FROM library")

print ("SQL query to get libraries executed")

sql_result_libraries = cursor.fetchall()

######################################################################
#creating a repertory for each libraries (versions in subdirectories)#
######################################################################

print ("different repertories being created")

for x in sql_result_libraries:
    path = "csv-data" + os.path.sep + str(x[0].decode()) + os.path.sep + str(x[1].decode())
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            print ("Creation of the directory %s failed" % path)

###############################################################################
#putting query result for reuse-core computing in csv files for each libraries#
###############################################################################

print ("creating and filling csv files for each libraries...")

size = len(sql_result_libraries)
counter = 1
 
for x in sql_result_libraries:
    csv_file_path = "csv-data" os.path.sep + str(x[0].decode()) + os.path.sep + str(x[1].decode()) + os.path.sep + "library-usage.csv"
    library_coordinates = str(x[0].decode()) + ":" + str(x[1].decode())

    #4298,403
    cursor.execute("use " + args.dbname)
    cursor.execute(
    "SELECT c.groupid AS clientgroupid, c.artifactid AS clientartifactid, c.version AS clientversion, p.package as memberpackage, m.class as memberclass, m.member as apimember FROM api_member AS m JOIN package AS p ON m.packageid=p.id JOIN api_usage AS u ON m.id=u.apimemberid JOIN client AS c ON u.clientid=c.id WHERE m.libraryid=(SELECT id FROM library WHERE coordinates = '" + library_coordinates + "');")
    columns_names = [i[0] for i in cursor.description]    
    sql_result_usage = cursor.fetchall()
    fp = open(csv_file_path, 'w')
    myFile = csv.writer(fp, lineterminator = '\n')
    myFile.writerow(columns_names)
    myFile.writerows(sql_result_usage)
    fp.close()
    print ("csv file created for  " + library_coordinates + " (" + str(counter) + os.path.sep + str(size) + ")")
    counter += 1


print ("csv files created for each libraries")
