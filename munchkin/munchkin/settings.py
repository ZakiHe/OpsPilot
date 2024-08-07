from dotenv import load_dotenv
from split_settings.tools import include, optional

load_dotenv()

include(
    "components/base.py",
    "components/audit_log.py",
    "components/database.py",
    "components/rest_framework.py",
    "components/celery.py",
    "components/minio.py",
    "components/unfold.py",
    "components/guardian.py",
    "components/kubernetes.py",
    "components/conversation_mq.py",
    "components/pilot.py",
    "components/bk_login.py",
    "components/remote_service.py",
    "components/automation.py",
    optional("local_settings.py"),
)
