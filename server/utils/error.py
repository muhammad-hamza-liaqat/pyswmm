from rest_framework.response import Response

def flatten_errors(serializer_errors: dict) -> str:
    
    messages = []
    for field, errs in serializer_errors.items():
        if isinstance(errs, list):
            messages.extend([str(e) for e in errs])
        elif isinstance(errs, dict):
            messages.append(flatten_errors(errs))
        else:
            messages.append(str(errs))
    return ". ".join(messages)

def error_response(message: str, errors: dict = None, status_code: int = 400):

    return Response({
        "success": False,
        "status": status_code,
        "message": message,
        "error": flatten_errors(errors) if errors else message
    }, status=status_code)
