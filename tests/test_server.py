import socket
import time
import subprocess
from collections.abc import Generator
from contextlib import closing
from multiprocessing import Process
from pathlib import Path

import pytest
import requests
from playwright.sync_api import Page, expect
from axe_playwright_python.sync_playwright import Axe

expect.set_options(timeout=10_000)


def wait_for_server_ready(url: str, timeout: float = 10.0, check_interval: float = 0.5) -> bool:
    """Make requests to provided url until it responds without error."""
    conn_error = None
    for _ in range(int(timeout / check_interval)):
        try:
            requests.get(url)
        except requests.ConnectionError as exc:
            time.sleep(check_interval)
            conn_error = str(exc)
        else:
            return True
    raise RuntimeError(conn_error)


@pytest.fixture(scope="session")
def free_port() -> int:
    """Returns a free port for the test server to bind."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def run_server(port: int):
    repo_root = Path(__file__).resolve().parents[1]
    site_dir = repo_root / "PyBay"
    subprocess.run(
        [
            "lektor",
            "server",
            "-h",
            "127.0.0.1",
            "-p",
            str(port),
        ],
        cwd=str(site_dir),
        check=True,
    )

@pytest.fixture()
def live_server_url(free_port: int) -> Generator[str, None, None]:
    proc = Process(target=run_server, args=(free_port,), daemon=True)
    proc.start()
    url = f"http://localhost:{free_port}/"
    wait_for_server_ready(url, timeout=10.0, check_interval=0.5)
    yield url
    proc.kill()


def test_home(page: Page, live_server_url: str):
    page.goto(live_server_url)
    expect(page).to_have_title("PyBay 2025 - 10th Annual Bay Area Python Dev Conference - Welcome to PyBay!")
    results = Axe().run(page)
    assert results.violations_count == 0, results.generate_report()