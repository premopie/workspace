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

# Compression settings
compression = {'chunks': True, 'compression': "lzf", 'shuffle': True}


class HDF5Files:
    """
    Serves as an interface for the list of open HDF5 files.
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
    Serves as an interface for the list of created variables.
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
    """fingerprint(obj=None)
    
    Generates 40B SHA1 digest from data of the specified object.
    
    Allowed object types:
    
    - HDF5 group
    
    - IVar class
    
    - None
    
    Parameters
    ----------
    obj : {None|Ivar class|HDF5 group}
        Object available in the interactive namespace. 
        
    Returns
    -------
    **string**
        40B SHA1 hexadecimal digest.
    """
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
    """get(group, default=True)
    
    By default get name of the variable associated with group,
    otherwise get variable itself, i.e. its instance.
    
    Parameters
    ----------
    group : obj
        Specified HDF5 group.
    default : bool
        Indicates whether this method additionally returns instance of the variable associated with group.
            
    Returns
    -------
    name : string
        Name of the variable associated with specified HDF5 group.
    """
    for name in lon:
        if group == getattr(interactive_namespace, name).group:
            return name if default else getattr(interactive_namespace, name)
    else:
        return


def index(obj):
    """index(obj)
    
    Returns an index of the specified object(s).
    
    Allowed object types:
    
    - index or range of indexes (int or slice)
    
    - HDF5 file name (string)
    
    - h5py file object

    Parameters
    ----------
    obj : {int|slice|string|h5py file object}
        Object available in the interactive namespace.
        
    Returns
    -------
    index : int
        Index of specified object.
    """
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
    """Contains low-level mechanisms for handling groups in HDF5.
    """
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
            for key in compression:
                print('klucz={}, wartosc={}'.format(key, compression[key]))
            self.group.create_dataset(name, data=value, **compression)

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
    """Each instance of the Variable class is paired with an associated
    HDF5 *root group* and exposes convenient interface for it.
    """
    def match(self):
        """match()
        
        Checks whether parent of group associated with specified variable has been modified.
        
        Returns
        -------
        **bool**
            ``True`` if there are no changes to parent of specified group, ``False`` otherwise.
        
        Examples
        ---------
        Add example variable (named ``var1``) to the HDF5 file with index = -1 on the list of files::
        
        >>> <interface_name>[-1].create.basic("var1")
        
        In variable ``var1`` create dataset named ``dset1``, which contains some numerical data::
        
        >>> var1.data.dset1 = [1,2,3,4]
        
        Create second variable named ``var2``, as a children of ``var1``::
        
        >>> <interface_name>[-1].create.basic("var2",var1)
        
        As for now, if we call ``match()`` method on ``var2``, it will return True, as the ``var1`` is up-to-date::
        
        >>> var2.match()
        
        **True**
        
        If ``var1`` will be modified (i.e. by adding another dataset to it, named ``dset2``)::
        
        >>> var1.data.dset2 = [2,4,6,8]
        
        Then ``var1`` variable will not be up-to-date, and ``match()`` method called on ``var2`` will return false::
        
        >>> var2.match()
        
        **False**
        """
        return self.group.attrs['parent'] == fingerprint(self.parent)

    def remove(self):
        """remove()

        Removes variable from the interactive namespace and removes group paired with this variable from the HDF5 file.
        
        Examples
        ---------
        Add example variable (named ``var1``) to the HDF5 file with index = -1 on the list of files::
        
        >>> <interface_name>[-1].create.basic("var1")
        
        Remove ``var1``, by calling ``remove()`` method on it::
        
        >>> var1.remove()
        """
        del(self.group.parent[self.group.name[1:]])
        update()

    def rename(self, name):
        """rename(name)
        Renames variable in the interactive namespace and HDF5 group associated to it.
        
        Parameters
        ----------
        name : str
            New name of the HDF5 group.
        
        Examples
        ---------
        Add example variable (named ``var1``) to the HDF5 file with index = -1 on the list of files::
        
        >>> <interface_name>[0].create.basic("var1")
        
        Rename ``var1`` to ``var2``, by calling ``rename()`` method on it::
        
        >>> var1.rename("var2")
        """
        self.group.move(self.group.name, '/' + name)
        update()


embedded_keys = [k for k in vars(type('EmptyClass', tuple(), dict()))]
# http://stackoverflow.com/questions/22609272/python-typename-bases-dict
for cls in list_of_variables:
    vars()[cls.__name__] = type(
        cls.__name__,
        (Variable, ),
        {k: v for k, v in vars(cls).items() if v not in embedded_keys})
