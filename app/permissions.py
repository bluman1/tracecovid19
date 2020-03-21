from rest_framework import permissions

from app.models import Organization


class OrganizationPermission(permissions.BasePermission):
    """
    Global permission check for One.
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        org = Organization.objects.filter(user=request.user).exists()
        return org
