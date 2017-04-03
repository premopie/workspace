import datetime as _d
import workspace as _w

hdf5_files = _w.HDF5Files()
variables = _w.Variables()


def add(filename, mode='a'):
    """
    Creates a HDF5 file in the workspace.
    
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
    Based on **h5py.File()**.
    
    Every HDF5 file is also a HDF5 group representing the root group of the file.

    Examples
    ---------
    Add a sample file to the workspace::
    
    >>> <workspace_name>.add("example.h5")
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
    Removes all HDF5 files from the workspace.
    
    Notes
    ------
    Based on **h5py.File()**.
    
    Files are not physically deleted form hard drive.

    Examples
    ---------
    Clear current workspace::

    >>> <workspace_name>.clear()
    """

    for f in _w.lof:
        f.close()
    _w.lof.clear()
    _w.update()


def close(obj=-1):
    """close()
    Closes selected HDF5 file and removes it from the workspace.
    
    Notes
    ------
    Based on **h5py.File()**.
    
    This method does not guarantee that the file will be correctly saved. To ensure no data corruption, **HDF5File.flush()** should be called after **HDF5File.close()**.

    Examples
    ---------
    Add a sample file to the workspace::
    
    >>> <workspace_name>.add("example.h5")
        
    File *"example.h5"* is present in workspace with index 0. 
    
    In order to close this file and remove from workspace we need to call *HDF5File.close()* method on *<workspace_name>[0]* object:: 
    
    >>> <workspace_name>[0].close()
    """

    _w.lof.pop(_w.index(obj)).close()
    _w.update()


# Metoda h5py.File.close() nie gwarantuje, że zawartość bufora
# zostanie poprawnie zapisana. W tym celu należy wykonać dodatkowo
# polecenie h5py.File.flush()
# http://stackoverflow.com/questions/31287744/corrupt-files-when-creating-hdf5-files-without-closing-them-h5py
def flush(obj=-1):
    """flush()
    Forces data in HDF5File to be copied from the memory buffer and saved on the hard drive.
    
    Notes
    ------
    Based on **h5py.File()**.
    
    Examples
    ---------
    Close selected file::
        
    >>> <workspace_name>[0].close()
        
    Ensure that it's data is saved on the hard drive::
    
    >>> <workspace_name>[0].flush()
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
