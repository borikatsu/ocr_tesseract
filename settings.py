# coding: UTF-8
import os
import os.path
import logzero
import logging

# ログ設定
logger = logzero.setup_logger(
    disableStderrLogger = False,
    name                = 'read-card-number',
    logfile             = os.path.join(os.path.dirname(__file__), 'logs/app.log'),
    level               = 20,
    formatter           = logging.Formatter('%(asctime)s %(levelname)s: %(message)s'),
    maxBytes            = 1048576,
    backupCount         = 5,
    fileLoglevel        = 20,
)