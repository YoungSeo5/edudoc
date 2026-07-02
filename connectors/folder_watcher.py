"""
로컬 폴더 watcher (Phase 0의 유일한 커넥터).

지정한 폴더를 감시하다가 새 파일이 들어오면 파이프라인으로 넘긴다.
Notion / Google Drive 커넥터는 이 인터페이스를 나중에 확장하는 과제로 둔다.

의존성: watchdog  (requirements.txt 참고)
watchdog 미설치 시에도 import 에러 없이 안내만 하도록 방어 처리.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    _HAS_WATCHDOG = True
except Exception:  # noqa: BLE001
    FileSystemEventHandler = object  # type: ignore
    Observer = None  # type: ignore
    _HAS_WATCHDOG = False


class _Handler(FileSystemEventHandler):  # type: ignore[misc]
    def __init__(self, on_file: Callable[[Path], None]) -> None:
        self._on_file = on_file

    def on_created(self, event) -> None:  # noqa: ANN001
        if not event.is_directory:
            self._on_file(Path(event.src_path))


def watch(folder: Path, on_file: Callable[[Path], None]) -> None:
    """folder 를 감시하며 새 파일마다 on_file(path) 호출. Ctrl+C로 종료."""
    if not _HAS_WATCHDOG:
        raise RuntimeError(
            "watchdog 미설치. `pip install watchdog` 후 다시 실행하세요. "
            "(감시 없이 한 번만 처리하려면 main.py의 'run' 명령을 쓰세요.)"
        )

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    observer.schedule(_Handler(on_file), str(folder), recursive=True)
    observer.start()
    print(f"[watch] 감시 시작: {folder}  (Ctrl+C 종료)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[watch] 종료")
    observer.join()
