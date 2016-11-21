import datetime as _d
import workspace as _w


def add(filename, mode='a'):

    if mode == 'w':
        mode == 'w-'

    # Ponowne otwarcie uprzednio otwartego pliku nie generuje
    # błędu
    f = _w.h5py.File(filename, mode)
    # Usuń i dodaj aby elementy listy pool występowały w
    # kolejności dodawania plików do zasobów
    if f in _w.pool:
        _w.pool.remove(f)
    _w.pool.append(f)

    _w.update()


def clear():
    for f in _w.pool:
        f.close()
    _w.pool.clear()
    _w.update()


def close(obj=-1):
    """close(obj=-1)

    Z przetsrzeni roboczej usuń wskazany plik HDF 5 (domyślnie osatnio
    otwarty).

    Z interaktywnej przestrzeni nazw ipython'a usuń wszystkie
    dowiązania do obiektów z usuwanego zasobu i zamknij plik.

    """
    _w.pool.pop(_w.index(obj)).close()
    _w.update()


# Metoda h5py.File.close() nie gwarantuje, że zawartość bufora
# zostanie poprawnie zapisana. W tym celu należy wykonać dodatkowo
# polecenie h5py.File.flush()
# http://stackoverflow.com/questions/31287744/corrupt-files-when-creating-hdf5-files-without-closing-them-h5py
def flush(obj=-1):
    _w.pool[_w.index(obj)].flush()


def list_files():
    print('\n'.join('{:2d}) {}\t {}'.format(i, f.filename, f.mode)
                    for i, f in enumerate(_w.pool)))


def list_variables():
    print('\n'.join('{:2d}) {} {} in {}'.format(i, l[0], p, l[1])
                    for i, l, p in
                    zip(range(len(_w.links)), _w.links,
                        (

                            '(' + getattr(_w.interactive_namespace,
                                          l[0]).parent.group.name[1:] + ')'
                            if
                            getattr(_w.interactive_namespace, l[0]).parent
                            else '(-)' for l in _w.links

                        ))))


def _template(cls):

    def create_variable(obj=-1, name=None, parent=None):

        try:
            f = _w.pool[_w.index(obj._obj)]
        except AttributeError:
            f = _w.pool[_w.index(obj)]

        if not name:
            name = cls.__name__.lower()[0] + str(
                _d.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

        cls.create(f.create_group(name), _w.fingerprint(parent))

        _w.update()

    return create_variable

for _cls in _w.variables:
    vars()[_w.create_fcn_name(_cls)] = _template(_cls)
