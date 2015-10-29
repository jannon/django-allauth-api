from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from allauth_api.account.rest_framework.permissions import EmailVerified

class EmailRequiredView(APIView):
    permission_classes = [EmailVerified,]

    def get(self, request):
        return Response("OK", HTTP_200_OK)
