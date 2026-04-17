# Fixtures 03 — Fixture Scopes

> **Goal:** Understand the five fixture scopes, what "scope" actually means in terms of creation and destruction, and how to pick the right scope for every situation in a large project.

---

## What Scope Means

**Scope** = how many times pytest creates and destroys a fixture during a test run.

The wider the scope, the fewer times the fixture is created. The narrower the scope, the more isolated each test is.

This is always a trade-off:
- **Wider scope** → faster (less setup/teardown), but tests share state → harder to isolate
- **Narrower scope** → slower (more setup/teardown), but each test is fully independent → easier to debug

---

## The Five Scopes

```
session  →  created once for the entire pytest run
package  →  created once per package (folder with __init__.py)
module   →  created once per .py file
class    →  created once per test class
function →  created once per test function  ← DEFAULT
```

Visualized for a run with 3 test files, 2 tests each:

```
pytest run starts
│
├── session fixture created (1 time total)
│
├── test_login.py starts
│   ├── module fixture created (1 time per file)
│   ├── test_valid_login
│   │   ├── function fixture created
│   │   ├── TEST RUNS
│   │   └── function fixture destroyed
│   ├── test_invalid_login
│   │   ├── function fixture created
│   │   ├── TEST RUNS
│   │   └── function fixture destroyed
│   └── module fixture destroyed
│
├── test_products.py starts
│   ├── module fixture created (again, for this file)
│   ...
│
└── session fixture destroyed (at the very end)
```

---

## `function` Scope (Default)

Created before each test, destroyed after each test. Most isolated.

```python
@pytest.fixture                       # scope="function" is the default
def page(context):
    page = context.new_page()
    yield page
    page.close()
```

**When to use:** Anything that tests might mutate.
- Browser page state (URL, form values, cookies)
- Database records
- In-memory state

**In this project:** `page` is function-scoped (provided by pytest-playwright). Every test gets a clean tab. One test filling in a username doesn't affect the next test.

```
test_valid_login   → page created → test runs → page closed
test_invalid_login → page created → test runs → page closed   ← fresh page
test_locked_out    → page created → test runs → page closed   ← fresh page
```

---

## `session` Scope

Created once when the test run starts, destroyed when it ends. Fastest, least isolated.

```python
@pytest.fixture(scope="session")
def browser():
    b = playwright.chromium.launch(headless=True)
    yield b
    b.close()
```

**When to use:** Expensive resources that don't hold per-test state.
- Browser process (launching takes ~1-2 seconds — multiplied by 100 tests = slow)
- Database connections
- Auth tokens that are valid for the whole run
- Configuration loaded from files/env

**In this project:**

```python
# conftest.py
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {**browser_context_args, "viewport": {"width": 1920, "height": 1080}}
```

The viewport config doesn't change between tests — session scope is correct. pytest-playwright internally uses session scope for the browser process itself.

**Performance difference — real numbers:**

```
100 tests, browser launch = 1.5 seconds

function scope: 100 × 1.5s = 150 seconds of just browser setup
session scope:  1 × 1.5s   = 1.5 seconds total

Winner: session scope saves ~148 seconds on 100 tests
```

---

## `module` Scope

Created once per test file. Useful when tests in a file share setup that's expensive but tests in different files should be independent.

```python
@pytest.fixture(scope="module")
def test_data():
    data = load_large_csv("test_data.csv")   # slow to load
    return data
```

**When to use:**
- Shared test data that all tests in a file read (never mutate)
- A database seeded with data for a specific feature's tests
- API responses cached for a group of related tests

```
test_product_page.py:
  module fixture created (data loaded once)
  test_product_count     → reads data
  test_product_names     → reads data
  test_product_prices    → reads data
  module fixture destroyed

test_checkout_page.py:
  module fixture created again (different data set for checkout)
  ...
```

---

## `class` Scope

Created once per test class. Rarely needed in functional/BDD testing — more common in unit test suites.

```python
class TestLoginFlow:
    @pytest.fixture(scope="class", autouse=True)
    def setup_user(self, db):
        self.user = db.create_user("alice", "password123")
        yield
        db.delete_user(self.user.id)

    def test_login(self, page):
        page.locator("#user").fill(self.user.username)
        ...

    def test_profile_visible(self, page):
        ...   # same self.user, setup only ran once
```

**When to use:** When you group tests that share a common precondition that only makes sense within that class.

---

## `package` Scope

Created once per Python package (folder with `__init__.py`). Sits between `module` and `session`. Rarely used but useful when you have feature folders.

