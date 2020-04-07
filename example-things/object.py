class IntClass:
    ops = ['typeof', 'str', 'iter<int>']
    def get(self, field):
        return Errors.FieldNotFound(f'type `int` has no field {field.name}')