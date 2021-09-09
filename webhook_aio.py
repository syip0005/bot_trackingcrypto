import json

from aiohttp import web
from discord.ext import commands, tasks
import discord
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()
app = web.Application()
routes = web.RouteTableDef()

# Unhard link all the bottom later on

# Load in famous traders list into memory (fix this later)
famous_traders = {
    "0xdec08cb92a506B88411da9Ba290f3694BE223c26".lower(): "Tom1",
    "0x198E18EcFdA347c6cdaa440E22b2ff89eaA2cB6f".lower(): "Tom2",
    "0xA39C50bf86e15391180240938F469a7bF4fDAe9a".lower(): "Kong1",
    "0x4C9ba42FEd324c556632489D196880002a6cE09d".lower():  "BigSmAK"
}

# Load in links to images hosted separately
imgs = {'confirmed': "https://i.postimg.cc/85tNkPBY/tick.png",
        'pending-simulation': "https://i.postimg.cc/W32sPJrr/clock.png",
        'pending': "https://i.postimg.cc/W32sPJrr/clock.png",
        'failed': "https://i.postimg.cc/Rhh9W5gZ/x.png"}

# End routers
routers = {'488d': 'uniswap', 'd12b': 'opensea'}


def setup(bot):
    """Standard function to add Webserver cog to Bot"""
    bot.add_cog(Webserver(bot))


class Webserver(commands.Cog):
    """Class which inherits from discord.py Cog. Cogs allow for async run of different
    'blocks' of code. This webserver block runs a HTTP webserver using `aiohttp` package which
    accepts HTTP push methods (webhooks)."""

    def __init__(self, bot):
        self.bot = bot
        # .start() method used in conjunction with @tasks.loop() decorator to start running

        self.web_server.start()

        @routes.post('/webhook')
        async def handle_post(request):
            if request.method == 'POST':
                payload_data = await request.json()

                # Move payload data processing acorss
                if payload_data['from'].lower() in famous_traders:
                    trader = famous_traders[payload_data['from'].lower()]
                else:
                    trader = 'Unknown Trader'

                if payload_data['to'][-4:].lower() in routers:
                    router_traded = routers[payload_data['to'][-4:].lower()]
                else:
                    router_traded = 'NA'

                channel = self.bot.get_channel(880409425754587176)  # get general channel

                # generates Discord embed - should put in another function later
                embed = discord.Embed(title="{} Trade Update".format(trader), url=self.generate_es_link(payload_data),
                                      description="{} has just made a {} trade".format(trader, payload_data['status']))
                embed.add_field(name="Trade From", value="{}".format(trader))
                embed.add_field(name="Pending Time Stamp", value=payload_data['pendingTimeStamp'])
                if router_traded != 'NA': embed.add_field(name="Router", value=router_traded)
                embed.set_thumbnail(url=imgs[payload_data['status']])

                await channel.send(embed=embed)

                print('[INFO] Trade noted at {}'.format(payload_data['pendingTimeStamp']))

                return web.Response(status=200, text='success')
            else:
                return web.Response(status=200, text='received but not post')

        self.web_server_port = os.environ.get('PORT', 5000)
        app.add_routes(routes)

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)  # provides async (non blocking) to serve multiple HOST/PORT
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=self.web_server_port)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()

    def generate_es_link(self, a_payload_data):

        if 'hash' in a_payload_data:
            temp_hash = a_payload_data['hash']
            temp_url = 'https://etherscan.io/tx/{}'.format(temp_hash)
            return temp_url
        else:
            print('Error, no hash key')


def main():
    bot_1 = commands.Bot(command_prefix='$')

    @bot_1.event
    async def on_ready():
        print("We are logged in as user {}".format(bot_1.user))

    setup(bot_1)
    bot_1.run(os.getenv('D_TOKEN'))


if __name__ == "__main__":
    main()