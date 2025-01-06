import time
from app.core.config import settings
import asyncio
from app.core.db import get_version


async def main():
    db_version = await get_version()
    print(f'{db_version=}')


if __name__ == "__main__":
    asyncio.run(main())
