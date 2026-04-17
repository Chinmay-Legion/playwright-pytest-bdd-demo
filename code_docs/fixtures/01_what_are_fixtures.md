# Fixtures 01 — What Are Fixtures & Why They Exist

> **Goal:** Understand the exact problem fixtures solve, how pytest discovers and runs them, and the vocabulary you need before going deeper.

---

## The World Without Fixtures

Let's say you have 4 tests that all need a browser page pointed at the login page.

```python
def test_valid_login():
    browser = chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.saucedemo.com/v1/")
    page.locator("#user-name").fill("standard_user")
    page.locator("#password").fill("secret_sauce")
    page.locator("#login-button").click()
    assert page.url == "https://www.saucedemo.com/v1/inventory.html"
    page.close()
    context.close()
    browser.close()

def test_invalid_login():
    browser = chromium.launch()       # copy-pasted
    context = browser.new_context()   # copy-pasted
    page = context.new_page()         # copy-pasted
    page.goto("https://www.saucedemo.com/v1/")  # copy-pasted
    page.locator("#user-name").fill("wrong_user")
    page.locator("#password").fill("wrong_pass")
    page.locator("#login-button").click()
    assert page.locator(".error-button").is_visible()
    page.close()       # forgot this once → browser process leaked
    context.close()
    browser.close()

# ... 2 more tests, all repeating the same 4 lines of setup ...
```

**Problems:**
1. **Repetition** — setup is copy-pasted across every test
2. **Fragility** — change the launch arguments (e.g. add `headless=False`) and you touch every test
3. **Leaks** — forget `browser.close()` once and you have a dangling process
4. **Noise** — 5 lines of setup before you even get to what the test is actually testing

---

## What a Fixture Is

A fixture is a function marked with `@pytest.fixture` that:
1. Runs **before** any test that needs it
2. **Returns (or yields) a value** — that value is what the test receives
3. Optionally **tears down** after the test finishes (via `yield`)

```python
import pytest

@pytest.fixture
def username():
    return "standard_user"      # test receives this string
```

```python
def test_login(username):       # pytest sees "username" → runs the fixture → injects the value
    assert len(username) > 0
```

pytest matches the **parameter name** `username` to the **fixture name** `username`. You never call `username()` yourself. pytest does it. This is the core mechanism.

---

## How pytest Discovers and Injects Fixtures

When pytest sees `def test_login(username, page, login_page)`:

1. It looks at each parameter name
2. For each name, it searches for a fixture with that name — in this order:
   - The test file itself
   - The `conftest.py` in the same folder
   - `conftest.py` files in parent folders (up to the root)
   - Built-in pytest fixtures (`tmp_path`, `capsys`, etc.)
   - Plugin-provided fixtures (`page`, `browser` from pytest-playwright)
3. It runs each fixture function and passes the return value as the argument

If no fixture is found → `FixtureError` at collection time (before any test runs).

---

## The Simplest Fixture

```python
# conftest.py
import pytest

@pytest.fixture
def base_url():
    return "https://www.saucedemo.com/v1/"
```

```python
# test_login.py
def test_navigate(page, base_url):   # "page" from playwright, "base_url" from conftest
    page.goto(base_url)
    assert "saucedemo" in page.url
```

Now if the URL changes, you change it in **one place** — the fixture.

---

## Fixtures Can Use Other Fixtures

This is the feature that makes fixtures scale. A fixture can declare parameters just like a test — pytest injects them the same way.

```python
@pytest.fixture
def base_url():
    return "https://www.saucedemo.com/v1/"

@pytest.fixture
def login_page(page, base_url):    # depends on TWO other fixtures
    page.goto(base_url)
    return SauceLoginPage(page)

def test_login(login_page):        # gets the fully navigated page object
    login_page.login("standard_user", "secret_sauce")
```

pytest builds a **dependency graph** and resolves it automatically. You declare what you need — pytest figures out the order.

---

## Fixtures vs Helper Functions — When to Use Each

A common question: why not just call a helper function?

```python
# Helper function approach
def make_login_page(page):
    page.goto(URL)
    return SauceLoginPage(page)

def test_login(page):
    login_page = make_login_page(page)   # you call it manually
    ...
```

Use a **helper function** when:
- The thing has no setup/teardown
- It's only used in one test file
- It doesn't depend on other fixtures

Use a **fixture** when:
- It needs teardown (browser, DB connection, temp file)
- Multiple tests need the same setup
- It depends on other fixtures (scope, browser, config)
- You want pytest to manage its lifetime

---

## Built-in Fixtures You Get for Free

pytest ships with useful fixtures. pytest-playwright adds browser-specific ones.

| Fixture | Source | What it gives you |
|---------|--------|-------------------|
| `tmp_path` | pytest | A temporary directory, auto-deleted |
| `capsys` | pytest | Capture stdout/stderr |
| `monkeypatch` | pytest | Safely patch objects, env vars, imports |
| `request` | pytest | Info about the current test (name, params, markers) |
| `browser` | pytest-playwright | A launched Chromium/Firefox/WebKit instance |
| `context` | pytest-playwright | A browser context (isolated session) |
| `page` | pytest-playwright | A browser page (tab) — what you use most |

---

## Parameterized Fixtures — One Fixture, Multiple Values

You can tell pytest to run the fixture (and every test using it) once per value:

```python
@pytest.fixture(params=["standard_user", "problem_user", "performance_glitch_user"])
def valid_username(request):
    return request.param      # request.param = the current value

def test_login(page, valid_username):
    # This test runs 3 times — once per username
    page.goto(URL)
    page.locator("#user-name").fill(valid_username)
    ...
```

pytest generates 3 test cases automatically:
```
test_login[standard_user]          PASSED
test_login[problem_user]           PASSED
test_login[performance_glitch_user] PASSED
```

This is useful for cross-browser testing:
```python
@pytest.fixture(params=["chromium", "firefox", "webkit"])
def browser_name(request):
    return request.param
```

---

## What's Next

- [02 — Dependency Injection](./02_dependency_injection.md) — the concept behind how fixtures are provided to tests
- [03 — Fixture Scopes](./03_fixture_scopes.md) — controlling how long a fixture lives
