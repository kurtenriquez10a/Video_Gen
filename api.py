import jwt
import time

ACCESS_KEY = 'dd750c90da9b46d5bc59b91fa957715b'
SECRET_KEY = 'f4fac419352b4117b9956306e027acbe'

# Generate API Token
def generate_api_token():
    payload = {
        'iss': ACCESS_KEY,
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600  # Token valid for 1 hour
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Test token generation
api_token = generate_api_token()
print(f"Generated Token: {api_token}")
