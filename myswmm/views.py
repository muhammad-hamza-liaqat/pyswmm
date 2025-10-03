import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pyswmm import Simulation
from rest_framework.permissions import IsAuthenticated


class RunSWMMAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        input_dir = os.path.join(settings.MEDIA_ROOT, "input")
        output_dir = os.path.join(settings.MEDIA_ROOT, "output")
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        input_file_path = os.path.join(input_dir, uploaded_file.name)
        with open(input_file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        try:
            with Simulation(input_file_path) as sim:
                for step in sim:
                    pass

            output_file_path = os.path.join(output_dir, "report.json")
            with open(output_file_path, "w") as f:
                f.write("{\"status\": \"Simulation complete\"}")

            return Response({
                "message": "Simulation completed successfully",
                "input_file": input_file_path,
                "output_file": output_file_path
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
