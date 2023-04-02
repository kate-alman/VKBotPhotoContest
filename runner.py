import asyncio
import logging


def run(
    start_tasks: list[asyncio.coroutines], stop_tasks: list[asyncio.coroutines]
) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    try:
        for task in start_tasks:
            loop.create_task(task())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.exception(f"Error: {e}")
    finally:
        try:
            tasks_to_stop = [loop.create_task(task()) for task in stop_tasks]
            loop.run_until_complete(
                asyncio.gather(*tasks_to_stop, return_exceptions=True)
            )
        except KeyboardInterrupt:
            pass
        finally:
            if not loop.is_closed():
                loop.close()
