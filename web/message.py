import json
import logging
import time

import google.api_core.exceptions
import google.cloud.pubsub
import redis


LOGGER = logging.getLogger(__name__)


class BaseMessage:
    def push(self, data: dict):
        raise NotImplementedError

    def polling(self, sleep: int):
        raise NotImplementedError


class CloudMessage(BaseMessage):
    BATCH_SIZE = 5

    def __init__(self, project: str, topic: str, subscription: str):
        self._topic = f'projects/{project}/topics/{topic}'
        self._subscription = f'projects/{project}/subscriptions/{subscription}'
        self._subscriber = google.cloud.pubsub.SubscriberClient()
        self._publisher = google.cloud.pubsub.PublisherClient()

    def push(self, data: dict):
        self._publisher.publish(self._topic, json.dumps(data).encode('utf-8'))

    def polling(self, sleep=3):
        while True:
            try:
                response = self._subscriber.pull(
                    self._subscription, max_messages=self.BATCH_SIZE)
            except google.api_core.exceptions.DeadlineExceeded:
                time.sleep(sleep)
                continue

            ack_ids = []

            for msg in response.received_messages:
                try:
                    yield json.loads(msg.message.data.decode())
                except Exception as e:
                    LOGGER.exception(f'Error while processing messages: {e}')
                else:
                    ack_ids.append(msg.ack_id)

            if ack_ids:
                self._subscriber.acknowledge(self._subscription, ack_ids)


class RedisMessage(BaseMessage):
    def __init__(self, host: str, port: int, db: int, channel: str):
        self._redis = redis.Redis(host=host, port=port, db=db)
        self._channel = channel

    def push(self, data: dict):
        self._redis.publish(self._channel, json.dumps(data))

    def polling(self, sleep=3):
        pubsub = self._redis.pubsub()
        pubsub.subscribe(self._channel)

        while True:
            message = pubsub.get_message()

            if message and message['type'] == 'message':
                yield json.loads(message['data'].decode('utf-8'))

            time.sleep(sleep)
