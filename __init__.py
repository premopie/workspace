"""
Workspace: python module for handling HDF5 variables
====================================================


Main features
-------------

- Provides a set of tools for handling variables, i.e. objects being
  instances of the ``Variable`` class.

- Variables are created by default in the ``__main__`` module.

- When running in IPython, variables are available through the
  interactive namespace.

- Each variable is paired with an associated HDF5 root group and
  exposes convinient interface for it.

- Created variables are stored in the HDF5 binary data format.

- Explore variables using tab completion mechanism. For IPython it is
  recommended to have greedy completion enabled.
"""
import hashlib
import sys

import h5py
import numpy
from IPython import get_ipython

from workspace.variables import list_of_variables

# Interactive namespace
interactive_namespace = sys.modules['__main__']
# List of open HDF5 files
lof = []
# List containing names of created variables
lon = []

# Hidden attributes
hidden_attributes = ['group', 'parent', 'create']


class HDF5Files:
    """
    Serves as an interface for list of open HDF5 files.
    """
    def __getitem__(self, index):
        return lof[index]

    def __iter__(self):
        return iter(lof)

    def __repr__(self):
        return '\n'.join(
            '{:2d}) {}'.format(i, repr(f).replace('<', '').replace('>', ''))
            for i, f in enumerate(lof))


class Variables:
    '''
    Serves as an interface for list of created variables.
    '''
    def __getitem__(self, index):
        return getattr(interactive_namespace, lon[index])

    def __iter__(self):
        return (getattr(interactive_namespace, name) for name in lon)

    def __repr__(self):
        return '\n'.join(
            '{:2d}) {}'.format(i, repr(getattr(interactive_namespace, name)))
            for i, name in enumerate(lon))


def create_fcn_name(cls):
    return 'create_' + cls.__name__.lower()


def fingerprint(obj=None):
    # Są trzy możliwości:
    # a) obj to grupa hdf5
    # b) obj to klasa IVar
    # c) obj to None
    if obj is None:
        return 40*'0'
    elif isinstance(obj, Group):
        group = obj.data.group
    else:
        group = obj['data']

    d = bytes()

    keys = list(group)
    keys.sort()
    for key in keys:
        d += numpy.array(group[key]).tobytes()

    if hasattr(group, 'attrs'):

        keys = list(group.attrs)
        keys.sort()
        for key in keys:
            d += numpy.array(group.attrs[key]).tobytes()

    return hashlib.sha1(d).hexdigest()


def get(group, default=True):
    '''get(group, default=True)

    By default get name of the variable associated with group,
    otherwise get variable itself, i.e. its instance.

    '''
    for name in lon:
        if group == getattr(interactive_namespace, name).group:
            return name if default else getattr(interactive_namespace, name)
    else:
        return


def index(obj):
    '''index(obj)

    Dopuszcza się następujące typy zmiennej obj:
    - int lub slice, czyli indeks lub zakres indeksów z puli zasobów;
    - str oznaczający nazwę zasobu (pliku) HDF 5;
    - obiekt typu h5py file object.

    '''
    if type(obj) is int or type(obj) is slice:
        index = obj
    elif type(obj) is h5py._hl.files.File:
        index = lof.index(obj)
    # Wyznacz obj na podstawie nazwy pliku
    elif type(obj) is str:
        for index, f in enumerate(lof):
            if obj == f.filename.split('/')[-1]:
                break
    try:
        lof[index]
        return index
    except IndexError:
        raise IndexError(
            "There is no HDF5 file associated with index {}!".format(index))


def link(group, parent=None):

    if parent:
        parent = get(parent, False)

    name = unify_name(group.name[1:])

    setattr(interactive_namespace, name,
            globals()[group.attrs['type']](group, parent))

    lon.append(name)

    return group


def unify_name(name):
    return name


