import json
import aiofiles
from pathlib import Path
from json import JSONDecodeError

from core.logger import log_error

async def read_json(path: Path):
    """
    Read and parse JSON from a file.
    Returns parsed data (dict or list).
    """
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content) if content else []

    except FileNotFoundError:
        # Legitimate "empty" state for many use cases
        return []

    except JSONDecodeError as e:
        # Corrupt JSON
        log_error(f"Invalid JSON in {path}", exc=e)
        raise

    except Exception as e:
        # Unexpected error
        log_error(f"Failed to read JSON file {path}", exc=e)
        raise


async def write_json(path: Path, data) -> None:
    """
    Write data as formatted JSON to a file.
    """
    try:
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(
                json.dumps(data, ensure_ascii=False, indent=4)
            )

    except Exception as e:
        log_error(f"Failed to write JSON file {path}", exc=e)
        raise


async def wipe_json(path: Path) -> None:
    """
    Clear a JSON file by writing an empty list.
    """
    await write_json(path, [])
