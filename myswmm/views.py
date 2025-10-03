import os
import re
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pyswmm import Simulation
from rest_framework.permissions import IsAuthenticated


class RunSWMMAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def parse_table(self, lines, start_index):
        table = []
        for line in lines[start_index:]:
            if line.strip() == "":
                break
            cols = list(filter(None, line.strip().split()))
            if cols:
                table.append(cols)
        return table

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        input_file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(input_file_path, "wb+") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        try:
            with Simulation(input_file_path) as sim:
                for step in sim:
                    pass

            rpt_file_path = os.path.splitext(input_file_path)[0] + ".rpt"
            if not os.path.exists(rpt_file_path):
                return Response({"error": ".rpt file not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            with open(rpt_file_path, "r") as f:
                rpt_lines = f.readlines()

            data = {}

            def safe_float(val):
                try:
                    return float(val)
                except:
                    return val

            # ----------------------------
            # Subcatchment Runoff Summary
            # ----------------------------
            try:
                subcatchment_index = [i for i, line in enumerate(rpt_lines) if "Subcatchment Runoff Summary" in line][0]
                table_start = subcatchment_index + 5  # skip headers
                table = self.parse_table(rpt_lines, table_start)
                subcatchments = []
                for row in table:
                    if len(row) >= 10:
                        subcatchments.append({
                            "name": row[0],
                            "total_precip": safe_float(row[1]),
                            "total_runon": safe_float(row[2]),
                            "total_evap": safe_float(row[3]),
                            "total_infil": safe_float(row[4]),
                            "imperv_runoff": safe_float(row[5]),
                            "perv_runoff": safe_float(row[6]),
                            "total_runoff": safe_float(row[7]),
                            "peak_runoff": safe_float(row[8]),
                            "runoff_coeff": safe_float(row[9])
                        })
                data["subcatchments"] = subcatchments
            except Exception:
                data["subcatchments"] = []

            # ----------------------------
            # Node Depth Summary
            # ----------------------------
            try:
                node_index = [i for i, line in enumerate(rpt_lines) if "Node Depth Summary" in line][0]
                table_start = node_index + 4
                table = self.parse_table(rpt_lines, table_start)[2:]  # skip column headers
                nodes = []
                for row in table:
                    if len(row) >= 6:
                        nodes.append({
                            "name": row[0],
                            "type": row[1],
                            "avg_depth": safe_float(row[2]),
                            "max_depth": safe_float(row[3]),
                            "max_hgl": safe_float(row[4]),
                            "time_of_max": row[5]
                        })
                data["nodes"] = nodes
            except Exception:
                data["nodes"] = []

            # ----------------------------
            # Node Inflow Summary
            # ----------------------------
            try:
                inflow_index = [i for i, line in enumerate(rpt_lines) if "Node Inflow Summary" in line][0]
                table_start = inflow_index + 4
                table = self.parse_table(rpt_lines, table_start)[2:]
                inflows = []
                for row in table:
                    if len(row) >= 7:
                        inflows.append({
                            "name": row[0],
                            "type": row[1],
                            "max_lateral_inflow": safe_float(row[2]),
                            "max_total_inflow": safe_float(row[3]),
                            "time_of_max": row[4],
                            "total_lateral_volume": safe_float(row[5]),
                            "total_inflow_volume": safe_float(row[6]),
                        })
                data["node_inflows"] = inflows
            except Exception:
                data["node_inflows"] = []

            # ----------------------------
            # Node Flooding Summary
            # ----------------------------
            try:
                flooding_index = [i for i, line in enumerate(rpt_lines) if "Node Flooding Summary" in line][0]
                table_start = flooding_index + 4
                table = self.parse_table(rpt_lines, table_start)[2:]
                flooding = []
                for row in table:
                    if len(row) >= 6:
                        flooding.append({
                            "node": row[0],
                            "hours_flooded": safe_float(row[1]),
                            "max_rate": safe_float(row[2]),
                            "time_of_max": row[3],
                            "total_flood_volume": safe_float(row[4]),
                            "total_ponded_volume": safe_float(row[5])
                        })
                data["node_flooding"] = flooding
            except Exception:
                data["node_flooding"] = []

            # ----------------------------
            # Link Flow Summary
            # ----------------------------
            try:
                link_index = [i for i, line in enumerate(rpt_lines) if "Link Flow Summary" in line][0]
                table_start = link_index + 6
                table = self.parse_table(rpt_lines, table_start)
                links = []
                for row in table:
                    if len(row) >= 7:
                        links.append({
                            "link": row[0],
                            "type": row[1],
                            "max_flow": safe_float(row[2]),
                            "time_of_max": row[3],
                            "max_velocity": safe_float(row[4]),
                            "max_flow_ratio": safe_float(row[5]),
                            "max_depth_ratio": safe_float(row[6])
                        })
                data["links"] = links
            except Exception:
                data["links"] = []

            if os.path.exists(input_file_path):
                os.remove(input_file_path)

            return Response({
                "message": "Simulation completed successfully",
                "data": data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            if os.path.exists(input_file_path):
                os.remove(input_file_path)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
