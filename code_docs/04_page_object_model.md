# 04 — Page Object Model (POM)

> **Goal:** Understand what the Page Object Model is, why it exists, how Playwright locators work inside page objects, and how to structure `pages/` for large projects.

---

## The Problem POM Solves

Without POM, browser interactions live directly in test files:

```python
def test_valid_login(page):
    page.goto("https://www.saucedemo.com/v1/")
    page.locator("#user-name").fill("standard_user")
    page.locator("#password").fill("secret_sauce")
    page.locator("#login-button").click()
    expect(page.locator(".title")).to_have_text("Products")

def test_invalid_login(page):
    page.goto("https://www.saucedemo.com/v1/")
    page.locator("#user-name").fill("wrong_user")     # duplicated
    page.locator("#password").fill("wrong_pass")      # duplicated
    page.locator("#login-button").click()             # duplicated
    expect(page.locator(".error-button")).to_be_visible()
```

Now the site changes `#login-button` to `#btn-login`. You grep for `#login-button` and fix it in 20 test files. One missed → flaky test in production.

**POM moves locators and interactions into a class.** Tests call methods. Only the class knows the selectors.

---

## What a Page Object Is

A page object is a Python class that represents one page (or a component of a page) in the application. It:

1. **Stores locators** — what elements are on the page
2. **Exposes actions** — what a user can do on the page (`login()`, `add_to_cart()`)
3. **Exposes assertions** — what the page should look like (`assert_on_products_page()`)
4. **Knows nothing about test logic** — no `assert` based on test conditions, no test data

```python
# pages/sd_login_page.py
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

_URL = "https://www.saucedemo.com/v1/"

class SauceLoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input = page.locator("#user-name")
        self.password_input = page.locator("#password")
        self.login_btn      = page.locator("#login-button")
        self.error_container = page.locator(".error-button")

    def navigate(self) -> None:
        super().navigate(_URL)

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()

    def assert_error_visible(self) -> None:
        expect(self.error_container).to_be_visible()
```

Now if `#login-button` changes → fix it in one place. All 20 tests still pass.

---

## Playwright Locators — How They Work

A locator is a **lazy reference** to a DOM element. It does not find the element when you create it — it finds (and re-finds) the element each time you interact with it.

```python
self.login_btn = page.locator("#login-button")   # no browser interaction yet

self.login_btn.click()    # NOW it searches the DOM and clicks
self.login_btn.click()    # searches DOM again (element may have re-rendered)
```

This is important: locators handle dynamic pages where elements re-render after interactions.

### Locator Types

```python
# CSS selector (most common)
page.locator("#login-button")          # by ID
page.locator(".error-button")          # by class
page.locator("input[type='submit']")   # by attribute
page.locator(".inventory_item:first-child")  # CSS pseudo-selectors

# Text content
page.get_by_text("Add to cart")        # exact text match
page.get_by_text("Add", exact=False)   # partial match

# Role (semantic — preferred for accessibility)
page.get_by_role("button", name="Login")
page.get_by_role("textbox", name="Username")

# Label (form fields)
page.get_by_label("Password")

# Placeholder
page.get_by_placeholder("Enter username")

# Test ID (explicit — most stable)
page.get_by_test_id("login-button")    # matches data-testid="login-button"
```

### Locator Priority (Industry Standard)

Use locators in this order — most stable first:

```
1. get_by_test_id()     ← explicit, survives CSS/text changes, needs dev cooperation
2. get_by_role()        ← semantic, accessible, stable
3. get_by_label()       ← good for forms
4. get_by_text()        ← fragile to copy changes
5. CSS by ID (#id)      ← stable if IDs are maintained
6. CSS by class (.cls)  ← fragile — classes change for styling reasons
```

In this project, `#user-name`, `#password`, `#login-button` are IDs — stable for this app. `.product_label` was a class that changed (why the test broke earlier).

---

## BasePage — Shared Behaviour

```python
# pages/base_page.py
from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, url: str) -> None:
        self.page.goto(url)

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url
```

Every page object inherits from `BasePage`. This gives you:
- A shared `self.page` reference
- Common actions (`navigate`, `get_title`, `get_url`) in one place
- A consistent interface — any page object can do these things

When you add something all pages need (e.g. `wait_for_network_idle()`), add it to `BasePage` once.

---

## Inheritance vs Composition

**Inheritance (current pattern):**
```python
class SauceLoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)    # gets self.page
        self.username = page.locator("#user-name")
```

Good when: all pages share behaviour. Simple hierarchy. Works well here.

