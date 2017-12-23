class MixedPermissionsMixin(object):
    permission_classes_by_action = {}

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            '''
            If action is not specified, return default AllowAny permission
            '''
            return [permission() for permission in self.permission_classes]