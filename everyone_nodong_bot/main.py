#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to handle '(my_)chat_member' updates.
Greets new users & keeps track of which chats the bot is in.

Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

from datetime import datetime

import dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)


GREET_DEBOUNCE_TERM = 60


class State:
    last_dt: datetime

    def __init__(self):
        self.last_dt = datetime.now()


state = State()

WELCOME_MULTIPLE_USER_PREFIX_FORMAT = """
안녕하세요!
""".strip()

WELCOME_SINGLE_USER_PREFIX_FORMAT = """
안녕하세요 [{member_name}](tg://user?id={member_id}) 님,
""".strip()

WELCOME_MESSAGE_FORMAT = """
전국민주일반노조 채팅방에 오신것을 환영합니다!\n조합비 납부 방법, 계좌번호 등 자주 묻는 질문은 홈페이지 참조 바랍니다.\nhttps://everyone-nodong.github.io/\n최근 소식은 채팅방 상단 고정된 메시지에서 확인하실 수 있습니다.
""".strip()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)



async def greet_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now()

    if (now - state.last_dt).total_seconds() < 60:
        return

    state.last_dt = now

    prefix = WELCOME_MULTIPLE_USER_PREFIX_FORMAT

    if len(update.message.new_chat_members) == 1:
        user = update.message.new_chat_members[0]
        prefix = WELCOME_SINGLE_USER_PREFIX_FORMAT.format(member_name=user.name, member_id=user.id)

    await update.effective_chat.send_message(
        text=prefix + ' ' + WELCOME_MESSAGE_FORMAT,
        parse_mode=ParseMode.MARKDOWN,
        disable_notification=True,
    )


def main() -> None:
    """Start the bot."""
    dotenv.load_dotenv('.env.local')

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv('TG_TOKEN')).build()

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_message))

    # Run the bot until the user presses Ctrl-C
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()