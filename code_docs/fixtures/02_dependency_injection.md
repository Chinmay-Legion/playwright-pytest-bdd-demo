# Fixtures 02 — Dependency Injection

> **Goal:** Understand what Dependency Injection means, why it exists, how pytest implements it through fixtures, and why it's the pattern that makes large test suites maintainable.

---

## The Concept — Without Jargon First

Imagine a restaurant kitchen.

**Without DI:** Every chef buys their own knives, sharpens them, and throws them away after each dish. If the restaurant wants to switch knife brands, every chef must change their behaviour.

**With DI:** The head chef provides knives to each cook at the start of the shift. Cooks just cook. If the knife brand changes, only the head chef changes — the cooks do nothing differently.

In testing:
- **Without DI** → each test creates its own browser, page, login object. Tests are tightly coupled to *how* those things are created.
- **With DI** → fixtures create and provide those things. Tests just use them. Tests are only coupled to *what* they need, not *how* it's made.

---

## The Technical Definition

**Dependency Injection** is a pattern where an object receives its dependencies from the outside rather than creating them itself.

```python
# No DI — the test creates its own dependency
def test_login():
    page = chromium.launch().new_context().new_page()   # test is responsible
    page.goto(URL)
    page.locator("#user-name").fill("standard_user")
    ...

# With DI — the dependency is injected by pytest
def test_login(page):       # "page" is provided from outside
    page.goto(URL)          # test just uses it
    page.locator("#user-name").fill("standard_user")
    ...
```

The test doesn't know or care how `page` was created. pytest does that work.

---

## How pytest Implements DI — Step by Step

pytest uses **introspection** to implement DI. When it sees:

```python
def test_login(page, login_page, base_url):
```

It does this internally:

```
1. Inspect the function signature → parameters: ["page", "login_page", "base_url"]
2. For each parameter name, find the matching fixture
3. Check if that fixture itself has parameters → resolve those first
4. Build execution order (the dependency graph)
5. Run fixtures in order, pass return values as arguments
6. Call test_login(page=<Page>, login_page=<SauceLoginPage>, base_url="https://...")
```

You never call `test_login(...)` yourself. pytest calls it with the right arguments. That's injection.

---

## Why This Matters — The Scaling Argument

Here's a real scenario. You have 50 tests. All of them create a `SauceLoginPage` directly:

```python
# Repeated in 50 tests
def test_something(page):
    page.goto("https://www.saucedemo.com/v1/")
    login_page = SauceLoginPage(page)
    ...
```

Now your team decides to add a **retry on navigation failure** — the CI server is flaky. Without DI:

```
Touch 50 test files.
Risk: missing some. Risk: inconsistent retry logic.
```

With DI:

```python
# conftest.py — one place
@pytest.fixture
def login_page(page):
    for attempt in range(3):
        try:
            page.goto("https://www.saucedemo.com/v1/")
            break
        except TimeoutError:
            if attempt == 2: raise

    return SauceLoginPage(page)
```

```
Touch 1 file (conftest.py).
All 50 tests get the retry automatically.
```

**This is the scaling argument for DI:** the cost of changing infrastructure is O(1), not O(n tests).

---

## DI Enables Swapping Implementations

This is the most powerful use of DI in large projects.

```python
# conftest.py — production config
@pytest.fixture
def api_client():
    return RealAPIClient(base_url="https://api.myapp.com")
```

```python
# conftest.py — local dev / CI without internet
@pytest.fixture
def api_client():
    return MockAPIClient()    # same interface, fake responses
```

Your tests don't change at all:

```python
def test_create_user(api_client):
    result = api_client.create_user({"name": "Alice"})
    assert result["id"] is not None
```

The test doesn't know if `api_client` is real or mocked. You swap the fixture, the test runs against both. This is how you test in isolation without touching production.

---

## DI vs Global Variables — Why Globals Break at Scale

```python
# BAD — global state
login_page = None

def setup():
    global login_page
    login_page = SauceLoginPage(page)

def test_login():
    login_page.login("user", "pass")    # depends on setup() having run first

def test_error():
    login_page.login("wrong", "wrong")  # what if test_login mutated login_page?
```

Problems with globals:
- **Order-dependent** — tests pass if run in one order, fail in another
- **Shared mutation** — one test's side effects break the next
- **No teardown** — you must remember to reset it manually
- **Invisible dependencies** — `test_error` silently depends on `setup()` having run

```python
# GOOD — DI via fixture
@pytest.fixture
def login_page(page):
    lp = SauceLoginPage(page)
    lp.navigate()
    return lp

def test_login(login_page):    # gets its own fresh login_page
    login_page.login("user", "pass")

def test_error(login_page):    # also gets its own fresh login_page
    login_page.login("wrong", "wrong")
```

Each test gets an independent `login_page`. No shared state. No order dependency. pytest creates and destroys it per test automatically.

---

## DI in This Project — Tracing the Actual Chain

In `test_sd_login_steps.py`:

```python
@given("the user is on the SauceDemo login page", target_fixture="login_page")
def navigate_to_sd_login(page: Page) -> SauceLoginPage:
    login_page = SauceLoginPage(page)
    login_page.navigate()
    return login_page
```

`page` here is **injected** by pytest-playwright. The step doesn't create a browser — it receives one.

In `conftest.py`:

```python
@when(parsers.re(r'the user logs in with username "(?P<username>[^"]*)" ...'))
def login_with_credentials(login_page, username: str, password: str) -> None:
    login_page.login(username, password)
```

`login_page` here is **injected** by pytest-bdd's `target_fixture` mechanism. The step doesn't know how `SauceLoginPage` was built — it just calls `.login()`.

This is DI all the way down:
```
pytest-playwright injects page
    → your @given creates SauceLoginPage, returns it as "login_page"
        → pytest-bdd injects "login_page" into @when
            → @when calls login_page.login(...)
```

No step creates what it doesn't own. Every dependency is declared, not constructed.

---

## The Interface Contract — Why DI Enables Duck Typing

Because `conftest.py`'s `@when` step receives `login_page` through DI, it doesn't care about the concrete type. It only cares that the object has a `.login()` method.

```python
# SauceLoginPage — has .login()
# PtaLoginPage   — also has .login()

# conftest.py @when works with BOTH because it only calls .login()
def login_with_credentials(login_page, username, password):
    login_page.login(username, password)   # works regardless of which concrete type
```

This is the **duck typing contract** DI enables: *"I don't care what you are — I care what you can do."*

In a large project with 20 different sites being tested, you could have 20 different page objects, all sharing the same `@when` step through this mechanism.

---

## Summary — When DI Helps

| Situation | Without DI | With DI |
|-----------|-----------|---------|
| Change browser launch args | Edit every test | Edit one fixture |
| Test against mock vs real API | Conditional logic in every test | Swap the fixture |
| Add logging to every page navigation | Edit every test | Add to the fixture |
| Parallel test isolation | Manual — easy to get wrong | Automatic — each test gets its own |
| Onboard a new developer | They read every test to understand setup | They read one fixture |

---

## What's Next

- [03 — Fixture Scopes](./03_fixture_scopes.md) — controlling how long a fixture lives and when it's shared
