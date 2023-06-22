#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import asyncio
from pathlib import Path
import os
import shutil
from typing import List

from telegram import __version__ as TG_VER

# from telegram._utils.types import FileInput

TOKEN = "token"

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import ForceReply, Update  # noqa: E402
from telegram.ext import (  # noqa: E402
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def run_command(url) -> List[str]:
    # Clear if dir exist
    root = Path("/tmp/t_ym3")
    if root.exists():
        shutil.rmtree(root)

    # Load audio
    command = ["yt-dlp", "-x", "--audio-format", "mp3", "-P", "/tmp/t_ym3", url]
    # yt-dlp -x --audio-format mp3 -P the_file 'https://www.youtube.com/watch?v=9uS4XosYl2A'
    proc = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    print(stdout.decode())
    print(stderr.decode())

    # Return list of musics
    music_files = []
    for file in root.iterdir():
        if file.suffix == ".mp3":
            music_files.append(file.absolute())
    return music_files


def check_valid_yt_url(url: str) -> bool:
    words = url.split(' ')
    if len(words) > 1:
        return False
    return True


async def process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    if check_valid_yt_url(url):
        music_files = await run_command(url)
        for music in music_files:
            await update.message.reply_audio(audio=music)
    else:
        await update.message.reply_text("Wrong URL")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
