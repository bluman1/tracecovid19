from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from app.models import Organization


class OrganizationAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            one = Organization.objects.get(user=user)
        except Organization.DoesNotExist:
            return Response(data={'error': 'You are not authorized to login.'}, status=status.HTTP_401_UNAUTHORIZED)
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            token.delete()
            token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'id': str(one.pk),
            'email': user.email,
            'name': one.name,
            'country': one.country,
            'message': one.message
        })
