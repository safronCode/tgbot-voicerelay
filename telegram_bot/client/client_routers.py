from telegram_bot.client.handlers.commands import *
from telegram_bot.client.handlers.callbacks import *

all_client_routers = [on_start_router,
                      on_reg_router,
                      to_reg_router,
                      on_channel_router,
                      to_voice_router]
