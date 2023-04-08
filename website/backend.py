import json

from aiohttp.web import HTTPFound, Request, Response, RouteTableDef, json_response
from voxelbotutils import web as webutils
import aiohttp_session
import discord
from aiohttp_jinja2 import template

from cogs import utils as botutils


routes = RouteTableDef()


@routes.get('/login_processor')
async def login_processor(request: Request):
    """
    Page the discord login redirects the user to when successfully logged in with Discord.
    """

    v = await webutils.process_discord_login(request)
    if isinstance(v, Response):
        return HTTPFound('/')
    session = await aiohttp_session.get_session(request)
    return HTTPFound(location=session.pop('redirect_on_login', '/'))


@routes.get('/logout')
async def logout(request: Request):
    """
    Destroy the user's login session.
    """

    session = await aiohttp_session.get_session(request)
    session.invalidate()
    return HTTPFound(location='/')


@routes.get('/login')
async def login(request: Request):
    """
    Direct the user to the bot's Oauth login page.
    """

    return HTTPFound(location=webutils.get_discord_login_url(request, "/login_processor"))


@routes.post('/fish_info')
async def fish_info(request: Request):
    """
    Get the fish info of the page
    """
    data = await request.json()  # Parse the request body as JSON
    fish_index = int(data)  # Convert the data to an integer

    fish = botutils.fetch_fish("website/static/images/bot-images/fish")

    print(str(fish[fish_index].image))
    fish_info = {
        "name": str(fish[fish_index].name),
        "image": str(fish[fish_index].image),
        "rarity": str(fish[fish_index].rarity),
        "size": str(fish[fish_index].size),
        "location": str(fish[fish_index].location)
    }

    return json_response(fish_info)


@routes.post('/fish_names')
async def fish_names(request: Request):
    """
    Get all fish names
    """

    fish = botutils.fetch_fish("website/static/images/bot-images/fish")

    fish_names = []
    for single_fish in fish:
        fish_names.append(single_fish.name.replace("_", " ").title())

    fish_names_formatted = {
        'names': fish_names
    }

    return json_response(fish_names_formatted)


@routes.post('/fish_position')
async def fish_position(request: Request):
    """
    Get all fish names
    """

    data = await request.json()
    fish = botutils.fetch_fish("website/static/images/bot-images/fish")

    fish_names = []
    for single_fish in fish:
        fish_names.append(single_fish.name)

    position = fish_names.index(str(data))

    fish_position_formatted = {
        'position': position
    }

    return json_response(fish_position_formatted)
