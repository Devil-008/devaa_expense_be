from flask import jsonify

def api_response(status_code: int, is_success: bool, message: str, data=None):
    """Standardized API response formatter."""
    response_body = {
        "status_code": status_code,
        "is_success": is_success,
        "message": message,
        "data": data
    }
    return jsonify(response_body), status_code