**Composition (for large projects with shared components):**
```python
class NavBar:
    def __init__(self, page):
        self.cart_icon = page.locator(".shopping_cart_link")
        self.menu_btn  = page.locator("#react-burger-menu-btn")

    def open_cart(self):
        self.cart_icon.click()

class InventoryPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.nav = NavBar(page)          # composed, not inherited
        self.items = page.locator(".inventory_item")

    def go_to_cart(self):
        self.nav.open_cart()             # delegates to the component
```

Use composition when: multiple pages share a component (navbar, sidebar, modal). The component becomes its own class — not duplicated in every page.

---

## Page Object Rules — What Goes In, What Stays Out

**IN the page object:**
- Locators (`self.login_btn = page.locator(...)`)
- User actions (`def login(self, username, password)`)
- Assertions about this page (`def assert_error_visible()`)
- Navigation to the page (`def navigate()`)
- Waiting logic specific to this page

**OUT of the page object:**
- Test data (`"standard_user"` — that belongs in the test or fixtures)
- Control flow (`if logged_in: ... else: ...`)
- Cross-page orchestration (a login page shouldn't know about the inventory page)
- pytest assertions or `expect()` calls based on test conditions

```python
# BAD — page object knows about test conditions
def login_and_verify(self, username, password, should_succeed):
    self.login(username, password)
    if should_succeed:
        expect(self.page.locator(".title")).to_have_text("Products")
    else:
        expect(self.error_container).to_be_visible()

# GOOD — page object does one thing, test decides what to assert
def login(self, username, password):
    self.username_input.fill(username)
    self.password_input.fill(password)
    self.login_btn.click()

def assert_error_visible(self):
    expect(self.error_container).to_be_visible()

def assert_on_products_page(self):
    expect(self.page.locator(".title")).to_have_text("Products")
```

---

## Returning Page Objects from Actions

When an action navigates to a new page, the method should return the new page object:

```python
class SauceLoginPage(BasePage):
    def login(self, username: str, password: str) -> "InventoryPage":
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()
        return InventoryPage(self.page)   # tells the caller: you're now here
```

```python
# In test
inventory = login_page.login("standard_user", "secret_sauce")
inventory.assert_on_products_page()
```

This makes the **navigation flow explicit** in the test. The test reads like the user journey.

For this project's BDD approach, step definitions handle the transition:

```python
@given("...", target_fixture="login_page")
def navigate(page): return SauceLoginPage(page)

@then("the user should land on the products page")
def verify(page):
    SauceProductPage(page).assert_on_products_page()
```

Both approaches are valid — the BDD way keeps page object construction in step definitions.

---

## Folder Structure for Large Projects

Mirror your app's navigation structure:

```
pages/
  base_page.py              ← shared base class
  components/
    nav_bar.py              ← shared navbar component
    modal.py                ← shared modal component
    pagination.py           ← shared pagination component
  auth/
    login_page.py
    register_page.py
    forgot_password_page.py
  shop/
    inventory_page.py
    product_detail_page.py
    cart_page.py
    checkout_page.py
  admin/
    dashboard_page.py
    user_management_page.py
```

```
tests/
  auth/
    sd_login.feature
    test_sd_login_steps.py  ← imports from pages/auth/
  shop/
    sd_shop.feature
    test_sd_shop_steps.py   ← imports from pages/shop/
```

The folder name in `pages/` matches the folder name in `tests/`. When you open a test file, you know exactly where to find its page objects.

---

## `expect()` — Playwright Assertions in Page Objects

Playwright's `expect()` is different from pytest's `assert`. It:
- Automatically **retries** for up to 5 seconds (configurable) — handles slow rendering
- Has **readable failure messages** built in
- Works on locators, not values

```python
from playwright.sync_api import expect

# Retry for up to 5s until the condition is true
expect(self.product_label).to_have_text("Products")
expect(self.error_container).to_be_visible()
expect(self.login_btn).to_be_enabled()
expect(self.page).to_have_url("https://www.saucedemo.com/inventory.html")
expect(self.items).to_have_count(6)
```

If the condition isn't met within the timeout:
```
AssertionError: Locator expected to have text 'Products'
Actual value: None
Error: element(s) not found
```

**Rule:** Use `expect()` for all browser assertions in page objects. Use plain `assert` for non-browser assertions (data, values, counts of Python lists).

---

## What's Next

Doc 05 will cover **Playwright deep dive** — how the browser/context/page model works, how to handle waits, intercept network requests, and deal with dynamic content.
