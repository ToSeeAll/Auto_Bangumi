from typing import Union

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import logging

from core.rss_collector import RSSCollector
from core.download_client import DownloadClient
from conf import settings
from utils import json_config

logger = logging.getLogger(__name__)

app = FastAPI()


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)


class Config(BaseModel):
    rss_link: str
    host: str
    user_name: str
    password: str
    download_path: str
    method: str
    enable_group_tag: bool
    not_contain: str
    debug_mode: bool
    season_one_tag: bool
    remove_bad_torrent: bool
    enable_eps_complete: bool


@app.post("/api/v1/config")
async def config(config: Config):
    data = {
        "rss_link": config.rss_link,
        "host": config.host,
        "user_name": config.user_name,
        "password": config.password,
        "download_path": config.download_path,
        "method": config.method,
        "enable_group_tag": config.enable_group_tag,
        "not_contain": config.not_contain,
        "debug_mode": config.debug_mode,
        "season_one": config.season_one_tag,
        "remove_bad_torrent": config.remove_bad_torrent,
        "enable_eps_complete": config.enable_eps_complete
    }
    json_config.save("/config/config.json", data)
    return "received"


class RSS(BaseModel):
    link: str


@app.post("/api/v1/subscriptions")
async def receive(link: RSS):
    data = RSSCollector().collect_collection(link.link)
    from const_dev import DEV_SETTINGS
    settings.init(DEV_SETTINGS)
    client = DownloadClient()
    client.add_collection_feed(link.link, item_path=data["title"])
    client.set_rule(data, link.link)
    return "Successed"


class Search(BaseModel):
    group: str
    title: str
    subtitle: str


@app.post("/api/v1/search")
async def search(input: Search):
    return "Nothing Happened"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.webui_port)