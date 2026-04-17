# Fixtures 05 — Fixture Chaining

> **Goal:** Understand how fixtures compose into chains and pipelines, how pytest resolves the dependency graph, and how to use chaining to build scalable test infrastructure for large projects.

---

## What Fixture Chaining Is

Fixture chaining is when a fixture declares another fixture as its dependency. The chain can be as deep as needed — pytest resolves all dependencies automatically.

```python
@pytest.fixture(scope="session")
def browser():
    return playwright.chromium.launch()

@pytest.fixture
def page(browser):          # depends on "browser"
    return browser.new_page()

@pytest.fixture
def login_page(page):       # depends on "page", which depends on "browser"
    page.goto("https://www.saucedemo.com/v1/")
    return SauceLoginPage(page)

def test_login(login_page):     # depends on "login_page"
    login_page.login("standard_user", "secret_sauce")
```

The full chain: `test_login → login_page → page → browser`

pytest resolves this chain bottom-up:
1. Creates `browser` (session scope)
2. Creates `page` (function scope) using `browser`
3. Creates `login_page` (function scope) using `page`
4. Runs `test_login` with `login_page`

---

## How pytest Resolves the Dependency Graph

pytest builds a **directed acyclic graph (DAG)** of fixture dependencies.

```
test_login
    └── login_page
            └── page
                    └── browser
```

For a test with multiple dependencies:

```python
def test_checkout(authenticated_page, product_catalog, config):
```

```
test_checkout
    ├── authenticated_page
    │       ├── page
    │       │     └── context
    │       │             └── browser
    │       └── credentials
    │               └── config
    ├── product_catalog
    │       └── db
    └── config          ← already resolved, reused
```

`config` is requested by both `authenticated_page` (via `credentials`) and `test_checkout` directly. pytest creates it **once** within its scope and shares the instance. No duplication.

---

## Chaining in This Project — The Actual Chain

```
pytest-playwright (built-in chain):
  playwright (session)
      → browser (session)
          → browser_context (session/function)
              → page (function)    ← what you receive as the "page" fixture

Your code adds to the chain:
  page (function)
      → SauceLoginPage created in @given step
          → returned via target_fixture="login_page"
              → injected into @when and @then steps
```

`browser_context_args` in this project's `conftest.py` plugs into pytest-playwright's chain:

```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {**browser_context_args, "viewport": {"width": 1920, "height": 1080}}
```

pytest-playwright reads `browser_context_args` when creating contexts. You're extending the chain without modifying any playwright code — just inserting a fixture with a known name.

---

## Building a Multi-Level Chain for a Large Project

Here's what a real chain looks like for a project with multiple user roles:

```python
# Level 0 — infrastructure
@pytest.fixture(scope="session")
def config():
    return {"base_url": os.getenv("BASE_URL"), "headless": True}

@pytest.fixture(scope="session")
def browser(config):
    b = playwright.chromium.launch(headless=config["headless"])
    yield b
    b.close()

# Level 1 — browser setup
@pytest.fixture
def page(browser):
    p = browser.new_page()
    yield p
    p.close()

# Level 2 — navigation
@pytest.fixture
def home_page(page, config):
    page.goto(config["base_url"])
    return HomePage(page)

@pytest.fixture
def login_page(page, config):
    page.goto(f"{config['base_url']}/login")
    return LoginPage(page)

# Level 3 — authentication (depends on Level 2)
@pytest.fixture
def standard_user_page(login_page):
    login_page.login("standard_user", "secret_sauce")
    return InventoryPage(login_page.page)

@pytest.fixture
def admin_user_page(login_page):
    login_page.login("admin_user", "admin_pass")
    return AdminDashboard(login_page.page)

# Level 4 — test-specific state (depends on Level 3)
@pytest.fixture
def cart_with_items(standard_user_page):
    standard_user_page.add_item("Sauce Labs Backpack")
    standard_user_page.add_item("Sauce Labs Bike Light")
    return CartPage(standard_user_page.page)
```

Now tests are incredibly clean:

```python
def test_checkout_total(cart_with_items):
    assert cart_with_items.item_count() == 2

def test_admin_can_see_users(admin_user_page):
    assert admin_user_page.user_list_visible()
```

Each test declares exactly what state it needs. The chain builds it. No test knows about browser launch, navigation, or login — those are infrastructure concerns.

---

## Chaining Solves the Combinatorial Problem

Without chaining, you'd need a fixture for every combination:

```python
# BAD — combinatorial explosion
@pytest.fixture
def standard_user_with_item_in_cart(page): ...

@pytest.fixture
def standard_user_on_checkout(page): ...

@pytest.fixture
def admin_user_with_item_in_cart(page): ...

@pytest.fixture
def admin_user_on_checkout(page): ...
# ... 10 user roles × 5 page states = 50 fixtures
```

With chaining, you compose:

