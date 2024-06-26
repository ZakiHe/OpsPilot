from apps.bot_mgmt.models import Bot
from apps.bot_mgmt.serializers import BotSerializer
from rest_framework.viewsets import ModelViewSet


class BotViewSet(ModelViewSet):
    serializer_class = BotSerializer
    queryset = Bot.objects.all()
