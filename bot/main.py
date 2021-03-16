import json
from discord_slash import cog_ext

import discord
from discord_slash import SlashCommand,SlashContext
import random
from discord_slash.utils import manage_commands
from discord.ext import commands
import pybelieva
import datetime
import asyncio
from discord_webhook import DiscordWebhook, DiscordEmbed

bot = commands.Bot(command_prefix = '-', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

guild_ids = [818136401757339680] 
time = datetime.datetime.now()

class Economy(commands.Cog):
    _token: str
    unb_client: pybelieva.Client  
    emoji: str  
    tax: float  

    def __init__(self, token: str, emoji: str, tax: float = 0.10):
        self._token = token  
        self.emoji = emoji
        self.tax = tax
        self.bot = bot
        self.unb_client = pybelieva.Client(self._token)
        print("Created UnbelievaBoat client!")
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready!")
    
    @cog_ext.cog_slash(name="lend",description="Leihe dir bis zu 10mio Casino Coins", guild_ids=guild_ids, options=[manage_commands.create_option(name = "amount", description=f"Gebe die Anzahl an Coins an, die du leihen möchtest. Du musst hierzu noch den Zinssatz darauf zahlen",option_type = 4,required = True)])
    async def _lend(self,  ctx: SlashContext, amount=''):
        await ctx.respond(eat=False)
        if int(amount) < 0:
            await ctx.channel.send('danke für den Versuch uns Geld zu schenken, aber wir nehmen keine negativen Kredite auf')
            return
        if int(amount) >= 10000000:
            await ctx.channel.send('Das ist sehr viel Geld, bitte melde dich bei Delfini oder Pinguini für so einen hohen Kredit')
            return
        if int(amount) == 0:
            await ctx.channel.send('Und für was brauchst du einen Kredit inhöhe von 0 coins?')
            return
        
        with open('data_store.json', 'r') as f:
            data = json.load(f)
        
        if str(ctx.author.id) not in list(data[str(ctx.guild.id)]):
            data[str(ctx.guild.id)][str(ctx.author.id)] = {
                "amount": 0,
                "time": 0,
                "mond": 0,
                "mars": 0,
                "saturn": 0,
                "jupiter": 0
            }
            with open('data_store.json', 'w') as f:
                json.dump(data, f, indent=4)
        
        if data[str(ctx.guild.id)][str(ctx.author.id)]['amount'] > 0:
            await ctx.channel.send('Du hast bereits Geld geliehen, bitte Zahle dieses zurück, bevor du einen neuen Kredit aufnehmen kannst.')
            return
        tax = int(int(amount) * self.tax)
        after_tax = int(int(amount) + ((self.tax/100)*int(amount)))
        guild = await self.unb_client.get_guild(ctx.guild.id)
        currency = guild.symbol
        message = await ctx.channel.send(f'Möchest du dir{currency}{amount} leihen?. Bis in 4 Wochen musst du {currency}{after_tax} zurückzahlen. Für Jeden weiteren Tag fallen {currency}25000 an! Bitte reagiere mit **`👍`** um zuzustimmen')
        await message.add_reaction('👍')
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '👍' and message.id == reaction.message.id
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=70.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('Action timed out')
            return
        
        await ctx.channel.send(f'Du hast dir {currency}{amount} geliehen. Bis in 4 Wochen musst du {currency}{after_tax} zurückzahlen. Für Jeden weiteren Tag fallen {currency}25000 an!')
        
        await self.unb_client.patch_user_balance(guild_id=ctx.guild.id, user_id=ctx.author.id, bank=int(amount), reason=f"lend command\n**Details:** {bot.get_channel(data[str(ctx.guild.id)]['log']).mention}")
        date = time.strftime("%d%m%Y")
        data[str(ctx.guild.id)][str(ctx.author.id)]['amount'] = int(after_tax)
        data[str(ctx.guild.id)][str(ctx.author.id)]['time'] = int(date)
        with open('data_store.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(int(data[str(ctx.guild.id)]['log']))
        
        webhook_url = str(data[str(ctx.guild.id)]['webhook'])
        embed1 = DiscordEmbed(title='', description=f'**User:** {ctx.author.mention}\n**Amount:** {amount}\n**Reason:** lend command', color='03b2f8')
        embed2 = DiscordEmbed(title='', description=f'a new member lend some money\n**User:** {ctx.author.mention}\n**Amount:** {amount}', color='03b2f8')
        embed1.set_author(name='Balance updated', icon_url='https://images-ext-2.discordapp.net/external/i0QukyQFeMvyky2L88d-lcpPGvruP_5XcvHxmsx56R0/https/media.discordapp.net/attachments/506838906872922145/551888336525197312/update.png')
        embed2.set_author(name='Lend', icon_url='https://static.wikia.nocookie.net/discordapp/images/e/ef/MemberCreation.png/revision/latest?cb=20180822022110')
        embed1.set_timestamp()
        embed2.set_timestamp()
        webhook = DiscordWebhook(url=webhook_url, content='')
        webhook.add_embed(embed1)
        webhook.add_embed(embed2)
        response = webhook.execute()
        
        channel = bot.get_channel(int(data[str(ctx.guild.id)]['log']))
        
        
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setlog(self, ctx, channel: discord.TextChannel = None):
        if channel == None:
            channel = ctx.channel
        for i in await ctx.guild.webhooks():
            if i.user.id == self.bot.user.id:
                await i.delete(reason="changed the log webhook")
        webhook = await channel.create_webhook(name='BankLog', avatar=await self.bot.user.avatar_url.read(), reason=f'setLog, changed by {ctx.author}')
        with open('data_store.json', 'r') as f:
            data = json.load(f)
        data[str(ctx.guild.id)]['webhook'] = webhook.url
        data[str(ctx.guild.id)]['log'] = channel.id
        with open('data_store.json', 'w') as f:
            json.dump(data, f, indent=4)
        await ctx.channel.send(f'setted the new log channel to {channel.mention}')


    @cog_ext.cog_subcommand(base="shop", name="buy", description="Kaufe dir ein Item erneut.", guild_ids=guild_ids, options=[manage_commands.create_option(description='Bitte gebe das Iteam das du kaufen möchtest an.', name='item', required=True, option_type=(3), choices=['Mond', 'Mars', 'Saturn', 'Jupiter', 'Treibstoff']), manage_commands.create_option(name = "amount", description=f"Bitte gebe an, wie oft du das Item kaufen willst (Du kannst überspringen, wenn du nur 1 möchtest)",option_type = 4,required = False)]) #, create_choices=('hello', 'foo', 'bar'))])
    async def group_shop(self, ctx: SlashContext, item='', amount=1):
        await ctx.respond(eat=False)
        
        bal = await self.unb_client.get_user_balance(guild_id=ctx.guild.id, user_id=ctx.author.id)
        with open('data_store.json', 'r+') as f:
            data = json.load(f)
        if item == 'Treibstoff':
            amount2 = 500000
            if amount2*amount > bal.cash + bal.bank:
                await ctx.channel.send(f'Du hast leider nicht genug um dir {amount} mal {item} kaufen zu können')
                return
            items = int(data[str(ctx.guild.id)][str(ctx.author.id)][str(item).lower()]) + int(amount)

            if bal.cash - int(amount2*amount) > 0:
                cash = int(amount2*amount)
                bank = 0
                await self.unb_client.patch_user_balance(guild_id=ctx.guild.id, user_id=ctx.author.id, cash=-int(amount2*amount), reason=f"bought new Item\n**Details:** {bot.get_channel(data[str(ctx.guild.id)]['log']).mention}")
            else:
                total = int(amount2*amount)
                cash = bal.cash
                
                bank = total - cash
                await self.unb_client.patch_user_balance(guild_id=ctx.guild.id, user_id=ctx.author.id, cash=-cash, bank = -bank, reason=f"bought new Item\n**Details:** {bot.get_channel(data[str(ctx.guild.id)]['log']).mention}")

            
            data[str(ctx.guild.id)][str(ctx.author.id)][str(item).lower()] = items
            with open('data_store.json', 'w') as f:
                json.dump(data, f, indent=4)
            await ctx.send(f'Du hast dir Erfolgreich {amount} mal das Item {item} gekauft')
            webhook_url = str(data[str(ctx.guild.id)]['webhook'])
            embed1 = DiscordEmbed(title='', description=f'**User:** {ctx.author.mention}\n**Amount:** Cash: `-{cash:,}` Bank: `-{bank:,}`\n**Reason:** bought new Item in shop\n**Item:** {item}\n**Amount of items:** {amount}', color='03b2f8')
            embed1.set_author(name='Balance updated', icon_url='https://images-ext-2.discordapp.net/external/i0QukyQFeMvyky2L88d-lcpPGvruP_5XcvHxmsx56R0/https/media.discordapp.net/attachments/506838906872922145/551888336525197312/update.png')
            embed1.set_timestamp()
            webhook = DiscordWebhook(url=webhook_url, content='')
            webhook.add_embed(embed1)
            response = webhook.execute()
            return
        if item == "Mond":
            amount2 = 1000000
        elif item == "Mars":
            amount2 = 2000000
        elif item == 'Saturn':
            amount2 = 3500000
        elif item == 'Jupiter':
            amount2 = 6000000
        else:
            return
        if amount2*amount > bal.cash + bal.bank:
            await ctx.channel.send(f'Du hast leider nicht genug Geld um dir {amount} mal {item} kaufen zu können')
            return

        
        items = int(data[str(ctx.guild.id)][str(ctx.author.id)][str(item).lower()]) + int(amount)
        print(items)
        data[str(ctx.guild.id)][str(ctx.author.id)][str(item).lower()] = items
        with open('data_store.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(int(amount2*amount))

        

        if int(data[str(ctx.guild.id)][str(ctx.author.id)]['treibstoff']) < amount:
            await ctx.send(f'Du hast leider nicht genug Treibstoffn. kaufe dir neue mit**`/shop buy item:Treibstoff amount:1`**')
            return
        data[str(ctx.guild.id)][str(ctx.author.id)]['treibstoff'] = int(data[str(ctx.guild.id)][str(ctx.author.id)]['treibstoff']) - int(amount)
        with open('data_store.json', 'w') as f:
            json.dump(data, f, indent=4)
        if bal.cash - int(amount2*amount) > 0:
            cash = -int(amount2*amount)
            bank = 0
            await self.unb_client.patch_user_balance(guild_id=ctx.guild.id, user_id=ctx.author.id, cash=-int(amount2*amount), reason=f"bought new Item\n**Details:** {bot.get_channel(data[str(ctx.guild.id)]['log']).mention}")
        else:
            total = int(amount2*amount)
            cash = bal.cash
            
            bank = total - cash
            await self.unb_client.patch_user_balance(guild_id=ctx.guild.id, user_id=ctx.author.id, cash=-cash, bank = -bank, reason=f"bought new Item\n**Details:** {bot.get_channel(data[str(ctx.guild.id)]['log']).mention}")

        await ctx.send(f'Du hast dir Erfolgreich {amount} mal das Item {item} gekauft')

        webhook_url = str(data[str(ctx.guild.id)]['webhook'])
        embed1 = DiscordEmbed(title='', description=f'**User:** {ctx.author.mention}\n**Amount:** Cash: `-{cash:,}` Bank: `-{bank:,}`\n**Reason:** bought new Item in shop\n**Item:** {item}\n**Amount of items:** {amount}', color='03b2f8')
        embed1.set_author(name='Balance updated', icon_url='https://images-ext-2.discordapp.net/external/i0QukyQFeMvyky2L88d-lcpPGvruP_5XcvHxmsx56R0/https/media.discordapp.net/attachments/506838906872922145/551888336525197312/update.png')
        embed1.set_timestamp()
        webhook = DiscordWebhook(url=webhook_url, content='')
        webhook.add_embed(embed1)
        response = webhook.execute()
        
        channel = bot.get_channel(int(data[str(ctx.guild.id)]['log']))

    @cog_ext.cog_subcommand(base="collect", name="income", description="Erhalte dein Geld.", guild_ids=guild_ids)
    async def collect_income(self, ctx: SlashContext):
        with open('data_store.json', 'r') as f:
            data = json.load(f)
        if time.strftime("%d%m%y") == str(data[str(ctx.guild.id)][str(ctx.author.id)]['collected']):
            await ctx.channel.send('Kein Income mehr vorhanden.')
            return
        mond = int(data[str(ctx.guild.id)][str(ctx.author.id)]['mond'])
        mars = int(data[str(ctx.guild.id)][str(ctx.author.id)]['mars'])
        saturn = int(data[str(ctx.guild.id)][str(ctx.author.id)]['saturn'])
        jupiter = int(data[str(ctx.guild.id)][str(ctx.author.id)]['jupiter'])
        total = mond*500000 + mars*1000000 + saturn*1500000 + jupiter*2000000
        if total <= 0:
            await ctx.channel.send('Kein Income vorhanden')
            return
        await self.unb_client.patch_user_balance(guild_id=ctx.guild.id, user_id=ctx.author.id, bank=total, reason=f"Collected ext income\n**Details:** {bot.get_channel(data[str(ctx.guild.id)]['log']).mention}")
        
        webhook_url = str(data[str(ctx.guild.id)]['webhook'])
        webhook = DiscordWebhook(url=webhook_url, content='')
        guild = await self.unb_client.get_guild(ctx.guild.id)
        currency = guild.symbol
        text = ''
        if mond*500000 > 0:
            embed1 = DiscordEmbed(title='', description=f'**User:** {ctx.author.mention}\n**Item:** Mond\n**Amount:** {mond*500000}\n**Incomes:** {mond}\n**Reason:** colected income', color='03b2f8')
            embed1.set_author(name='Balance updated', icon_url='https://images-ext-2.discordapp.net/external/i0QukyQFeMvyky2L88d-lcpPGvruP_5XcvHxmsx56R0/https/media.discordapp.net/attachments/506838906872922145/551888336525197312/update.png')
            embed1.set_timestamp()
            webhook.add_embed(embed1)
            text += f'{mond}\*{currency}500000 | Mond | Amount: {mond*500000}\n'
        
        if mars*1000000 > 0:
            embed1 = DiscordEmbed(title='', description=f'**User:** {ctx.author.mention}\n**Item:** Mars\n**Amount:** {mars*1000000}\n**Incomes:** {mars}\n**Reason:** colected income', color='03b2f8')
            embed1.set_author(name='Balance updated', icon_url='https://images-ext-2.discordapp.net/external/i0QukyQFeMvyky2L88d-lcpPGvruP_5XcvHxmsx56R0/https/media.discordapp.net/attachments/506838906872922145/551888336525197312/update.png')
            embed1.set_timestamp()
            webhook.add_embed(embed1)
            text += f'{mars}\*{currency}1000000 | Mars | Amount: {mars*1000000}\n'
            
        if saturn*1500000 > 0:
            embed1 = DiscordEmbed(title='', description=f'**User:** {ctx.author.mention}\n**Item:** Saturn\n**Amount:** {saturn*1500000}\n**Incomes:** {saturn}\n**Reason:** colected income', color='03b2f8')
            embed1.set_author(name='Balance updated', icon_url='https://images-ext-2.discordapp.net/external/i0QukyQFeMvyky2L88d-lcpPGvruP_5XcvHxmsx56R0/https/media.discordapp.net/attachments/506838906872922145/551888336525197312/update.png')
            embed1.set_timestamp()
            webhook.add_embed(embed1)
            text += f'{saturn}\*{currency}1500000 | Saturn | Amount: {saturn*1500000}\n'
            
        if jupiter*2000000 > 0:
            embed1 = DiscordEmbed(title='', description=f'**User:** {ctx.author.mention}\n**Item:** Jupiter\n**Amount:** {jupiter*2000000}\n**Incomes:** {jupiter}\n**Reason:** colected income', color='03b2f8')
            embed1.set_author(name='Balance updated', icon_url='https://images-ext-2.discordapp.net/external/i0QukyQFeMvyky2L88d-lcpPGvruP_5XcvHxmsx56R0/https/media.discordapp.net/attachments/506838906872922145/551888336525197312/update.png')
            embed1.set_timestamp()
            webhook.add_embed(embed1)
            text += f'{jupiter}\*{currency}2000000 | Jupiter | Amount: {jupiter*2000000}\n'
        
        embed = discord.Embed(title='', description=f'income collected:\n{text}', timestamp=time)
        #embed.set_timestamp(time)
        await ctx.send(embed=embed)
        response = webhook.execute()
        data[str(ctx.guild.id)][str(ctx.author.id)]['collected'] = time.strftime("%d%m%y")
        with open('data_store.json', 'w') as f:
            json.dump(data, f, indent=4)

    @cog_ext.cog_slash(description="Verschenke Geld", guild_ids=guild_ids, options=[manage_commands.create_option(description='Bitte gebe an, wie viel Geld du verschenken möchtest.', name='Amount', required=True, option_type=(4)), manage_commands.create_option(description='Soll Das giveaway für alle zugänglich sein, oder nur für den PinguClan?', name='Public', required=False, option_type=(3), choices=['Public', 'Private']), manage_commands.create_option(description='Gebe eine custom beschreibung an. Zeichenlimit: 200; Links sind verboten.', name='Beschreibung', required=False, option_type=3)])
    async def giveaway(self, ctx: commands.Context, Amount = 0, Public = 'False', Beschreibung=''):
        await ctx.respond(eat=False)
        print(Public)
        print(len(str(Beschreibung)))
        if len(str(Beschreibung)) > 200:
            await ctx.channel.send('Bitte wähle eine kürzere Beschreibung.')
            return
        if Public == 'Public':
            role = 818136401757339680 #everyone
        else:
            role = 821320546918072320 #pinguclan
            
        if Amount <= 0:
            return await ctx.send("Du solltest schon ein bischen mehr verschenken ;)")
        bal = await self.unb_client.get_user_balance(
            ctx.guild.id, ctx.author.id
        )  
        if bal.cash < Amount: 
            return await ctx.send("Du hast leider nicht genug Geld bei dir..")
        guild = await self.unb_client.get_guild(ctx.guild.id)
        currency = guild.symbol
        await self.unb_client.patch_user_balance( 
            ctx.guild.id, ctx.author.id, cash=-Amount, reason="giveaway command"
        )
        
        #if Beschreibung == None:
        description = f"{Beschreibung}\n{ctx.author.mention} verschenkt {currency}{Amount}! \nreagiere mit {self.emoji}, um teilzunehmen. \nBenötigte Rolle: {ctx.guild.get_role(role).mention}"
        #else:
        #    description = f'{Beschreibung}'
        embed = discord.Embed(title="Giveaway", description=description)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(self.emoji)  
        await asyncio.sleep(60)  
        msg = await ctx.channel.fetch_message(msg.id)
        e = []
        for i in ctx.author.roles:
            e.append(i.id)
        
        candidates = [
            i
            async for i in cast(
                Reaction,
                get(
                    msg.reactions,
                    emoji=self.emoji,
                ),  
            ).users()  
            if not i.bot  
            and i != ctx.author and role in e
        ]
        print(msg.reactions, candidates)
        
        try:
            winner: Union[User, Member] = random.choice(
                candidates
            )
            embed = discord.Embed(title="Giveaway", description=f'Winner: {winner.mention}')
            await msg.edit(embed = embed)
            await self.unb_client.patch_user_balance(  
                ctx.guild.id, winner.id, cash=Amount, reason="giveaway winner"
            )
            await msg.clear_reactions()
        except:
            embed = discord.Embed(title="Giveaway", description='No winners')
            await msg.edit(embed = embed)
            await msg.clear_reactions()
        
        with open('data_store.json', 'r') as f:
            data = json.load(f)
        webhook_url = str(data[str(ctx.guild.id)]['webhook'])
        webhook = DiscordWebhook(url=webhook_url, content='')
        embed1 = DiscordEmbed(title='', description=f'**User:** {ctx.author.mention}\n**Action:** Giveaway\n**Amount:** -{Amount}', color='03b2f8')
        embed2 = DiscordEmbed(title='', description=f'**User:** {winner.mention}\n**Action:** Giveaway won\n**Amount:** +{Amount}', color='03b2f8')
        embed1.set_author(name='Balance updated', icon_url='https://images-ext-2.discordapp.net/external/i0QukyQFeMvyky2L88d-lcpPGvruP_5XcvHxmsx56R0/https/media.discordapp.net/attachments/506838906872922145/551888336525197312/update.png')
        embed2.set_author(name='Balance updated', icon_url='https://images-ext-2.discordapp.net/external/i0QukyQFeMvyky2L88d-lcpPGvruP_5XcvHxmsx56R0/https/media.discordapp.net/attachments/506838906872922145/551888336525197312/update.png')
        embed1.set_timestamp()
        embed2.set_timestamp()
        webhook.add_embed(embed1)
        webhook.add_embed(embed2)
        response = webhook.execute()


with open('bot-settings.json', 'r') as f:
    data = json.load(f)

bot.add_cog(Economy(str(data['unb']), "\N{MONEY WITH WINGS}", tax = 2.3))
bot.load_extension("jishaku")
bot.run(str(data['discord']))
