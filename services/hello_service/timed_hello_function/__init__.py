import logging
logger = logging.getLogger(__name__)

import datetime

import azure.functions as func

def main(mytimer: func.TimerRequest):
  utc_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

  if mytimer.past_due:
    logger.info("The timer is past due!")

  logger.info(f"Python timer trigger function ran at {utc_timestamp}")
