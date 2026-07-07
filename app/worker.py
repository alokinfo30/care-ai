import os
import logging
from datetime import datetime
from redis import Redis

logger = logging.getLogger(__name__)


def handle_sensor_job(sensor_data: str, user_id: str, language: str = 'en'):
    """RQ job handler: debounces, batches, and processes sensor events."""
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = Redis.from_url(redis_url)
        key_last = f"last_event:{user_id}"
        key_pending = f"pending_events:{user_id}"
        now = int(datetime.utcnow().timestamp())
        debounce_secs = int(os.getenv('DEBOUNCE_SECS', '5'))

        last = r.get(key_last)
        if last and now - int(last) < debounce_secs:
            # Debounce: append to pending list for batch processing
            r.rpush(key_pending, sensor_data)
            logger.info(f"Debounced event for {user_id}; queued for batch.")
            return {'status': 'debounced'}

        # Update last event timestamp
        r.set(key_last, now, ex=300)

        # Gather pending events
        pending = []
        while True:
            item = r.lpop(key_pending)
            if not item:
                break
            pending.append(item.decode() if isinstance(item, (bytes, bytearray)) else item)

        # Aggregate sensor payloads
        if pending:
            aggregated = sensor_data + "\n" + "\n".join(pending)
        else:
            aggregated = sensor_data

        # Import here to avoid heavy imports at module load
        from app.crew import SmartphoneRobotCrew

        crew = SmartphoneRobotCrew()
        result = crew.process_sensor_data(aggregated, user_id, language)
        logger.info(f"Processed sensor job for {user_id}: {result.get('status')}")
        return result

    except Exception as e:
        logger.exception(f"Worker failed: {e}")
        return {'status': 'error', 'error': str(e)}
