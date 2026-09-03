from http import HTTPStatus


class StatusCode:
    OK = HTTPStatus.OK.value                                  # 200
    CREATED = HTTPStatus.CREATED.value                        # 201
    ACCEPTED = HTTPStatus.ACCEPTED.value                      # 202
    NO_CONTENT = HTTPStatus.NO_CONTENT.value                  # 204

    BAD_REQUEST = HTTPStatus.BAD_REQUEST.value                # 400
    UNAUTHORIZED = HTTPStatus.UNAUTHORIZED.value              # 401
    FORBIDDEN = HTTPStatus.FORBIDDEN.value                    # 403
    NOT_FOUND = HTTPStatus.NOT_FOUND.value                    # 404
    METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED.value  # 405
    CONFLICT = HTTPStatus.CONFLICT.value                      # 409
    UNPROCESSABLE_ENTITY = HTTPStatus.UNPROCESSABLE_ENTITY.value  # 422
    TOO_MANY_REQUESTS = HTTPStatus.TOO_MANY_REQUESTS.value    # 429

    INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR.value  # 500
    NOT_IMPLEMENTED = HTTPStatus.NOT_IMPLEMENTED.value              # 501
    BAD_GATEWAY = HTTPStatus.BAD_GATEWAY.value                      # 502
    SERVICE_UNAVAILABLE = HTTPStatus.SERVICE_UNAVAILABLE.value      # 503
    GATEWAY_TIMEOUT = HTTPStatus.GATEWAY_TIMEOUT.value              # 504