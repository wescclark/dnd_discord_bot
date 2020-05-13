from discord.ext import commands


class DMAccessOnly(commands.CheckFailure):
    pass


def is_dm():
    async def predicate(ctx):
        if "DM" not in [_.name for _ in ctx.author.roles]:
            raise DMAccessOnly("This command is for DMs only.")
        return True

    return commands.check(predicate)
