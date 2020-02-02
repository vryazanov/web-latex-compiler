import json
import logging
import queue
import time

import google.api_core.exceptions
import google.cloud.pubsub


LOGGER = logging.getLogger(__name__)


class BaseMessage:
    def push(self, data):
        raise NotImplementedError

    def polling(self, *args, **kwargs):
        raise NotImplementedError


class CloudMessage(BaseMessage):
    def __init__(self, project: str, topic: str, subscription: str):
        self._topic = f'projects/{project}/topics/{topic}'
        self._subscription = f'projects/{project}/subscriptions/{subscription}'
        self._subscriber = google.cloud.pubsub.SubscriberClient()
        self._publisher = google.cloud.pubsub.PublisherClient()

    def push(self, data: dict):
        self._publisher.publish(self._topic, bytes(json.dumps(data)))

    def polling(self, sleep=3, batch_size=5, limit=None):
        while True:
            try:
                response = self._subscriber.pull(
                    self._subscription, max_messages=batch_size)
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


class LocalMessage(BaseMessage):
    def __init__(self):
        self._queue = queue.Queue()

    def push(self, data: dict):
        self._queue.put(json.dumps(data))

    def polling(self, sleep=3):
        while True:
            if not self._queue.empty():
                yield json.loads(self._queue.get())
            time.sleep(sleep)
