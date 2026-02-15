from flask import Blueprint, jsonify, request
from .keys import KeyManager
import time
import jwt

main = Blueprint('main', __name__)
keymanager = KeyManager()

keymanager.generate_rsa_key(expiry_seconds=3600)  # Generate a key that expires in 1 hour
keymanager.generate_rsa_key(expiry_seconds=-3600)  # Generate a key that is expired 1 hour ago

# Convert RSA keys to JWK format for JWKS endpoint
def rsa_key_to_jwk(key):
    public_key = key['public_key']
    numbers = public_key.public_numbers()
    return {
        "kty": "RSA",
        "kid": key['kid'],
        "use": "sig",
        "alg": "RS256",
        "n": jwt.utils.base64url_encode(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")).decode(),
        "e": jwt.utils.base64url_encode(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")).decode()
    }

# Root endpoint to check if the server is running    
@main.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok"}), 200

# Log each request method, path, and response status
@main.after_request
def log_request(response):
    print(f"{request.method} {request.path} -> {response.status}")
    return response
   
# Endpoint to serve the public keys in JWKS format
@main.route("/.well-known/jwks.json", methods=['GET'])
def jwks():
    unexpiredKeys = keymanager.get_unexpired_keys()
    keys = {"keys": [rsa_key_to_jwk(key) for key in unexpiredKeys]}
    return jsonify(keys)

# Endpoint to get the list of unexpired keys signed JWT on a POST request
@main.route('/auth', methods=['POST'])
def get_keys():
    expired_param = request.args.get("expired", "false").lower() == "true"

    # Choose the correct key based on expired_param
    if expired_param:
        key = next((k for k in keymanager.keys if k['expiry'] < int(time.time())), None)
    else:
        key = next((k for k in keymanager.get_unexpired_keys()), None)

    if not key:
        return jsonify({"error": "No suitable key found"}), 500
    
    payload = {
        "sub": "fake-user",
        "iat": int(time.time()),
        "exp": key['expiry']
    }

    token = jwt.encode(
        payload,
        key['private_key'],
        algorithm="RS256",
        headers={"kid": key['kid']}
    )

    return jsonify({"token": token})