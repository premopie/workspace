'''Przestrzeń roboczą tworzą pliki HDF5, których zawartość jest
eksponowana w interaktywnej przestrzeni nazw ipython'a.'''
import hashlib
import sys

import h5py
import numpy
from IPython import get_ipython

from workspace.variables import list_of_variables

# Interactive namespace
interactive_namespace = sys.modules['__main__']
# List of open HDF5 Files
lof = []
# List of variables created in the interactive namespace
lov = []

# Hidden attributes
hidden_attributes = ['group', 'parent', 'create']


class HDF5Files:
    '''HDF5Files is a collection of open HDF5 files which contributes to
    workspace.

    '''
    def __getitem__(self, index):
        return lof[index]

    def __iter__(self):
        return iter(lof)

    def __repr__(self):
        return '\n'.join(
            '{:2d}) {}'.format(i, repr(f)) for i, f in enumerate(lof))


class Variables:
    '''Variables is a collection of Variable instances located in the
    interactive_namespace.

    '''
    def __getitem__(self, index):
        return getattr(interactive_namespace, lov[index])

    def __iter__(self):
        return (getattr(interactive_namespace, v) for v in lov)

    def __repr__(self):
        return '\n'.join(
            '{:2d}) {}'.format(i, repr(getattr(interactive_namespace, v)))
            for i, v in enumerate(lov))

# class Variables:
#     '''Variables is a collection of Variable instances located in the
#     interactive_namespace.

#     '''
#     def __getitem__(self, index):
#         return lov[index]

#     def __iter__(self):
#         return iter(lov)

#     def __repr__(self):
#         return '\n'.join(
#             '{:2d}) {}'.format(i, repr(var)) for i, var in enumerate(lov))


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
        for key in keys:
            d += numpy.array(group.attrs[key]).tobytes()

    return hashlib.sha1(d).hexdigest()


def get(group, default=True):
    '''get(group, default=True)

    By default get name of the variable associated with group,
    otherwise get variable itself, i.e. its instance.

    '''
    for name in lov:
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


# def link(group, parent=None):

#     if parent:
#         parent = getattr(interactive_namespace, parent.name[1:])

#     setattr(interactive_namespace,
#             group.name[1:],
#             globals()[group.attrs['type']](group, parent))

#     lov.append(getattr(interactive_namespace, group.name[1:]))

#     return group

def link(group, parent=None):

    if parent:
        parent = get(group, False)

    name = unify_name(group.name[1:])

    setattr(interactive_namespace, name,
            globals()[group.attrs['type']](group, parent))

    lov.append(name)

    return group


def unify_name(name):
    return name


# I.  W Pythonie dla danego scope nazwy atrybutów są niepowtarzalne
#     (nie można w tym samym czasie utworzyć dwóch różnych obiektów o
#     tej samej nazwie). Zatem, do identyfikacji instancji klas
#     Variable i jej pochodnych wykorzystane zostaną nazwy
#     atrybutów.

# II. Nie wolno utworzyć instancji o zadanym atrybucie, jeżeli atrybut
#     ten został już utworzony wcześniej (do zmiany w przyszłości).
def update():

    # Na wypadek, gdy dodano nowy zasób należy przebudować wszystkie grupy
    for v in lov:
        # Komendę "xdel" można zastąpić komendą "reset_selective",
        # która generuje prośbę o potwierdzenie.
        get_ipython().run_line_magic('xdel', v)
    lov.clear()

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


# Dataset nie powinien posiadać atrybutów, gdyż nie będą one dostępne
# poprzez tradycyjną notację.
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
        return 'Variable {} {} from {}'.format(
            get(self.group),
            '(' + get(self.parent.group) + ')' if self.parent else '(-)',
            repr(self.group.file))

    # def __repr__(self):
    #     return 'Variable {} {} from {}'.format(
    #         self.group.name[1:],
    #         '(' + self.parent.group.name[1:] + ')' if self.parent else '(-)',
    #         repr(self.group.file))


class Variable(Group):

    '''Each instance of the Variable class is paired with an associated
    HDF5 *root group* and exposes convinient interface for it.

    '''
    def match(self):
        return self.group.attrs['parent'] == fingerprint(self.parent)

    def remove(self):
        '''remove()

        From HDF5 file remove group paired with this variable.

        '''
        del(self.group.parent[self.group.name[1:]])
        update()

    def rename(self, name):
        self.group.move(self.group.name, '/' + name)
        update()


embedded_keys = [k for k in vars(type('EmptyClass', tuple(), dict()))]
# http://stackoverflow.com/questions/22609272/python-typename-bases-dict
for cls in list_of_variables:
    vars()[cls.__name__] = type(
        cls.__name__,
        (Variable, ),
        {k: v for k, v in vars(cls).items() if v not in embedded_keys})
