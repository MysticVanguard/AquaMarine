from urllib.parse import urlencode

from aiohttp.web import HTTPFound, Request, Response, RouteTableDef
from voxelbotutils import web as webutils
import aiohttp_session
import discord
from aiohttp_jinja2 import template
from flask import Flask, request, session, redirect, url_for, render_template, flash

from cogs import utils as botutils


routes = RouteTableDef()


@routes.get("/")
@template('index.html.j2')
@webutils.add_discord_arguments()
async def index(request: Request):
    """
    Index of the website, has "login with Discord" button.
    If not logged in, all pages should redirect here.
    """

    return {}

@routes.get("/bestiary")
@template('bestiary.html.j2')
@webutils.add_discord_arguments()
async def bestiary(request: Request):
    """
    Index of the website, has "login with Discord" button.
    If not logged in, all pages should redirect here.
    """

    return {}

@routes.get("/commands")
@template('commands.html.j2')
@webutils.add_discord_arguments()
async def commands(request: Request):
    """
    Index of the website, has "login with Discord" button.
    If not logged in, all pages should redirect here.
    """

    return {}

@routes.get("/use")
@template('use.html.j2')
@webutils.add_discord_arguments()
async def use(request: Request):
    """
    Index of the website, has "login with Discord" button.
    If not logged in, all pages should redirect here.
    """

    return {}
