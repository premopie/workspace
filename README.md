# Workspace
-----------

Python module for handling HDF5 variables in [ipython](http://ipython.org/) console.  
Created variables are stored using [h5py.](http://www.h5py.org)

### Main Features
-----------------
- Provides a set of tools for handling variables, i.e. objects being
  instances of the ``Variable`` class.
- Variables are created in the interactive namespace, which is by
  default a current ``__main__`` module.
- When running in IPython, variables are available through the
  interactive namespace.
- Each variable is paired with an associated HDF5 root group and
  exposes convenient interface for it.
- Created variables are stored in the HDF5 binary data format.
- Explore variables using tab completion mechanism. For IPython it is
  recommended to have greedy completion enabled.
- Dataset compression is enabled by default. Compression parameters can
  be changed through the interactive namespace.

### Motivation
--------------
A goal of this project is to provide environment for handling HDF5 files in Python console (preferably in IPython). Main application of this module is to store and organize large amount of measurement data.

### Prerequisites
-----------------
Workspace requires the following software installed for your platform:
1. [Python](https://www.python.org/)
2. [NumPy](http://www.numpy.org/)
3. [H5py](http://www.h5py.org/)
4. [IPython](https://ipython.org/) (optional)

The easiest way of getting all required software is to install [Anaconda](https://www.continuum.io/downloads)

### Basic Usage
---------------
This chapter assumes that all required packages are installed.
##### ENVIRONMENT CONFIGURATION
In order to start working with  **Workspace** module following steps are needed:
1. Run Python interpreter in the directory containing project files.
2. Import ``ui`` module:
```import workspace.ui```
3. Create an instance of the ``Interface()`` class:
```ws = workspace.ui.Interface()```
4. Enable tab completion mechanism: (optional, IPython only)
```get_ipython().magic('config IPCompleter.greedy = True')```

##### CREATING/OPENING A HDF5 FILE
HDF5 file are being created by calling ``add`` method on the ``ws`` object, which is an instance of the ``workspace.ui.Interface()`` class.

##### Example:
*In*: ``ws.add("example_file.h5")``

##### CREATING VARIABLES
Variables are being created by calling a proper``create`` method on the ``ws[file_index]``, which points to HDF5 file with index = [file_index] in the interactive namespace.
As for now there is only ``basic`` type supported. More information could be found in the [API Reference](https://wojciechwisniewski.github.io/)

##### Example:
*In*: ``ws[0].create.basic("var1")``

It is also possible to specify parent of variable that is being created:
Following code creates variable ``var2`` as a children of ``var1``.

*In*: ``ws[0].create.basic("var2",var1)``

##### REMOVING VARIABLES
In order to remove variable from the HDF5 file and the interactive namespace, method ``remove()`` should be called on it.

##### Example:
*In*: ``var1.remove()``

##### DISPLAYING LIST OF HDF5 FILES
List of HDF5 files that are loaded in current session is available through ``ws`` object, which is an instance of the ``workspace.ui.Interface()`` class.

##### Example:
*In*: ``ws``
*Out*: 
```
0) HDF5 file "file_0.h5" (mode r+)
1) HDF5 file "file_1.h5" (mode r+)
2) HDF5 file "file_2.h5" (mode r+)
```

##### DISPLAYING LIST OF VARIABLES
List of variables contained in all HDF5 files that are loaded in current session, is available through ``ws.vars``, where ``ws`` is an instance of the ``workspace.ui.Interface()`` class.

##### Example:
*In*: ``ws.vars``
*Out*: 
```
0) Variable var_0 (-) from HDF5 group "/var_0" (1 members) in HDF5 file "file_0.h5" (mode r+)
1) Variable var_1 (var_0) from HDF5 group "/var_1" (1 members) in HDF5 file "file_0.h5" (mode r+)
2) Variable var_2 (var_1) from HDF5 group "/var_2" (1 members) in HDF5 file "file_1.h5" (mode r+)
2) Variable var_3 (-) from HDF5 group "/var_3" (1 members) in HDF5 file "file_2.h5" (mode r+)
```
For each variable there is also name of the parent of associated HDF5 group displayed in bracket.
If the group does not have parent, ``(-)`` is showed.

### API Documentation
---------------------
API documentation is available on the web: [API Reference](https://wojciechwisniewski.github.io/)

### License
-----------
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
