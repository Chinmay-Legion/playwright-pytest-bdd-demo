# Fixtures 06 — conftest.py Strategy for Large Projects

> **Goal:** Understand how to organise conftest.py files as a project grows, what belongs at each level, and how to avoid the common mistake of putting everything in one file.

---

## What conftest.py Is

`conftest.py` is a special file pytest loads automatically before running tests. It has three purposes:

1. **Fixtures** — shared setup/teardown for tests in the same folder (and subfolders)
2. **Hooks** — pytest lifecycle callbacks (e.g. `pytest_html_report_title`)
3. **Plugins** — registering local pytest plugins

You do not import from `conftest.py`. pytest discovers it automatically by filename.

---

## The Search Order — How pytest Finds Fixtures

When a test requests a fixture named `login_page`, pytest searches:

```
1. The test file itself
2. conftest.py in the same directory as the test file
3. conftest.py in the parent directory
4. conftest.py in the grandparent directory
... (keeps going up to the rootdir)
5. Built-in pytest fixtures
6. Plugin-provided fixtures (pytest-playwright, etc.)
```

The **first match wins**. This means inner conftest.py files can **override** fixtures defined in outer ones — intentionally.

---

## Single conftest — Fine for Small Projects

When you have one test folder and under 20 tests, one conftest.py is fine:

```
playwright-demo/
  tests/
    conftest.py       ← everything here
    test_sd_login_steps.py
    test_pta_login_steps.py
  pages/
  pyproject.toml
```

This is where this project is now. It works. It starts to hurt when:
- The conftest grows beyond ~100 lines
- You add features that have nothing to do with each other
- Different test files need different browser configurations

---

## Multi-Level conftest — The Scalable Pattern

As the project grows, split conftest.py files by responsibility:

```
playwright-demo/
  conftest.py                    ← Level 0: project-wide (env, reporting)
  tests/
    conftest.py                  ← Level 1: all tests (browser, page, base_url)
    auth/
      conftest.py                ← Level 2: auth-specific (logged-in fixtures)
      test_login.py
      test_logout.py
      test_password_reset.py
    shop/
      conftest.py                ← Level 2: shop-specific (cart, product fixtures)
      test_products.py
      test_cart.py
      test_checkout.py
    admin/
      conftest.py                ← Level 2: admin-specific (admin login, user management)
      test_user_management.py
      test_reports.py
```

---

## What Goes at Each Level

### Level 0 — Root conftest.py (project-wide)

Things that apply to every test, regardless of feature:

```python
# conftest.py (project root)
import pytest

def pytest_html_report_title(report):
    report.title = "My App — Test Report"

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: fast sanity checks")
    config.addinivalue_line("markers", "regression: full coverage suite")

@pytest.fixture(scope="session")
def env():
    return os.getenv("TEST_ENV", "staging")   # "staging" or "production"
```

### Level 1 — tests/conftest.py (all browser tests)

Browser infrastructure that every test needs:

```python
# tests/conftest.py
import pytest
from playwright.sync_api import BrowserContext

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {**browser_context_args, "viewport": {"width": 1920, "height": 1080}}

@pytest.fixture(scope="session")
def base_url(env):
    urls = {
        "staging":    "https://staging.saucedemo.com",
        "production": "https://www.saucedemo.com",
    }
    return urls[env]

# Shared @when step — used by BOTH auth and shop features
@when(parsers.re(r'the user logs in with username "(?P<username>[^"]*)" ...'))
def login_with_credentials(login_page, username, password):
    login_page.login(username, password)
```

### Level 2 — tests/auth/conftest.py (auth feature only)

Fixtures only the auth tests need:

```python
# tests/auth/conftest.py
import pytest
from pages.sd_login_page import SauceLoginPage
from pages.sd_product_page import SauceProductPage

@pytest.fixture
def login_page(page, base_url):
    page.goto(base_url)
    return SauceLoginPage(page)

@pytest.fixture
def authenticated_inventory(login_page):
    login_page.login("standard_user", "secret_sauce")
    return SauceProductPage(login_page.page)
```

These fixtures are invisible to `tests/shop/` — they don't pollute the shop tests' fixture namespace.

### Level 2 — tests/shop/conftest.py (shop feature only)

```python
# tests/shop/conftest.py
import pytest

@pytest.fixture
def product_catalog(authenticated_inventory):
    # authenticated_inventory comes from shop's own conftest (or level 1)
    return authenticated_inventory.get_all_products()

@pytest.fixture
def cart(authenticated_inventory):
    cart = authenticated_inventory.open_cart()
    yield cart
    cart.clear()   # teardown: empty cart between tests
```

