from pywebpush import webpush
import json

# Generate VAPID keys
# Note: pywebpush doesn't have a direct 'generate_vapid_keys' function exposed in the top level usually, 
# but we can use the `vapid` CLI functionality or `cryptography` internally.
# Actually, looking at common usage, people often use `vapid --applicationServerKey` CLI.
# But inside python, we can assume we might need to rely on the CLI or use a library helper if available.
# Let's try running the command line via subprocess as that is the official way often cited, 
# OR check if we can import the Vapid class.

try:
    # Try importing from pywebpush if they expose it
    # Older versions might not.
    # A reliable way without dealing with complex imports is just using the CLI tool that comes with it.
    import subprocess
    output = subprocess.check_output(["vapid", "--applicationServerKey"], stderr=subprocess.STDOUT).decode()
    print("KEYS_START")
    print(output.strip())
    print("KEYS_END")

except Exception as e:
    # Fallback: Generate using ecdsa library directly if vapid command fails
    # This is a bit more complex but ensures it works in python script
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        import base64

        private_key = ec.generate_private_key(ec.SECP256R1())
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )

        def to_b64(b):
            return base64.urlsafe_b64encode(b).decode('utf-8').strip('=')

        # Extracting the raw numbers for VAPID is slightly different than just PEM
        # Actually, pywebpush needs the base64url encoded public and private integer/bytes.
        # It's easier to just try to use the CLI if installed.
        print(f"ERROR: {e}")
    except ImportError:
        print("ERROR: Cryptography not installed and vapid CLI failed")
