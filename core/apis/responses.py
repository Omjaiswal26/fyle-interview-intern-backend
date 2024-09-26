from flask import jsonify, make_response

class APIResponse:
    @classmethod
    def respond(cls, data=None, message=None, status_code=200):
        response_data = {
            "status_code": status_code,
            "data": data,
            "message": message  # Include a message for all responses
        }
        return make_response(jsonify(response_data), status_code)
    @classmethod
    def error(cls, message, status_code=400, error=None):
        response_data = {
            "message": message,
            "status_code": status_code
        }
        if error is not None:
            response_data["error"] = error
        return make_response(jsonify(response_data), status_code)
