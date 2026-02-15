from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check korchi user authenticated ar admin kina.
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsFacultyUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check korchi user faculty kina.
        return request.user and request.user.is_authenticated and request.user.role == 'faculty'

class IsStudentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check korchi user student kina.
        return request.user and request.user.is_authenticated and request.user.role == 'student'
