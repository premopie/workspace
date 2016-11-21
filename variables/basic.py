import datetime


class Basic:

    @staticmethod
    def create(group, parent):
        group.attrs['type'] = 'Basic'
        group.attrs['parent'] = parent
        group.attrs['created'] = str(datetime.datetime.now()).rsplit('.')[0]
        group.attrs['modified'] = group.attrs['created']
        group.attrs['log'] = ''
        data = group.create_group('data')