---

## Fixture Override — Environment-Specific Configuration

The search order (inner conftest wins) lets you override fixtures per folder:

```
tests/
  conftest.py           ← base_url = staging URL
  production_smoke/
    conftest.py         ← base_url = production URL  (override)
    test_smoke.py       ← uses production URL
  test_full_suite.py    ← uses staging URL
```

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def base_url():
    return "https://staging.saucedemo.com/v1/"

# tests/production_smoke/conftest.py
@pytest.fixture(scope="session")
def base_url():                                # same name — overrides for this folder
    return "https://www.saucedemo.com/v1/"
```

Every fixture in the chain (`login_page`, `page`, etc.) automatically uses the right URL for its folder. No test file changes.

---

## What Belongs in conftest.py vs the Test File

| Belongs in conftest.py | Belongs in the test file |
|------------------------|--------------------------|
| Fixtures used by 2+ test files | Fixtures used only in that file |
| Shared step definitions (`@when` used by multiple features) | Step definitions specific to one feature |
| Browser/page infrastructure | Test-specific page object instantiation |
| Environment config | Test data for a specific scenario |
| Hooks (report title, markers) | Nothing hook-related |

In this project:

```python
# conftest.py — correctly placed (shared across SD and PTA features)
@when(parsers.re(r'the user logs in with username "(?P<username>[^"]*)" ...'))
def login_with_credentials(login_page, username, password): ...

# test_sd_login_steps.py — correctly placed (SD-specific)
@given("the user is on the SauceDemo login page", target_fixture="login_page")
def navigate_to_sd_login(page): ...
```

---

## The Growing Pains Pattern — How Projects Actually Evolve

**Phase 1: 1-5 tests**
```
tests/conftest.py    ← everything, fine
```

**Phase 2: 10-30 tests, 2-3 features**
```
tests/conftest.py    ← browser setup, shared steps
tests/test_auth.py   ← auth-specific @given/@then
tests/test_shop.py   ← shop-specific @given/@then
```

**Phase 3: 50+ tests, 5+ features, multiple environments**
```
conftest.py                   ← env config, report hooks
tests/conftest.py             ← browser, base_url, shared steps
tests/auth/conftest.py        ← auth fixtures
tests/auth/test_login.py
tests/shop/conftest.py        ← shop fixtures
tests/shop/test_products.py
tests/api/conftest.py         ← API client fixtures (no browser)
tests/api/test_endpoints.py
```

**Phase 4: Multiple environments, CI/CD pipeline**
```
conftest.py
tests/conftest.py
tests/auth/conftest.py
tests/staging/conftest.py     ← staging-specific overrides
tests/production/conftest.py  ← production-specific overrides (smoke only)
```

You never rewrite your test files — you add conftest.py files and override fixtures.

---

## Signs Your conftest.py Needs to Be Split

- It's longer than 150 lines
- It has imports for page objects from 3+ different features
- You scroll past auth fixtures to find shop fixtures
- New team members have trouble finding the fixture they need
- Adding a fixture for feature A accidentally breaks feature B

---

## Industry Standard Layout for Large Projects

```
project/
  conftest.py                    ← pytest hooks, env fixtures, markers
  pyproject.toml                 ← pytest config, base dirs, addopts
  pages/                         ← page objects (no fixtures here)
    base_page.py
    auth/
      login_page.py
      register_page.py
    shop/
      inventory_page.py
      cart_page.py
  tests/
    conftest.py                  ← browser setup, shared @when steps
    auth/
      __init__.py
      conftest.py                ← login_page, authenticated_page fixtures
      sd_login.feature
      test_sd_login_steps.py
    shop/
      __init__.py
      conftest.py                ← inventory_page, cart_page fixtures
      sd_shop.feature
      test_sd_shop_steps.py
    api/
      __init__.py
      conftest.py                ← api_client fixture (no browser)
      test_product_api.py
```

The `pages/` folder mirrors the `tests/` folder structure. When you look for the page object for auth tests, you look in `pages/auth/`. When you look for auth test fixtures, you look in `tests/auth/conftest.py`. Consistent, predictable, scalable.

---

## Summary — The Three Rules

1. **Put fixtures where they're first needed** — if only `test_auth.py` uses it, it goes in `tests/auth/conftest.py`, not the root
2. **Override at the folder level** — environment differences belong in folder-level conftest overrides, not in test files
3. **Never import from conftest.py** — pytest loads it automatically; if you're importing from it, something is wrong with your structure
