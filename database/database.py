import os

from dotenv import load_dotenv
from asyncmy import create_pool


load_dotenv()


grow_pool = None
main_pool = None


async def init_databases():
    global grow_pool, main_pool

    if grow_pool is None:
        grow_pool = await create_pool(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),

            minsize=5,
            maxsize=10,

            autocommit=True,
            pool_recycle=300
        )

    if main_pool is None:
        main_pool = await create_pool(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("MAIN_DB_NAME"),

            minsize=5,
            maxsize=10,

            autocommit=True,
            pool_recycle=300
        )


def get_grow_pool():
    return grow_pool


def get_main_pool():
    return main_pool


async def close_databases():
    global grow_pool, main_pool

    if grow_pool is not None:
        grow_pool.close()
        await grow_pool.wait_closed()
        grow_pool = None

    if main_pool is not None:
        main_pool.close()
        await main_pool.wait_closed()
        main_pool = None