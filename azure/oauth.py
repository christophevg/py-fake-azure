import logging
logger = logging.getLogger(__name__)

from flask_restful import Resource

from azure.app import api

class Token(Resource):
  def post(self):
    return {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
      "expires_in": 300,
      "refresh_expires_in": 0,
      "token_type": "Bearer",
      "id_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
      "not-before-policy": 1592926207,
      "scope": "openid email user_code profile identification_type address language alias_name action_codes phone"
    }

api.add_resource( Token, "/oauth/token" )
logger.info("OAUTH fake token endpoint ready")
