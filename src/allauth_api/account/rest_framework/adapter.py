from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED


class AccountAdapterMixin(object):
    def new_user_response(self, user):
        serializer_class = self.new_user_serializer()
        return_data = None
        if serializer_class:
            return_data = serializer_class(instance=user).data
        return Response(return_data, HTTP_201_CREATED)

    def new_user_serializer(self, user):
        return None
