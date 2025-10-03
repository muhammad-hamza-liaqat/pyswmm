from rest_framework.response import Response

def success_response(message: str, data: dict = None, status_code: int = 200):

    return Response({
        "success": True,
        "status": status_code,
        "message": message,
        "data": data or {}
    }, status=status_code)
