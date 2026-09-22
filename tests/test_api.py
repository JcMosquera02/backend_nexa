from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get('/health').json()['status'] == 'ok'


def test_consent_required():
    response = client.post('/api/auth/register', json={
        'cedula': '100000002', 'nombre_completo': 'Sin Consentimiento',
        'correo': 'sin@nexa.co', 'password': 'CambioSeguro123!',
        'role': 'residente', 'consentimiento_datos': False,
    })
    assert response.status_code == 422
