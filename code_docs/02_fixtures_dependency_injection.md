# 02 — Fixtures, Dependency Injection & Fixture Chaining

> **Goal:** Understand what fixtures are, how pytest injects them automatically, how to control their lifetime, and how to chain them together — the foundation of scalable test architecture.

---

## The Problem Fixtures Solve

Imagine every test needs a browser page. Without fixtures you'd write:

```python
def test_login():
    browser = launch_browser()
    page = browser.new_page()
    page.goto("https://example.com")
    # ... test ...
    browser.close()         # must remember this every time

def test_products():
    browser = launch_browser()   # copy-pasted again
    page = browser.new_page()
    ...
```

This is fragile — if setup changes, you fix it in 50 places. Fixtures solve this.

---

## What is a Fixture?

A fixture is a function decorated with `@pytest.fixture`. pytest runs it before any test that requests it, and optionally tears it down after.

```python
import pytest

@pytest.fixture
def username():
    return "standard_user"     # setup — returns the value

def test_login(username):      # pytest sees "username" parameter, finds the fixture
    assert username == "standard_user"
```

**Key insight:** pytest matches parameter names to fixture names. `def test_login(username)` tells pytest *"I need the fixture called `username`."* You never call `username()` yourself — pytest does it.

This is **Dependency Injection (DI)**: the test declares what it needs; the framework provides it.

---

## Dependency Injection — The Core Idea

DI means: *don't create your dependencies — declare them, and let something else provide them.*

```python
# WITHOUT DI — test creates its own dependencies (tightly coupled)
def test_login():
    page = launch_browser().new_page()   # test is responsible for browser lifecycle
    page.goto(URL)
    ...

# WITH DI — test declares what it needs (loosely coupled)
def test_login(page):    # "page" is a fixture provided by pytest-playwright
    page.goto(URL)       # test just uses it — no setup, no teardown
    ...
```

Benefits for large projects:
- Change how the browser starts → change one fixture, zero tests
- Swap real browser for mock → swap the fixture, tests don't know
- Add logging/recording → add it to the fixture once

---

## Fixture Scopes — Controlling Lifetime

Scope controls how often pytest creates and destroys a fixture.

| Scope | Created once per... | Destroyed after... |
|-------|--------------------|--------------------|
| `function` | test function (default) | that test ends |
| `class` | test class | all methods in class done |
| `module` | `.py` file | all tests in file done |
| `session` | entire test run | all tests done |

```python
@pytest.fixture(scope="function")   # default — fresh browser page per test
def page():
    ...

@pytest.fixture(scope="session")    # one browser for the whole run (faster)
def browser():
    ...
```

**Industry rule:** Use the widest scope that keeps tests independent.
- `session` for expensive things: browser launch, database connection
- `function` for things that must be clean per test: page state, logged-in session

In this project, `conftest.py` uses `scope="session"` for `browser_context_args` because viewport config never changes between tests.

---

## Setup and Teardown with `yield`

Use `yield` to split a fixture into setup and teardown:

```python
@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page              # ← test runs here, receives this value
    page.close()            # ← teardown: runs after test, even if test failed
```

Everything **before** `yield` = setup.  
Everything **after** `yield` = teardown (guaranteed to run).

This is equivalent to `try/finally` — pytest handles cleanup even on test failure.

---

## conftest.py — The Shared Fixture File

`conftest.py` is a special file pytest loads automatically for every test in the same folder (and subfolders). You put fixtures here when multiple test files need them.

```
tests/
  conftest.py              ← fixtures available to ALL test files below
  test_sd_login_steps.py   ← can use fixtures from conftest.py
  test_pta_login_steps.py  ← can also use fixtures from conftest.py
```

You can have multiple conftest files at different levels:

```
conftest.py                ← project-wide fixtures (e.g. database)
tests/
  conftest.py              ← test-suite fixtures (e.g. browser config)
  auth/
    conftest.py            ← auth-specific fixtures (e.g. logged-in user)
    test_login.py
```

