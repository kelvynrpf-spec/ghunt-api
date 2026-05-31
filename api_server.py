from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os
import sys

app = Flask(__name__)
CORS(app)

PORT = int(os.environ.get('PORT', 5000))
GHUNT_PATH = '/app/ghunt'

@app.route('/')
def home():
    return jsonify({
        'service': 'GHunt OSINT API',
        'status': 'online',
        'endpoints': {
            'check_email': '/check/email/<email>',
            'health': '/health'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'ghunt_path': GHUNT_PATH})

@app.route('/check/email/<email>')
def check_email(email):
    """Verifica informações de um email Google"""
    try:
        # Tenta executar o GHunt
        result = subprocess.run(
            ['python3', 'check_email.py', email],
            capture_output=True,
            text=True,
            timeout=90,
            cwd=GHUNT_PATH
        )
        
        output = result.stdout + result.stderr
        
        info = {
            'email': email,
            'exists': 'exists' in output.lower() or 'found' in output.lower(),
            'raw_output': output[:2000]
        }
        
        # Tenta extrair nome
        for line in output.split('\n'):
            line_lower = line.lower()
            if 'name' in line_lower and ':' in line:
                info['name'] = line.split(':', 1)[-1].strip()
            if 'photo' in line_lower and ('http' in line or 'ggpht' in line):
                info['photo'] = line.split(':', 1)[-1].strip().split()[0]
        
        return jsonify({
            'success': True,
            'email': email,
            'data': info
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timeout - busca demorou muito'}), 408
    except Exception as e:
        return jsonify({'error': str(e), 'email': email}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
