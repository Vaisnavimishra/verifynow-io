"""
Kafka producer used to hand off verification work to background worker(s),
so the HTTP request returns immediately instead of blocking on a multi-second
web-search-grounded LLM call.

When KAFKA_ENABLED=false (e.g. simple local dev without a broker running),
the API process runs the same verification pipeline as an in-process asyncio
background task instead. This is a deliberate, documented fallback for local
development -- the default and production path (docker-compose) always uses
Kafka. Either way, the verification logic executed is identical and real;
only the dispatch mechanism differs.
"""
import json
import logging

from aiokafka import AIOKafkaProducer

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_producer: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await _producer.start()
    return _producer


async def stop_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None


async def publish_verification_task(request_id: str) -> None:
    producer = await get_producer()
    await producer.send_and_wait(
        settings.KAFKA_VERIFICATION_TOPIC, {"request_id": request_id}
    )
    logger.info("Published verification task %s to Kafka", request_id)
