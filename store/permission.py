def is_moderator(user):
    return user.groups.filter(name='Moderator').exists()

def is_seller(user):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.groups.filter(name='seller').exists()
    
def is_customer(user):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.groups.filter(name='customer').exists()