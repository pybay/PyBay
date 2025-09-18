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
from lektor.project import Project
from lektor import db


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


def run_static_server(directory: str, port: int):
    # Lightweight static HTTP server rooted at the built output directory
    from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

    class RootedHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    httpd = ThreadingHTTPServer(("127.0.0.1", port), RootedHandler)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()


@pytest.fixture(scope="session")
def built_site_dir(tmp_path_factory) -> Path:
    """Build the Lektor site once and return the output directory."""
    repo_root = Path(__file__).resolve().parents[1]
    site_dir = repo_root 
    out_dir = tmp_path_factory.mktemp("lektor-build")
    subprocess.run([
        "lektor", "build", "-O", str(out_dir)
    ], cwd=str(site_dir), check=True)
    return out_dir


@pytest.fixture(scope="session")
def base_url(free_port: int, built_site_dir: Path) -> Generator[str, None, None]:
    proc = Process(target=run_static_server, args=(str(built_site_dir), free_port), daemon=True)
    proc.start()
    url = f"http://localhost:{free_port}/"
    wait_for_server_ready(url, timeout=10.0, check_interval=0.5)
    yield url
    proc.kill()

    
def get_pages(query, pad, pages: set[str]):
    for page in query.all():
        # lektor gives us page names without a trailing slash, but 
        # our server redirects to the page with the trailing slash. 
        # it doesn't cause any issues, but makes logs chattier and 
        # is probably imperceptibly slower
        pages.add(f"{page.path}/")  
        get_pages(db.Query(page.path, pad), pad, pages)
    return pages
    
def all_pages() -> list[str]:
    project = Project.discover()
    env = project.make_env()
    pad = env.new_pad()
    return get_pages(db.Query("/", pad), pad, set())
    

@pytest.mark.parametrize("lektor_page", all_pages())
def test_all_posts(page: Page, base_url: str, lektor_page: str):
    page.goto(lektor_page)
    results = Axe().run(page)
    assert results.violations_count == 0, results.generate_report()