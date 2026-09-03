"""
Standalone worker process: consumes verification tasks from Kafka and runs
the real verification pipeline. Run with:

    python -m app.worker.consumer

This is the production dispatch path (see docker-compose.yml `worker` service).
"""
import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from app.config import get_settings
from app.db.session import AsyncSessionLocal
from app.services.pipeline import process_verification_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verification-worker")

settings = get_settings()


async def handle_message(request_id: str) -> None:
    async with AsyncSessionLocal() as session:
        await process_verification_request(request_id, session)


async def run() -> None:
    consumer = AIOKafkaConsumer(
        settings.KAFKA_VERIFICATION_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_CONSUMER_GROUP,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        enable_auto_commit=True,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    logger.info(
        "Worker started, listening on topic '%s' at %s",
        settings.KAFKA_VERIFICATION_TOPIC,
        settings.KAFKA_BOOTSTRAP_SERVERS,
    )
    try:
        async for msg in consumer:
            request_id = msg.value.get("request_id")
            if not request_id:
                logger.warning("Received message without request_id: %s", msg.value)
                continue
            logger.info("Processing verification request %s", request_id)
            try:
                await handle_message(request_id)
            except Exception:  # noqa: BLE001
                logger.exception("Unhandled error processing request %s", request_id)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(run())
