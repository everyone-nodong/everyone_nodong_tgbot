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

import dotenv
from telegram import Update, Message
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

GREET_DEBOUNCE_MESSAGE_COUNT = 10


class State:
    message_count: int
    last_message: Message | None

    def __init__(self):
        self.message_count = GREET_DEBOUNCE_MESSAGE_COUNT+1
        self.last_message = None


state = State()

WELCOME_MESSAGE_FORMAT = """
안녕하세요! 전국민주일반노조 누구나노조지회 채팅방에 오신것을 환영합니다!
조합비 납부 방법, 계좌번호 등 자주 묻는 질문은 홈페이지를 참조해주세요.
https://everyone-nodong.github.io/
최근 소식은 채팅방 상단 고정된 메시지에서 확인하실 수 있습니다.
""".strip()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def count_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state.message_count += 1


async def greet_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("message_count=%d <= GREET_DEBOUNCE_MESSAGE_COUNT=%d", state.message_count, GREET_DEBOUNCE_MESSAGE_COUNT)

    if state.message_count <= GREET_DEBOUNCE_MESSAGE_COUNT:
        return

    state.message_count = 0

    if not update.effective_chat:
        return

    if state.last_message:
        await state.last_message.delete()

    state.last_message = await update.effective_chat.send_message(
        text=WELCOME_MESSAGE_FORMAT,
        parse_mode=ParseMode.MARKDOWN,
        disable_notification=True,
    )


def main() -> None:
    """Start the bot."""
    dotenv.load_dotenv('.env.local', override=True)

    # Create the Application and pass it your bot's token.
    application = Application.builder().concurrent_updates(True).token(os.getenv('TG_TOKEN', '')).build()

    application.add_handler(MessageHandler(filters.ALL, count_message), group=0)
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_message), group=1)

    # Run the bot until the user presses Ctrl-C
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()