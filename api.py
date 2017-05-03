"""
:Object: **variables**: List of all variables available in the interactive namespace.

Instance of ``__init__.Variables``.

:Object: **hdf5_files**: List of all HDF5 files available in the interactive namespace.

Instance of ``__init__.HDF5Files``.

"""

import datetime as _d
import workspace as _w

hdf5_files = _w.HDF5Files()
variables = _w.Variables()

def add(filename, mode='a'):
    """
    Creates or opens a HDF5 file on the hard drive and adds it to the interactive namespace.
    
    Parameters
    ----------
    filename : str
        Name of the HDF5 file.
    mode : str, optional
        Mode in which to open file, one of ('r', 'r+', 'w', 'w-', 'x', 'a').
        
        +------------+----------------------------------------------------------+
        | **r**      | Readonly, file must exist                                |
        +------------+----------------------------------------------------------+
        | **r+**     | Read/write, file must exist                              |
        +------------+----------------------------------------------------------+
        | **w**      | Create file, truncate if exists                          |
        +------------+----------------------------------------------------------+
        | **w- or x**| Create file, fail if exists                              |
        +------------+----------------------------------------------------------+
        | **a**      | Read/write if exists, create otherwise (**default**)     |
        +------------+----------------------------------------------------------+
        
    Notes
    ------
    Based on ``h5py.File()``.
    The root group is automatically created when the HDF5 file is created.

    Examples
    ---------
    Add a sample file to the interactive namespace::
    
    >>> <interface_name>.add("example.h5")
    """

    if mode == 'w':                                         
        mode == 'w-'

    # Ponowne otwarcie uprzednio otwartego pliku nie generuje
    # błędu
    f = _w.h5py.File(filename, mode)
    # Usuń i dodaj aby elementy listy lof występowały w
    # kolejności dodawania plików do zasobów
    if f in _w.lof:
        _w.lof.remove(f)
    _w.lof.append(f)

    _w.update()


def clear():
    """
    Closes all open HDF5 files and removes them from the interactive namespace.
    Files are not physically deleted form the hard drive, but rather deleted from current interactive namespace.
    
    Notes
    ------
    Based on ``h5py.File()``.
    

    Examples
    ---------
    Clears current interactive namespace::

    >>> <interface_name>.clear()
    """

    for f in _w.lof:
        f.close()
    _w.lof.clear()
    _w.update()


def close(obj=-1):
    """close(obj=-1)
    Closes HDF5 file with selected index and removes it from the interactive namespace.
    The default index is minus one, which means the last item on the list of files.
    
    Notes
    ------
    Based on ``h5py.File()``.
    
    This method does not guarantee that the file will be correctly saved. To ensure no data corruption, ``api.flush()`` should be called after ``api.close()``.

    Examples
    ---------
    Add a sample file to the interactive namespace::
    
    >>> <interface_name>.add("example.h5")
        
    File *"example.h5"* is present in interactive namespace with index = -1. 
    
    In order to close this file and remove from the interactive namespace we need to call ``api.close()`` method on ``<interface_name>[file_index]`` file object:: 
    
    >>> <interface_name>[-1].close()
    """
    
    
    _w.lof.pop(_w.index(obj)).close()
    _w.update()


def flush(obj=-1):
    """flush(obj=-1)
    Forces data in HDF5 file to be copied from the memory buffer and saved on the hard drive.
    The default index is minus one, which means the last item on the list of files.
    
    Notes
    ------
    Based on ``h5py.File()``.
    
    Examples
    ---------
    Close selected file::
        
    >>> <interface_name>[file_index].close()
        
    Ensure that it's data is saved on the hard drive::
    
    >>> <interface_name>[file_index].flush()
    """

    _w.lof[_w.index(obj)].flush()


def _template(cls):

    def create_variable(obj=-1, name=None, parent=None):

        try:
            f = _w.lof[_w.index(obj._index)]
        except AttributeError:
            f = _w.lof[_w.index(obj)]

        if not name:
            name = cls.__name__.lower()[0] + str(
                _d.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

        cls.create(f.create_group(name), _w.fingerprint(parent))

        _w.update()

        return getattr(_w.interactive_namespace, name)

    return create_variable


for _cls in _w.list_of_variables:
    vars()[_w.create_fcn_name(_cls)] = _template(_cls)
