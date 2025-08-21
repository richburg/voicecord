from typing import Union, cast

from discord import Interaction, Member, PermissionOverwrite, Role, app_commands
from discord.ext.commands import Bot, Cog, GroupCog

from app.helpers import get_voice_channel_by_creator_id


class Voice(GroupCog, name="voice"):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_ready")
    async def on_ready(self) -> None:
        await self.bot.tree.sync()

    async def _apply_overwrites(self, interaction: Interaction, overwrites: dict):
        voice_channel = await get_voice_channel_by_creator_id(interaction)
        if voice_channel:
            await voice_channel.edit(overwrites=overwrites)
            await interaction.response.send_message("I've updated your channel")

    async def _apply_one_overwrite(
        self,
        interaction: Interaction,
        target: Union[Role, Member],
        overwrite: PermissionOverwrite,
    ):
        voice_channel = await get_voice_channel_by_creator_id(interaction)
        if voice_channel:
            await voice_channel.set_permissions(target=target, overwrite=overwrite)
            await interaction.response.send_message("I've updated your channel")

    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.command(name="public")
    async def public(self, interaction: Interaction):
        assert interaction.guild
        await self._apply_overwrites(
            interaction,
            overwrites={
                interaction.guild.default_role: PermissionOverwrite(connect=True)
            },
        )

    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.command(name="private")
    async def private(self, interaction: Interaction):
        assert interaction.guild
        await self._apply_overwrites(
            interaction,
            overwrites={
                cast(Member, interaction.user): PermissionOverwrite(connect=True),
                interaction.guild.default_role: PermissionOverwrite(connect=False),
            },
        )

    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.command(name="ghost")
    async def ghost(self, interaction: Interaction):
        assert interaction.guild
        await self._apply_one_overwrite(
            interaction,
            interaction.guild.default_role,
            PermissionOverwrite(view_channel=False),
        )

    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_channels=True, move_members=True)
    @app_commands.command(name="allow")
    async def allow(self, interaction: Interaction, target: Member):
        assert interaction.guild
        await self._apply_one_overwrite(
            interaction,
            target,
            PermissionOverwrite(connect=True),
        )

    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_channels=True, move_members=True)
    @app_commands.command(name="disallow")
    async def disallow(self, interaction: Interaction, target: Member):
        assert interaction.guild
        await self._apply_one_overwrite(
            interaction,
            target,
            PermissionOverwrite(connect=False),
        )

        if (
            target.voice
            and target.voice.channel
            and target.voice.channel.id == interaction.user.voice.channel.id  # type: ignore
        ):
            await target.move_to(None)


async def setup(bot: Bot):
    await bot.add_cog(Voice(bot))
