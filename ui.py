import workspace.api


class Create:

    def __init__(self, obj):
        self._obj = obj

for cls in workspace.variables:
    setattr(Create,
            cls.__name__.lower(),
            getattr(workspace.api, workspace.create_fcn_name(cls)))


class Resource:

    def __init__(self, obj):
        self._obj = obj
        self.create = Create(obj)

    def close(self):
        workspace.api.close(self._obj)

    def flush(self):
        workspace.api.flush(self._obj)


class Interface:

    def __call__(self):
        workspace.api.list_variables()

    def __getitem__(self, obj=-1):
        return Resource(obj)

    def add(self, filename, mode='a'):
        workspace.api.add(filename, mode)

    def clear(self):
        workspace.api.clear()

    def pool(self):
        workspace.api.list_files()

    def vars(self):
        workspace.api.list_variables()
