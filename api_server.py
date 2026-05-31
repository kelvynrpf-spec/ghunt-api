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
            'check_gaia': '/check/gaia/<gaia_id>',
            'health': '/health'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/check/email/<email>')
def check_email(email):
    """Verifica informações de um email Google"""
    try:
        result = subprocess.run(
            ['python3', f'{GHUNT_PATH}/ghunt.py', 'email', email],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=GHUNT_PATH
        )
        
        output = result.stdout
        
        # Parse do output do GHunt
        info = {
            'email': email,
            'exists': 'exists' in output.lower(),
            'raw_output': output[:1000]
        }
        
        # Extrai nome se disponível
        if 'name' in output.lower():
            for line in output.split('\n'):
                if 'name' in line.lower():
                    info['name'] = line.split(':')[-1].strip()
                    break
        
        # Extrai foto se disponível
        if 'photo' in output.lower():
            for line in output.split('\n'):
                if 'photo' in line.lower() or 'avatar' in line.lower():
                    info['photo'] = line.split(':')[-1].strip()
                    break
        
        return jsonify({
            'success': True,
            'email': email,
            'data': info
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timeout'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check/gaia/<gaia_id>')
def check_gaia(gaia_id):
    """Verifica informações por GAIA ID"""
    try:
        result = subprocess.run(
            ['python3', f'{GHUNT_PATH}/ghunt.py', 'gaia', gaia_id],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=GHUNT_PATH
        )
        
        return jsonify({
            'success': True,
            'gaia_id': gaia_id,
            'data': {
                'raw_output': result.stdout[:1000]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
