#!/usr/bin/env python
# coding=utf-8
# ******************************************************
# Author       : Zhang Xingang
# Email        : zhangxingang@xiaomi.com
# Last modified: 20/02/25 11:22
# Filename     : feishu_alert.py
# Description  :
# ******************************************************
import time

from elastalert.alerts import Alerter, DateTimeEncoder
from requests import get, post, RequestException
from elastalert.util import elastalert_logger, EAException


class FeiShuAlerter(Alerter):
    required_options = {'feishu'}

    def __init__(self, rule):
        super(FeiShuAlerter, self).__init__(rule)
        self.app_id = self.rule["feishu"]["app_id"]
        self.app_secret = self.rule["feishu"]["app_secret"]
        self.chat_id = self.rule["feishu"].get("chat_id")
        self.open_id = self.rule["feishu"].get("open_id")
        self.user_id = self.rule["feishu"].get("user_id")
        self.email = self.rule["feishu"].get("email")
        self.tenant_access_token = self.get_tenant_access_token()

    def get_tenant_access_token(self):
        body = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        try:
            r = get("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/", json=body).json()
            if r['code'] == 0:
                # elastalert_logger.debug("token: " + r['tenant_access_token'])
                return r['tenant_access_token']
        except Exception as e:
            raise EAException("Get tenant_access_token failed:".format(e))

    def alert(self, matches):
        headers = {
            "Authorization": "Bearer " + self.tenant_access_token
        }
        body = {
            "chat_id": self.chat_id,
            "open_id": self.open_id,
            "user_id": self.user_id,
            "email": self.email,
            "msg_type": "text",
            "content": {
                "text": self.create_alert_body(matches)
            }
        }
        try:
            r = post("https://open.feishu.cn/open-apis/message/v4/send/", json=body, headers=headers)
            r.raise_for_status()
        except RequestException as e:
            # elastalert_logger.debug(r.content)
            raise EAException("Error request to feishu: {}\n{}".format(str(e)))

    def get_info(self):
        return {
            "type": "feishu",
            "timestamp": time.time()
        }
