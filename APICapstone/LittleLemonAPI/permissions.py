from rest_framework.permissions import BasePermission

class MenuItemPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        elif request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return request.user.is_superuser or request.user.groups.filter(name="Manager").exists()
        else:
            return False
            
class ManagerPermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.groups.filter(name="Manager").exists()
    
class CartPermissions(BasePermission):
    def has_permission(self, request, view):
        return len(request.user.groups.all()) == 0

class OrderPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return not request.user.is_superuser and not request.user.groups.exists()
        elif request.method in ('DELETE', 'PUT'):
            return request.user.is_superuser or request.user.groups.filter(name="Manager").exists()
        elif request.method == 'PATCH':
            return request.user.is_superuser or request.user.groups.exists()
        else:
            return request.user.is_authenticated
            
        
    
                    
                
    
            
