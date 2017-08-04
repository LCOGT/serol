from django.shortcuts import render

class ScheduleView(APIView):
    """
    Schedule observations given a full set of observing parameters
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def post(self, request, format=None):
        ser = RequestSerializer(data=request.data)
        if not ser.is_valid(raise_exception=True):
            logger.error('Request was not valid')
            return Response(ser.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            token = request.session.get('token', False)
            if not token:
                return Response("Not authenticated with ODIN.", status=status.HTTP_401_UNAUTHORIZED)
            resp = ser.save(token=token)
            return resp
