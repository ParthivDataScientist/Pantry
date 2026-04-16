
import os
import base64
from pywebpush import webpush, WebPushException

# Path to keys
private_key_path = r"d:\Desktop\Pantry\private_key.pem"

def test_load_key():
    print(f"Checking private key at: {private_key_path}")
    if not os.path.exists(private_key_path):
        print("File does not exist!")
        # Try relative
        private_key_path_rel = "private_key.pem"
        if os.path.exists(private_key_path_rel):
            print(f"File exists at relative path: {private_key_path_rel}")
            path_to_use = private_key_path_rel
        else:
            return
    else:
        path_to_use = private_key_path

    with open(path_to_use, "r") as f:
        content = f.read()
        print("Key content loaded.")

    # Try to send a mock push
    sub_info = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/fake",
        "keys": {
            "p256dh": "BNcR6S9M_K69z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8K6z8=",
            "auth": "fakeauth="
        }
    }
    
    print("\n--- Testing with file path ---")
    try:
        webpush(
            subscription_info=sub_info,
            data="test",
            vapid_private_key=path_to_use,
            vapid_claims={"sub": "mailto:admin@example.com"}
        )
    except WebPushException as e:
        print(f"Expected WebPushException (fake endpoint): {e}")
    except Exception as e:
        print(f"Unexpected error with file path: {e}")


    print("\n--- Testing with Raw Base64 ---")
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        
        # Load the private key to get the raw bytes
        with open(path_to_use, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        
        # Get raw bytes (d value)
        # This is slightly complex in cryptography but we can do it
        private_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
        raw_b64 = base64.urlsafe_b64encode(private_bytes).decode('utf-8').rstrip('=')
        
        print(f"Raw Base64: {raw_b64}")
        
        webpush(
            subscription_info=sub_info,
            data="test",
            vapid_private_key=raw_b64,
            vapid_claims={"sub": "mailto:admin@example.com"}
        )
    except WebPushException as e:
        print(f"Expected WebPushException (fake endpoint): {e}")
    except Exception as e:
        print(f"Unexpected error with raw base64: {e}")

if __name__ == "__main__":
    test_load_key()
