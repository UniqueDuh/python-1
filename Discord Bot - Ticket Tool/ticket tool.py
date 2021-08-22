import discord, traceback, random, time, sqlite3
from discord.ext import commands
from datetime import datetime


#configuration
prefix = ">"
TOKEN = "ODc4OTE3ODk5MjExOTA3MDgy.YSIKFA.gqPPCcPLWFQASlGNd6dwFmAzoKs"
color = 0x73ff00 # enter hex color of what u want the embeds color to be (currently set to green)
bot = commands.Bot(command_prefix=prefix,intents=discord.Intents.all())
bot.remove_command('help')


bot.name_of_ticket_category = "TICKETS" # put the NAME of ur ticket category
bot.guild = 850852312473403413 #enter server id of the server the bot is in
bot.support_role = 0 #enter the id of your support role
bot.bot_id = 878917899211907082 # enter the id of your discord bot
bot.paypal_email = "killlua92@gmail.com" # enter your paypal email here
bot.bitcoin_address = "bitcoin:bc1qjhd9swpp6uf9tl3dx7t27ejgpvlxrqf9rgnpcn" # enter your bitcoin address here
bot.log_channel = 850852312750620674


#database connection
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute(f'CREATE TABLE IF NOT EXISTS ticket_panel(channel_id VALUE, message_id VALUE)')
c.execute(f'CREATE TABLE IF NOT EXISTS ticket_number(number VALUE)')

@bot.command()
async def help(ctx):
    embed=discord.Embed(description=f"**{prefix}post_panel** - Posts the panel for users to create a ticket",color=color,timestamp=datetime.utcnow())
    embed.set_author(name="Commands",icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.id != bot.bot_id:
        c.execute("SELECT * FROM ticket_panel")
        data = c.fetchall()
        message_id = data[0][1]
        channel_id = data[0][0]
        c.execute("SELECT * FROM ticket_number")
        ticket_number2 = c.fetchall()
        ticket_number = ticket_number2[0][0]
        if len(ticket_number2) == 0:
            value = 0
            c.execute(f"INSERT INTO ticket_number (number) VALUES('{value}')")
            conn.commit()
            c.execute("SELECT * FROM ticket_number")
            ticket_number = c.fetchall()[0][0]
        guild = bot.get_guild(bot.guild)
        if message_id == payload.message_id:
            guild = bot.get_guild(bot.guild)
            role = guild.get_role(bot.support_role)
            category = discord.utils.get(guild.categories,name=bot.name_of_ticket_category)
            ticket_number += 1
            channel = await guild.create_text_channel(f"Ticket-{ticket_number}",category=category)
            overwrites = {role:discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.default_role:discord.PermissionOverwrite(view_channel=False)}
            await channel.edit(overwrites=overwrites)
            c.execute('UPDATE ticket_number SET number = number + 1')
            conn.commit()
            def check(m):
                return m.author.id == payload.user_id and m.channel.id == channel.id
            member = guild.get_member(payload.user_id)
            embed=discord.Embed(description="Hello, thank you for opening a ticket. What service are you looking to purchase today?",color=color,timestamp=datetime.utcnow())
            embed.set_author(name="Select Service",icon_url=member.avatar_url)
            await channel.send(embed=embed)
            service = await bot.wait_for("message",check=check)
            embed=discord.Embed(description="What payment method will you be using? Paypal or Bitcoin (BTC)?",color=color,timestamp=datetime.utcnow())
            embed.set_author(name="Payment Method",icon_url=member.avatar_url)
            await channel.send(embed=embed)
            payment_method = await bot.wait_for("message",check=check)
            paypal = ["paypal","pp","Paypal","PayPal","pay","pal","PAYPAL"]
            bitcoin = ["btc","BTC","Bitcoin","bitcoin","BITCOIN"]
            if payment_method.content in paypal:
                await channel.send(f"Please send payment to **{bot.paypal_email}**")
                valid = True
            elif payment_method.content in bitcoin:
                await channel.send(f"Please send payment to **{bot.bitcoin_address}**")
                valid = True
            else:
                await channel.send("That is not a valid response")
                valid = False
            if valid == True:
                embed=discord.Embed(description="Once you have sent payment please say **done**",color=color,timestamp=datetime.utcnow())
                embed.set_author(name="Awaiting Confirmation",icon_url=member.avatar_url)
                await channel.send(embed=embed)
                confirmation = await bot.wait_for("message",check=check)
                responses = ["done","Done","DONE","d0ne"]
                if confirmation.content in responses:
                    embed=discord.Embed(description="Please send the link to what you wanted boosted",color=color,timestamp=datetime.utcnow())
                    embed.set_author(name="Link",icon_url=member.avatar_url)
                    await channel.send(embed=embed)
                    link = await bot.wait_for("message",check=check)
                    embed=discord.Embed(description="Thank you for ordering, your order has been forwarded to Jinx to process",color=color,timestamp=datetime.utcnow())
                    embed.set_author(name="Confirmed Order",icon_url=member.avatar_url)
                    await channel.send(embed=embed)
                    log_channel = guild.get_channel(bot.log_channel)
                    embed=discord.Embed(color=color,timestamp=datetime.utcnow())
                    embed.set_author(name=f"Ticket-{ticket_number}",icon_url=member.avatar_url)
                    embed.add_field(name="Service:",value=service.content)
                    embed.add_field(name="Payment Method:",value=payment_method.content)
                    embed.add_field(name="Payment Confirmed by User:",value="True")
                    embed.add_field(name="Link to Boost:",value=link.content)
                    embed.set_footer(text="Please check if you have received payment and process the order")
                    await log_channel.send(embed=embed)
                else:
                    await channel.send("That is not a valid response")

        



@bot.command()
async def post_panel(ctx):
    if ctx.author.guild_permissions.administrator:
        c.execute(f"DROP TABLE ticket_panel;")
        c.execute(f'CREATE TABLE IF NOT EXISTS ticket_panel(channel_id VALUE, message_id VALUE)')
        conn.commit()
        embed=discord.Embed(description="Request an Order please create a ticket by reacting below",color=color,timestamp=datetime.utcnow())
        embed.set_author(name="Ticket Panel",icon_url=ctx.author.avatar_url)
        sent = await ctx.send(embed=embed)
        c.execute(f"INSERT INTO ticket_panel (channel_id, message_id) VALUES('{ctx.channel.id}','{sent.id}')")
        conn.commit()
        await sent.add_reaction("\U0001f4e7")
    else:
        embed=discord.Embed(description="You do not have permission to use this command",color=color,timestamp=datetime.utcnow())
        embed.set_author(name="Insufficient Permission",icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)























bot.run(TOKEN)
