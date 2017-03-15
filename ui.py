import workspace.api


class Create:

    def __init__(self, index):
        self._index = index


for cls in workspace.list_of_variables:
    setattr(Create,
            cls.__name__.lower(),
            getattr(workspace.api, workspace.create_fcn_name(cls)))


class HDF5File:

    def __init__(self, index):
        self._index = index
        self.create = Create(index)

    def __repr__(self):
        return repr(workspace.api.hdf5_files[self._index])

    def close(self):
        workspace.api.close(self._index)

    def flush(self):
        workspace.api.flush(self._index)


class Interface:

    vars = workspace.api.variables

    def __repr__(self):
        return repr(workspace.api.hdf5_files)

    def __getitem__(self, index):
        return HDF5File(index)

    def __iter__(self):
        return iter(workspace.api.hdf5_files)

    def add(self, filename, mode='a'):
        workspace.api.add(filename, mode)

    def clear(self):
        workspace.api.clear()
