import datetime

class Basic:
    """
    Contains definition of ``Basic`` variable type.
    This type provides following attributes:
    
    - ``parent``: parent of group associated with selected variable
    
    - ``created``: datetime of variable creation
    """

    @staticmethod
    def create(group, parent):
        """
        Creates ``Basic`` variable.
        """
        
        group.attrs['type'] = 'Basic'
        group.attrs['parent'] = parent
        group.attrs['created'] = str(datetime.datetime.now()).rsplit('.')[0]
        group.attrs['modified'] = group.attrs['created']
        group.attrs['log'] = ''
        data = group.create_group('data')
