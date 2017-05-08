import datetime as _d
import workspace as _w

hdf5_files = _w.HDF5Files()
variables = _w.Variables()
compression = _w.compression


def add(filename, mode='a'):

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

    for f in _w.lof:
        f.close()
    _w.lof.clear()
    _w.update()


def close(obj=-1):
    """close(obj=-1)

    Z przetsrzeni roboczej usuń wskazany plik HDF 5 (domyślnie osatnio
    otwarty).

    Z interaktywnej przestrzeni nazw ipython'a usuń wszystkie
    dowiązania do obiektów z usuwanego zasobu i zamknij plik.

    """
    _w.lof.pop(_w.index(obj)).close()
    _w.update()


def flush(obj=-1):
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
