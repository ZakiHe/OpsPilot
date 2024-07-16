import json
import threading

import pika
from loguru import logger

from core.server_settings import server_settings

CODE_REVIEW_EVENT = "code_review_event"


class BaseEventBus:

    def prepare_eventbus(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=server_settings.rabbitmq_host, port=server_settings.rabbitmq_port,

                                      credentials=pika.PlainCredentials(server_settings.rabbitmq_username,
                                                                        server_settings.rabbitmq_password)))
        channel = connection.channel()
        channel.exchange_declare(exchange='event_bus', exchange_type='fanout', durable=True)
        return connection, channel

    def publish(self, messages: str):
        """
        事件广播
        :param messages:
        :return:
        """
        connection, channel = self.prepare_eventbus()

        properties = pika.BasicProperties(delivery_mode=2, expiration=str(5 * 60 * 1000))

        channel.basic_publish(exchange='event_bus', routing_key='', body=messages,
                              properties=properties)
        connection.close()

    def consume(self, queue_name: str, callback_func):
        """
        事件消费
        :param queue_name:
        :param callback_func:
        :return:
        """
        connection, channel = self.prepare_eventbus()

        result = channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange='event_bus', queue=queue_name)

        def callback(ch, method, properties, body):
            try:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                obj = json.loads(body.decode())
                callback_func(obj)
            except Exception as e:
                logger.error(e)

        channel.basic_consume(result.method.queue, callback, False)
        consume_thread = threading.Thread(target=channel.start_consuming)
        consume_thread.start()