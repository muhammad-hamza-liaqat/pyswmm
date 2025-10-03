import os
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pyswmm import Simulation
from rest_framework.permissions import IsAuthenticated


class RunSWMMAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        unique_id = str(uuid.uuid4())
        input_file_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}.inp")

        with open(input_file_path, "wb+") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        try:
            with Simulation(input_file_path) as sim:
                for step in sim:
                    pass

            rpt_file_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}.rpt")

            original_rpt = os.path.splitext(input_file_path)[0] + ".rpt"
            if os.path.exists(original_rpt):
                os.rename(original_rpt, rpt_file_path)

            if os.path.exists(input_file_path):
                os.remove(input_file_path)

            file_url = f"{request.scheme}://{request.get_host()}/media/{unique_id}.rpt"

            return Response({
                "message": "Simulation completed successfully",
                "report_file": file_url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            if os.path.exists(input_file_path):
                os.remove(input_file_path)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
