import logging

from discord import Member, VoiceState
from discord.ext.commands import Bot, Cog

from app.helpers import (
    create_channel,
    create_db_channel,
    delete_channel,
    get_ban,
    get_channel_by_creator_id,
    wants_to_create_channel,
)


class Handlers(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_ready")
    async def on_ready(self) -> None:
        assert self.bot.user
        logging.info(f"Logged in as {self.bot.user.name}#{self.bot.user.discriminator}")

    @Cog.listener("on_voice_state_update")
    async def voice_update(self, member: Member, b: VoiceState, a: VoiceState):
        if wants_to_create_channel(b, a):
            ban = await get_ban(member.id)
            if ban is not None:
                return await member.send(
                    f"I'm unable to create you a voice channel. You were banned on <t:{ban.timestamp}:F> by <@{ban.staff_id}> for the following reason `{ban.reason}`"
                )
            channel = await create_channel(member)
            await member.move_to(channel)
            await create_db_channel(channel.id, member.id)

        channel = await get_channel_by_creator_id(member.id)

        # Checks if user left from his/her own channel
        if channel and b.channel and b.channel.id == channel.id:
            voice_channel = member.guild.get_channel(channel.id)
            if voice_channel:
                await voice_channel.delete()
                await delete_channel(channel)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Handlers(bot))
