import asyncio


async def main():
    print("Hello, world!")
    while True:
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
