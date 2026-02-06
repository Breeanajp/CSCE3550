import time
import uuid
from cryptography.hazmat.primitives.asymmetric import rsa

class KeyManager:
    def __init__(self):
        self.keys = []

    # Generate a RSA key pair
    def generate_rsa_key(self, expiry_seconds):
        private_key = rsa.generate_private_key(
            public_exponent=65537, 
            key_size=2048,
        )
    
        # Assign a unique identifier to the key
        kid = str(uuid.uuid4())

        # Set an expiration time for the key
        exp = int(time.time()) + expiry_seconds

        # Dictionary to hold the key information
        key = {
            "kid": kid,
            "private_key": private_key,
            "public_key": private_key.public_key(),
            "expiry": exp    
        }

        self.keys.append(key)   # Add key dictionary to the list of keys
        return key  # Return the key dictionary for reference
    
    # Get all unexpired keys
    def get_unexpired_keys(self):
        current_time = int(time.time())
        return [key for key in self.keys if key['expiry'] > current_time]
    
    # Get a key by its unique identifier (kid)
    def get_key_by_kid(self, kid):
        for key in self.keys:
            if key['kid'] == kid:
                return key
        return None  # Return None if no matching key is found