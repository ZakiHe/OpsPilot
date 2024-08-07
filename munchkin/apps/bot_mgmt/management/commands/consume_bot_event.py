import datetime
import json

import pika
from apps.bot_mgmt.models import Bot, BotConversationHistory
from apps.channel_mgmt.models import Channel, ChannelUser, ChannelUserGroup, CHANNEL_CHOICES
from django.core.management import BaseCommand
from loguru import logger
from wechatpy.enterprise import WeChatClient
from munchkin.components.conversation_mq import (
    CONVERSATION_MQ_HOST,
    CONVERSATION_MQ_PASSWORD,
    CONVERSATION_MQ_PORT,
    CONVERSATION_MQ_USER,
)

user_channels = {}


def on_message(channel, method_frame, header_frame, body):
    try:
        message = json.loads(body.decode())

        if "text" in message:
            sender_id = message["sender_id"]
            if "input_channel" in message:
                input_channel = message["input_channel"]
                user_channels[sender_id] = message["input_channel"]
            else:
                input_channel = user_channels[sender_id]

            assistant_id = message["metadata"]["assistant_id"]

            logger.debug(f"用户ID:[{sender_id}] BotID:[{assistant_id}] 通道:[{input_channel}] 消息:{message}")

            bot = Bot.objects.get(assistant_id=assistant_id)

            channel_obj = Channel.objects.get(name=input_channel)
            channel_user_exists = ChannelUser.objects.filter(
                user_id=sender_id, channel_user_group__channel=channel_obj
            ).exists()
            channel_user_group = ChannelUserGroup.objects.get(channel=channel_obj, owner=bot.owner,
                                                              name="默认用户组")

            if channel_user_exists is False:
                logger.info(f"用户[{sender_id}]在[{channel_obj.name}]中不存在,创建用户,并加入默认用户组")

                if channel_obj.channel_type == CHANNEL_CHOICES.ENTERPRISE_WECHAT:
                    conf = channel_obj.decrypted_channel_config

                    wechat_client = WeChatClient(
                        conf['channels.enterprise_wechat_channel.EnterpriseWechatChannel']['corp_id'],
                        conf['channels.enterprise_wechat_channel.EnterpriseWechatChannel']['secret'],
                    )
                    wechat_username = wechat_client.user.get(sender_id)['name']
                    ChannelUser.objects.create(channel_user_group=channel_user_group, owner=bot.owner,
                                               user_id=sender_id, name=wechat_username)
                else:
                    ChannelUser.objects.create(channel_user_group=channel_user_group, owner=bot.owner,
                                               user_id=sender_id)

            channel_user = ChannelUser.objects.filter(user_id=sender_id, channel_user_group=channel_user_group,
                                                      owner=bot.owner).first()

            # 创建对话历史
            created_at = datetime.datetime.fromtimestamp(message["timestamp"], tz=datetime.timezone.utc)
            logger.debug(
                f'写入消息，完整信息如下: bot={bot}, user={channel_user}, created_at={created_at}, conversation_role={message["event"]}, conversation={message["text"]}'
            )

            BotConversationHistory.objects.get_or_create(
                bot=bot,
                user=channel_user,
                created_at=created_at,
                owner=bot.owner,
                conversation_role=message["event"],
                conversation=message["text"],
            )
    except Exception as e:
        logger.error(f"消息处理失败:{e}")
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


class Command(BaseCommand):
    help = "获取对话历史"

    def handle(self, *args, **options):

        logger.info(f"初始化消息队列连接:[{CONVERSATION_MQ_HOST}:{CONVERSATION_MQ_PORT}]")

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=CONVERSATION_MQ_HOST,
                port=CONVERSATION_MQ_PORT,
                credentials=pika.PlainCredentials(CONVERSATION_MQ_USER, CONVERSATION_MQ_PASSWORD),
            )
        )
        channel = connection.channel()
        channel.basic_consume("pilot", on_message)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        connection.close()
