from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Superuser ba admin role — duitai allow.
        return request.user and request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )

class IsFacultyUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check korchi user faculty kina.
        return request.user and request.user.is_authenticated and request.user.role == 'faculty'

class IsStudentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check korchi user student kina.
        return request.user and request.user.is_authenticated and request.user.role == 'student'
