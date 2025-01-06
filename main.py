import time
from app.core.config import settings
import asyncio
from app.core import db


async def main():
    print("Hello, world!")
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