def update():

    # Na wypadek, gdy dodano nowy zasób należy przebudować wszystkie grupy
    try:
        for name in lon:
            # Komendę "xdel" można zastąpić komendą "reset_selective",
            # która generuje prośbę o potwierdzenie.
            get_ipython().run_line_magic('xdel', name)
    except AttributeError:
        for name in lon:
            delattr(interactive_namespace, name)
    lon.clear()

    # "G": lista wszystkich grup dostępnych w zasobach, tworząca
    #      graf zwany lasem
    # "C": zbiór grup posiadających rodziców
    # "P": zbiór korzeni lub liści
    G = set()
    for f in lof:
        G.update(f.values())

    # h odwzorowanie g -> fingerprint(g)
    h = {g: fingerprint(g) for g in G}

    # Wyznacz grupy ze środka drzewa (posiadające rodziców) ...
    C = {g for p in G for g in G if h[p] == g.attrs['parent']}
    # ... oraz pozostałe grupy (tj.: korzenie - grupy bez rodziców
    # i wierzchołki autonomiczne - nie powiązane z żadną grupą)
    P = G - C

    # Dowiąż korzenie i liście
    for g in P:
        link(g)

    # Dowiąż grupy (wierzchołki) ze środka drzewa
    while C:
        P = {link(g, p) for p in P
             for g in C if h[p] == g.attrs['parent']}
        C = C - P


class Group:

    def __init__(self, group, parent=None):
        super().__setattr__('group', group)
        # Na poziomie zasobów hdf5 parent to 40 znakowy string. Na
        # poziomie pythona parent to klasa rodzica lub None, jeżeli
        # nie ma rodzica
        super().__setattr__('parent', parent)

    def __dir__(self):
        return list(self.group) + list(self.group.attrs) + list(
            att for att in super().__dir__() if not att.startswith('_')
            and att not in hidden_attributes)

    # http://stackoverflow.com/questions/3644545/pythons-getattr-gets-called-twice
    def __getattr__(self, name):
        if name in self.group.attrs:
            return self.group.attrs[name]
        elif name in self.group:
            if type(self.group[name]) is h5py._hl.group.Group:
                return Group(self.group[name])
            else:
                # Zwróć (nieopakowany) dataset
                return self.group[name]
        else:
            raise AttributeError(
                "'{}' object has no attribute '{}'".format(self, name))

    def __setattr__(self, name, value):
        if name in self.group.attrs:
            self.group.attrs[name] = value
        elif name in self.group:
            self.group[name] = value
        else:
            self.group.create_dataset(name, data=value)

    def __repr__(self):
        if isinstance(self, Variable):
            return 'Variable {} {} from {} in {}'.format(
                get(self.group),
                '(' + get(self.parent.group) + ')' if self.parent else '(-)',
                repr(self.group).replace('<', '').replace('>', ''),
                repr(self.group.file).replace('<', '').replace('>', ''))
        else:
            return '{} in {}'.format(
                repr(self.group).replace('<', '').replace('>', ''),
                repr(self.group.file).replace('<', '').replace('>', ''))


class Variable(Group):

    '''
    Notes
    ------
    Each instance of the Variable class is paired with an associated
    HDF5 *root group* and exposes convinient interface for it.

    '''
    def match(self):
        return self.group.attrs['parent'] == fingerprint(self.parent)

    def remove(self):
        '''remove()
        Removes associated HDF5 group.
        Method called on specified variable in the workspace. 
        
        Examples
        ---------
        Add example variable (named "E") to the HDF5 file with index = 0 in the workspace::
    
        >>> <workspace_name>[0].create.basic("E")
        
        Remove "E", by calling remove() method on it::
        
        >>> E.remove()
        '''

        del(self.group.parent[self.group.name[1:]])
        update()

    def rename(self, name):
        '''rename(name)
        Renames associated HDF5 group.
        Method called on specified variable in the workspace.
        
        Parameters
        ----------
        name : str
            New name of the HDF5 group.
    
        Examples
        ---------
        Add example variable (named "E") to the HDF5 file with index = 0 in the workspace::
    
        >>> <workspace_name>[0].create.basic("E")
        
        Rename "E" to "Z", by calling rename() method on it::
        
        >>> E.rename("Z")
        '''

        self.group.move(self.group.name, '/' + name)
        update()


embedded_keys = [k for k in vars(type('EmptyClass', tuple(), dict()))]
# http://stackoverflow.com/questions/22609272/python-typename-bases-dict
for cls in list_of_variables:
    vars()[cls.__name__] = type(
        cls.__name__,
        (Variable, ),
        {k: v for k, v in vars(cls).items() if v not in embedded_keys})
