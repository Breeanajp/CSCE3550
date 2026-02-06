import logging
from app import create_app
from waitress import serve

app = create_app()

if __name__ == "__main__":
    print("Starting server on 0.0.0.0:8080")
    
    # Enable logging for Waitress
    logging.basicConfig(level=logging.INFO)
    
    serve(app, host="0.0.0.0", port=8080)