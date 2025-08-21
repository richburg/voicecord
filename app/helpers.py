from typing import Optional, cast

from discord import (
    CategoryChannel,
    Interaction,
    Member,
    PermissionOverwrite,
    VoiceChannel,
    VoiceState,
)
from sqlmodel import select

from app.config import CHANNELS_CATEGORY_ID, JOIN_TO_CREATE_CHANNEL_ID
from app.database import Ban, Channel, async_session


def wants_to_create_channel(before: VoiceState, after: VoiceState) -> bool:
    return bool(
        not before.channel
        and after.channel
        and after.channel.id == JOIN_TO_CREATE_CHANNEL_ID
    )


def generate_overwrites_for_new_channel(member: Member) -> dict:
    return {
        member.guild.default_role: PermissionOverwrite(connect=False),
        member: PermissionOverwrite(connect=True),
    }


async def get_ban(user_id: int) -> Optional[Ban]:
    async with async_session() as s:
        result = await s.execute(select(Ban).where(Ban.user_id == user_id))
        item = result.scalar_one_or_none()
        return item


async def create_channel(member: Member):
    category = member.guild.get_channel(CHANNELS_CATEGORY_ID)

    if category is None:
        raise Exception("Invalid ID: `CHANNELS_CATEGORY`")

    if not isinstance(category, CategoryChannel):
        raise TypeError("Invalid category: `CHANNELS_CATEGORY`")

    return await member.guild.create_voice_channel(
        name=f"{member.global_name or member.name}'s channel",
        category=category,
        overwrites=generate_overwrites_for_new_channel(member),
    )


async def create_db_channel(channel_id: int, creator_id: int):
    async with async_session() as s:
        channel = Channel(id=channel_id, creator_id=creator_id)
        s.add(channel)
        await s.commit()
        await s.refresh(channel)


async def get_channel_by_creator_id(creator_id: int) -> Optional[Channel]:
    async with async_session() as s:
        result = await s.execute(
            select(Channel).where(Channel.creator_id == creator_id)
        )
        item = result.scalar_one_or_none()
        return item


async def get_voice_channel_by_creator_id(
    interaction: Interaction,
) -> Optional[VoiceChannel]:
    channel = await get_channel_by_creator_id(interaction.user.id)
    if not channel:
        await interaction.response.send_message("You don't own a channel")
        return

    assert interaction.guild
    voice_channel = interaction.guild.get_channel(channel.id)
    if not voice_channel:
        await interaction.response.send_message(
            "Your voice channel is probably deleted manually"
        )
        return

    return cast(VoiceChannel, voice_channel)


async def delete_channel(channel: Channel):
    async with async_session() as s:
        await s.delete(channel)
        await s.commit()
