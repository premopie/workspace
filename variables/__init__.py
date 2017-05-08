"""
:Object: **list_of_variables**: List of classes containing available variable types.

Adding class (which defines variable type) to this list, makes it possible to use this variable type in the Workspace.

**Notes**

This mechanism allows users to create their own variable types.

This is profitable in cases when additional custom attributes are needed.
"""

from . import basic

list_of_variables = [basic.Basic]
