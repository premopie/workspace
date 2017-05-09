import workspace.api


class Create:

    def __init__(self, index):
        self._index = index


for cls in workspace.list_of_variables:
    setattr(Create,
            cls.__name__.lower(),
            getattr(workspace.api, workspace.create_fcn_name(cls)))


class HDF5File:
    """
    Imports functions from api.py and serves as an interface for end user.
    """
    def __init__(self, index):
        self._index = index
        self.create = Create(index)

    def __repr__(self):
        return repr(workspace.api.hdf5_files[self._index])

    def close(self):
        """
        Alias of ``api.close()``.
        """
        workspace.api.close(self._index)

    def flush(self):
        """
        Alias of ``api.flush()``.
        """
        workspace.api.flush(self._index)


class Interface:
    """
    Imports functions from api.py and serves as an interface for end user.

    :Object: **vars**: List of all variables available in the interactive namespace.
    
    :Object: **compression**: Dictionary that contains dataset compression parameters.
    """
    vars = workspace.api.variables
    compression = workspace.api.compression
    
    def __repr__(self):
        return repr(workspace.api.hdf5_files)

    def __getitem__(self, index):
        return HDF5File(index)

    def __iter__(self):
        return iter(workspace.api.hdf5_files)

    def add(self, filename, mode='a'):
        """
        Alias of ``api.add()``.
        """
        workspace.api.add(filename, mode)

    def clear(self):
        """
        Alias of ``api.clear()``.
        """
        workspace.api.clear()
