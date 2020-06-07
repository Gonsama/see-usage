# see-usage
This tool has been developed by Semih Locqueneux in link with a thesis to obtain a master in computer sciences (University of Mons). The tool can be used after obtaining data from a related work : " https://github.com/castor-software/core-83 " (use script export.py on the data obtained) or on data obtained by another tool as long as it follows the right format, that is to say the usage of a library must be contained in a csv file called library-usage.csv where there are 6 columns : clientgroupid, clientartifactid, clientversion, memberpackage, memberclass, apimember. Data already exported in the right format can be downloaded on [this link](https://drive.google.com/file/d/1K6_CLU-xilddJg-lCwuTOt9XUM2TmfRn/view?usp=sharing). To obtain this data, the script export.py was used on a database furnished by the authors of the related work ([data](https://zenodo.org/record/2567268)) which contains the statical usages of the 99 most poupular libraries in the Central Maven Repository as of september 2018. The exported data can be used to get familiar with the tool. An example of use of each script is described in the following (for the junit library).

### Necessary Python modules (version 3 at least)
- requests
- matplotlib
- networkx
- scipy

### export.py
This script exports the usage data from a database and writes it in specific csv files following the hierarchy csv-data/groupid:artifactid/version/library-usage.csv for each libraries.
```
 python3 export.py --host localhost --user user --password 12345 --dbname api_dependencies

```

### data-repartition.py

This script plots the repartition of the data available for all the versions of a specific library. The repartition can be according to the number of unique clients, usages or unique members. The library path argument must be the path to the repertory containing every version of the library (the script will search for version/library-usage.csv files for each version)

```
 python3 data_repartition.py --lp csv-data/junit/junit/ --type clients

```

### diversity-evolution.py

This script plots the diversity for all the versions of a specific library. As the diversity can be computed for the used members of the library or the unique clients that used the library, it can be specified in an argument (--according). Likewise, the diversity can be computed with different formulas which can be chosen with the --formula argument. The library path argument must be the path to the repertory containing every version of the library (the script will search for version/library-usage.csv files for each version). The explanation of the various formulas can be found in the thesis.

```
 python3 diversity_evolution.py --lp csv-data/junit/junit/ --formula simpson --according clients

```

### reusability-index-evolution.py

This script plots the reusability index for all the versions of a specific library. The reusability index is a metric which is defined by " The maximal value n such that n members are used by at least n clients ". The library path argument must be the path to the repertory containing every version of the library (the script will search for version/library-usage.csv files for each version)

```
python3 reusability_index_evolution.py --lp csv-data/junit/junit/

```

### core.py

This script is different from the precendent ones, it doesn't plot anything. It actually computes the reuse-core of specified libraries and writes the result on a csv file called reuse-core-P.csv where the P can be specified in argument (--percent). The reusability index is a metric which is defined by " The reuse-core for a specific alpha is the necessary and sufficient subset of members of an API which satisfy alpha percent of the clients ". The example below means that a core will be computed for each version of the JUnit library. The same can be done for only one version by specifying it in the path. Likewise the core can be computed for each version of every single library by specifying the root as the path.

```
python3 core.py --path csv-data/junit/junit --percent 50

```

### core-evolution.py

This script plots the reuse-core for all the versions of a specific library. Multiple curve can be on the same plot by specifying it in argument (--p) . The library path argument must be the path to the repertory containing every version of the library (the script will search for version/library-usage.csv files for each version). The precondition is that the core.py script was used on the libraries previously.

```
python3 core_evolution.py --lp csv-data/junit/junit/  --p 20 40 60 80

```

### compare-cores.py

This script plots the intersection of two cores on a circular diagram. The example below is comparing the reuse-core with alpha = 60 percent for the 4.10 and 4.12 version of JUnit

```
python3 compare_cores.py --cp1 csv-data/junit/junit/4.10/reuse-core-60.csv --cp2 csv-data/junit/junit/4.12/reuse-core-60.csv

```

### scatter.py

This script plots the scatter plot of two metrics specified in argument. It also prints the pearson correlation coefficient between the data os the two metrics. The example below is plotting the scatter plot of the number of members used (x-axis) and the reusability index (y-axis)

```
python3 scatter.py --lp csv-data/junit/junit/ --metric1 nMembers --metric2 reusability-index --o junit-scatter


```