```
tests/
  auth/
    __init__.py
    test_login.py
    test_logout.py
  checkout/
    __init__.py
    test_cart.py
    test_payment.py
```

```python
@pytest.fixture(scope="package")
def auth_test_data():
    return seed_auth_data()   # shared across test_login.py AND test_logout.py
                              # but NOT shared with checkout/ tests
```

---

## Scope Interactions — What Happens When Scopes Mix

A **wider-scope** fixture can use a **same or wider** scope fixture. A **narrower-scope** fixture cannot use a **wider-scope** fixture directly... actually that's backwards.

The rule is:

> A fixture can only use fixtures of **equal or wider** scope.

```python
@pytest.fixture(scope="session")
def browser(): ...

@pytest.fixture(scope="function")
def page(browser):    # OK — function uses session (wider)
    return browser.new_page()

@pytest.fixture(scope="session")
def cached_page(page):  # ERROR — session cannot use function (narrower)
    ...
```

Why? Because a `session`-scoped fixture lives for the whole run. If it depended on a `function`-scoped fixture (which gets destroyed after each test), the session fixture would hold a reference to something that no longer exists.

pytest catches this and raises a `ScopeMismatch` error at collection time.

---

## The Standard Scope Stack for Browser Testing

This is the pattern pytest-playwright uses internally, and what you should follow:

```python
@pytest.fixture(scope="session")       # 1 browser per run
def browser():
    b = playwright.chromium.launch()
    yield b
    b.close()

@pytest.fixture(scope="session")       # 1 context per run (or per module, depending on isolation needs)
def context(browser):
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    yield ctx
    ctx.close()

@pytest.fixture(scope="function")      # 1 page per test — always function scope
def page(context):
    p = context.new_page()
    yield p
    p.close()
```

Why this split?
- Browser: expensive to launch → session
- Context: holds cookies/storage → reset per test (or per session if tests don't interfere)
- Page: holds URL state, form state → always function-scoped

---

## `autouse` — Apply a Fixture to Every Test Without Declaring It

```python
@pytest.fixture(autouse=True)
def reset_db_between_tests(db):
    db.truncate_test_tables()   # runs before every test automatically
    yield
    # no teardown needed — next test's setup handles it
```

`autouse=True` means: run this fixture for every test in scope — the test doesn't need to declare it as a parameter.

Combine with scope:
```python
@pytest.fixture(scope="session", autouse=True)
def start_test_server():
    server = TestServer().start()
    yield
    server.stop()
```

This starts a test server once at the beginning of the run, stops it at the end — no test has to mention it.

**Warning:** Use `autouse` sparingly. It makes behaviour invisible. Only use it for cross-cutting concerns (logging, DB reset, server start) that genuinely apply to everything.

---

## Choosing the Right Scope — Decision Guide

```
Is this fixture expensive to create (browser, DB connection, server)?
  YES → session or module scope

Does the fixture hold state that tests might mutate (page URL, form values, records)?
  YES → function scope (fresh per test)
  NO  → wider scope is safe

Is this fixture read-only (config, URLs, credentials, test data that tests never write to)?
  YES → session scope — safe to share

Is this fixture tied to one feature's test file?
  YES → module scope

Are you unsure?
  → Start with function scope. You can always widen it later for performance.
     Going the other way (widening → narrowing) means finding subtle bugs.
```

---

## Real Scope Decisions in a Large Project

```python
# session — browser process. Created once. Never mutated.
@pytest.fixture(scope="session")
def browser(): ...

# session — config. Read from env once. Never changes.
@pytest.fixture(scope="session")
def config():
    return {"base_url": os.getenv("BASE_URL"), "api_key": os.getenv("API_KEY")}

# module — test data seeded for a whole feature's tests.
@pytest.fixture(scope="module")
def product_catalog(db):
    products = db.seed_products(count=20)
    yield products
    db.delete_products(products)

# function — page state. Always fresh per test.
@pytest.fixture
def page(context): ...

# function — logged-in session. Each test needs a clean auth state.
@pytest.fixture
def authenticated_page(page, config):
    page.goto(config["base_url"])
    page.locator("#user").fill("standard_user")
    page.locator("#pass").fill("secret_sauce")
    page.locator("#btn").click()
    return page
```

---

## What's Next

- [04 — Yield and Teardown](./04_yield_and_teardown.md) — how to reliably clean up after tests
- [05 — Fixture Chaining](./05_fixture_chaining.md) — building complex fixture pipelines