pytest walks up the folder tree loading all conftest files. Inner fixtures override outer ones with the same name.

---

## Fixture Chaining — Fixtures That Use Other Fixtures

Fixtures can depend on other fixtures. This is **fixture chaining**.

```python
@pytest.fixture(scope="session")
def browser():
    b = playwright.chromium.launch()
    yield b
    b.close()

@pytest.fixture
def page(browser):         # ← requests the "browser" fixture
    p = browser.new_page()
    yield p
    p.close()

@pytest.fixture
def login_page(page):      # ← requests "page", which requested "browser"
    lp = SauceLoginPage(page)
    lp.navigate()
    return lp

def test_login(login_page):   # gets the fully built login page
    login_page.login("user", "pass")
```

The chain: `test_login` → needs `login_page` → needs `page` → needs `browser`.  
pytest resolves the entire chain automatically, in the right order.

This is how `pytest-playwright` works internally — it gives you `browser`, `context`, and `page` as chainable fixtures out of the box.

---

## target_fixture — Step Definitions as Fixtures (pytest-bdd specific)

In pytest-bdd, `@given`/`@when`/`@then` step functions are NOT fixtures by default. `target_fixture` promotes a step's return value into a fixture.

```python
@given("the user is on the SauceDemo login page", target_fixture="login_page")
def navigate_to_sd_login(page: Page) -> SauceLoginPage:
    login_page = SauceLoginPage(page)
    login_page.navigate()
    return login_page        # ← registered as fixture "login_page" for this scenario
```

Now any subsequent step in the same scenario can request `login_page` as a parameter:

```python
@when('the user logs in with ...')
def login_with_credentials(login_page, username, password):
    login_page.login(username, password)   # same object, not re-created
```

Without `target_fixture` you would have to use a global variable or re-create the page object in every step — both are bad patterns.

---

## The Full Pattern in This Project

```
pytest-playwright provides:
  browser (session) → context (session) → page (function)
                                                ↓
test_sd_login_steps.py @given uses page:
  page → SauceLoginPage (registered as "login_page" via target_fixture)
                ↓
conftest.py @when receives "login_page":
  login_page.login(username, password)
                ↓
test_sd_login_steps.py @then receives "login_page":
  login_page.assert_error_visible()
```

One browser. One page. One login page object. Shared across all steps. No globals. No repetition.

---

## Industry Standards for Fixtures in Large Projects

**1. Keep fixtures small and single-purpose**
```python
# Bad — does too much
@pytest.fixture
def setup():
    db = connect_db()
    user = create_user(db)
    browser = launch_browser()
    yield browser, db, user
    cleanup(db)

# Good — separate concerns, chain them
@pytest.fixture(scope="session")
def db(): ...

@pytest.fixture
def user(db): ...

@pytest.fixture
def authenticated_page(page, user): ...
```

**2. Use the right scope — don't default everything to `function`**
- `session`: browser, DB connection, auth tokens that don't change
- `function`: page state, test data that must be isolated

**3. Put shared fixtures in conftest.py, feature-specific ones in the test file**

**4. Never use global variables to share state between steps — use `target_fixture` or fixtures**

**5. Fixtures compose better than inheritance** — prefer building fixtures from other fixtures over subclassing test classes.

---

## Vocabulary Cheatsheet

| Term | Meaning |
|------|---------|
| **Fixture** | A function that provides setup/teardown to tests |
| **DI (Dependency Injection)** | Declare what you need; framework provides it |
| **Fixture scope** | How long a fixture lives (`function`, `session`, etc.) |
| **yield fixture** | Fixture with teardown after the yield |
| **conftest.py** | Shared fixture file auto-loaded by pytest |
| **Fixture chaining** | A fixture that depends on another fixture |
| **target_fixture** | pytest-bdd: promote a step's return value to a fixture |

---

## What's Next

Doc 03 covers **pytest-bdd** — Gherkin syntax, feature files, step definitions, parsers, and how everything in this project connects end to end.
