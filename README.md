# Parameters of buildings

First practical part (1/3) of Master's thesis: Generalization of LOD2 building models using the aggregation method (2020).

Script serves for reading .xml building file format and counting parameters of buildings in spatial data model. 


## System requirements

Python packages:

* math
* shapely
* lxml
* markup3dmodule (available at: https://github.com/tudelft3d/CityGML2OBJs/blob/master/markup3dmodule.py)
* json
* sys

Skript works in Python 2 


## Parameters of script

* [1] Name of output text file which serves as input for optimization script (.txt)
* [2] Name of output text file which serves as input for visualization script (.txt)
* [3] Name of .xml file with buildings data model
