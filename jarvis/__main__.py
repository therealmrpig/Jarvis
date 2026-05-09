import signal
import sys
import asyncio

from jarvis.engine import Engine

async def main():
    engine = Engine()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(engine.shutdown()))

    try:
        await engine.startup()
    except Exception as e:
         print(f"Error during startup: {e}")
    finally:
        # Final cleanup attempt
        await engine.shutdown()
    

    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass