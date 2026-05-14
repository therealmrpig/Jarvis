import asyncio
from jarvis.engine import Engine

async def main():
    engine = Engine()
    try:
        await engine.start()
    except asyncio.CancelledError:
        pass
    finally:
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())