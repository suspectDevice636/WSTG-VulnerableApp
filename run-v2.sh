#!/bin/bash
# Run WSTG Vulnerable App V2 with SSL support

python3 -c "
from app_v2 import app, init_db
import ssl

if __name__ == '__main__':
    init_db()
    
    # Self-signed certificate
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        ssl_context=context
    )
"
