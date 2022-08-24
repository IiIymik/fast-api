from fastapi import FastAPI
import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./database.db")
Session = sessionmaker(bind=engine)


class Film(BaseModel):
    cinema: str
    title: str
    age: str
    session: str


app = FastAPI()


def get_db():
    return Session()


@app.get("/")
def read_root():
    return {"Test": "Hello"}


@app.get("/doc")
def read_root():
    return 'There is the page on documentation. You can learn more by the following link https://www.uvicorn.org/'


@app.get('/film_zhovten/{film_id}', response_model=Film)
async def get_film_zhovten():
    async with aiohttp.ClientSession() as session:
        url = "https://zhovten-kino.kiev.ua/sessions"
        async with session.get(url) as response:
            text = await response.read()
            results = BeautifulSoup(text, "lxml").find_all(
                'div', class_="schedule__films")
            for result in results:
                return Film(cinema="Zhovten",
                            title=result.find(
                                'p', class_="schedule__film__title").text,
                            age=result.find(
                                'div', class_='age_restriction').text,
                            session=result.find('div', class_="session").text.replace('\n',
                                                                                      ' ').strip(),
                            )


@app.get('/film_multiplex/{film_id}', response_model=Film)
async def get_film_multiplex():
    async with aiohttp.ClientSession() as session:
        url = "https://multiplex.ua/ru/cinema/kyiv/lavina"
        async with session.get(url) as response:
            text = await response.read()
            results = BeautifulSoup(text, "lxml").find_all(
                'div', class_="film")
            for result in results:
                try:
                    return Film(cinema="Multiplex",
                                title=result.find('div', class_="title").text.replace(
                                    '\n', '').lstrip(),
                                age=result.find('span', class_="age").text,
                                session=result.find('div', class_="sessions showmore").text.replace(
                                    '\n', ' ').strip(),
                                )
                except AttributeError as e:
                    print(e)