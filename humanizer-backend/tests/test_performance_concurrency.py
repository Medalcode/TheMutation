import asyncio

from fastapi.testclient import TestClient

from app.limiter import _LOCAL_BUCKETS_MAX, RateLimiter
from app.main import app

client = TestClient(app)


def test_concurrencia_solicitudes_simultaneas():
    """Verifica que el backend procese múltiples peticiones concurrentes sin errores de carrera."""

    async def run_batch():
        return await asyncio.gather(
            *[asyncio.to_thread(client.post, "/api/v1/humanize", json={"texto": f"Peticion {i}"}) for i in range(20)]
        )

    respuestas = asyncio.run(run_batch())
    for r in respuestas:
        assert r.status_code in (200, 429)


def test_limiter_pruning_memoria_bajo_alta_carga():
    """Verifica que _prune_local_buckets mantenga la memoria acotada ante miles de IPs únicas."""
    limiter = RateLimiter(app=None, requests=100, window=60)
    now = 10000.0

    # Llenar buckets con 15,000 IPs falsas antiguas
    for i in range(15000):
        limiter._local_buckets[f"192.168.{i // 256}.{i % 256}"] = (10.0, now - 500)

    assert len(limiter._local_buckets) == 15000

    # Ejecutar purga
    limiter._prune_local_buckets(now)

    # Verificar que el diccionario se haya reducido al techo máximo permitido
    assert len(limiter._local_buckets) <= _LOCAL_BUCKETS_MAX