```python
# GOOD — O(n) fixtures instead of O(n×m)
@pytest.fixture
def standard_user_page(login_page): ...     # role fixtures

@pytest.fixture
def admin_user_page(login_page): ...

@pytest.fixture
def cart_with_items(standard_user_page): ... # state fixtures

@pytest.fixture
def checkout_page(cart_with_items): ...
```

Tests pick the chain they need:

```python
def test_something(admin_user_page): ...
def test_checkout(checkout_page): ...
```

---

## `target_fixture` — Chaining Through pytest-bdd Steps

In pytest-bdd, step functions are not fixtures by default. `target_fixture` is the mechanism that inserts a step's return value into the fixture chain.

```python
# Step 1 — @given creates the page object and registers it as a fixture
@given("the user is on the SauceDemo login page", target_fixture="login_page")
def navigate_to_sd_login(page: Page) -> SauceLoginPage:
    login_page = SauceLoginPage(page)   # uses "page" fixture from pytest-playwright
    login_page.navigate()
    return login_page                   # registered as fixture "login_page"

# Step 2 — @when receives "login_page" as a fixture (from step 1's target_fixture)
@when(parsers.re(r'the user logs in with username "(?P<username>[^"]*)" ...'))
def login_with_credentials(login_page, username: str, password: str):
    login_page.login(username, password)

# Step 3 — @then also receives "login_page" — same object, not re-created
@then("the login error message should be displayed")
def verify_login_error(login_page: SauceLoginPage):
    login_page.assert_error_visible()
```

The chain through BDD steps:

```
page (pytest-playwright fixture)
    → @given step creates SauceLoginPage, target_fixture="login_page"
        → @when receives login_page, calls .login()
            → @then receives login_page, calls .assert_error_visible()
```

All three steps operate on the **same** `SauceLoginPage` instance. This is fixture chaining across BDD step boundaries.

---

## Fixture Override — Changing One Link in the Chain

Because pytest resolves fixture names by searching from the innermost conftest outward, you can **override** a fixture for a specific folder or test without touching anything else.

```
tests/
  conftest.py                ← base_url = "https://www.saucedemo.com"
  test_sd_login_steps.py     ← uses base_url from above
  staging/
    conftest.py              ← base_url = "https://staging.saucedemo.com"  (override)
    test_sd_staging.py       ← uses staging base_url
```

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def base_url():
    return "https://www.saucedemo.com/v1/"

# tests/staging/conftest.py
@pytest.fixture(scope="session")
def base_url():
    return "https://staging.saucedemo.com/v1/"   # overrides for staging/ only
```

Every other fixture in the chain (`login_page`, `page`, etc.) still works unchanged — they just get a different `base_url`. You changed one link, the whole chain adapts.

This is how teams run the same tests against production, staging, and local environments without duplicating test code.

---

## Chaining Anti-Patterns to Avoid

**1. Fixture that does too much (god fixture)**

```python
# BAD — one fixture sets up everything
@pytest.fixture
def everything(page):
    page.goto(URL)
    login(page)
    add_item_to_cart(page)
    go_to_checkout(page)
    return page

def test_checkout_total(everything):   # can't reuse any intermediate state
    ...
```

```python
# GOOD — chain of focused fixtures
@pytest.fixture
def login_page(page): ...
@pytest.fixture
def inventory_page(login_page): ...
@pytest.fixture
def cart_page(inventory_page): ...
@pytest.fixture
def checkout_page(cart_page): ...

def test_checkout_total(checkout_page): ...   # clean, composable
def test_cart_count(cart_page): ...           # reuses earlier link in the chain
```

**2. Sharing mutable state through a wide-scope fixture**

```python
# BAD — session-scoped fixture holds mutable list
@pytest.fixture(scope="session")
def cart():
    return []   # every test adds to the same list!

def test_a(cart):
    cart.append("item1")   # mutates session fixture

def test_b(cart):
    assert len(cart) == 0  # FAILS — test_a's mutation persists
```

```python
# GOOD — function scope for mutable state
@pytest.fixture
def cart():
    return []   # fresh list per test
```

**3. Deep chains with hidden coupling**

If your chain is 8 levels deep and you don't know what changed when a test breaks, the chain is too opaque. Keep chains to 4-5 levels max. Use `conftest.py` comments to document what each level provides.

---

## Reading the Chain — How to Debug Fixture Issues

Run pytest with `--setup-show` to see exactly which fixtures are set up and torn down for each test:

```bash
pytest tests/test_sd_login_steps.py --setup-show -v
```

Output:
```
SETUP    S browser_context_args
SETUP    S browser
SETUP    F context
SETUP    F page
    test_successful_login_with_valid_credentials
        SETUP    F login_page (via target_fixture in @given)
        TEARDOWN F login_page
TEARDOWN F page
TEARDOWN F context
TEARDOWN S browser
TEARDOWN S browser_context_args
```

`S` = session scope. `F` = function scope. This shows you the exact order and lifetime.

---

## What's Next

- [06 — conftest.py Strategy](./06_conftest_strategy.md) — where to put fixtures as your project grows
