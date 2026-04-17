# 03 — pytest-bdd: BDD, Gherkin & Step Definitions

> **Goal:** Understand Behaviour-Driven Development, how Gherkin feature files work, how step definitions connect to them, and how this project is structured to scale.

---

## What is BDD?

BDD (Behaviour-Driven Development) is a practice where you write test scenarios in plain English **before** writing code. The plain English is readable by developers, testers, and non-technical stakeholders (product managers, QA leads).

The idea: **describe behaviour, not implementation.**

```
# Implementation-focused (bad for communication)
"Call login() with username='standard_user', assert HTTP 200"

# Behaviour-focused (everyone understands)
"Given I am on the login page
 When I log in with valid credentials
 Then I should see the products page"
```

pytest-bdd is the bridge: it connects plain-English scenarios to Python functions.

---

## Gherkin — The Language of Feature Files

Gherkin is the structured English syntax BDD uses. Files end in `.feature`.

```gherkin
Feature: SauceDemo User Authentication        ← what capability this file covers
  As a SauceDemo user                         ← who benefits
  I want to authenticate                      ← what they want
  So that I can access the product catalog    ← why (the business value)

  Background:                                 ← runs before EVERY scenario in this file
    Given the user is on the SauceDemo login page

  @smoke                                      ← tag (becomes a pytest mark)
  Scenario: Successful login with valid credentials
    When the user logs in with username "standard_user" and password "secret_sauce"
    Then the user should land on the products page
```

### The Five Keywords

| Keyword | Purpose |
|---------|---------|
| `Given` | Precondition — system state before the action |
| `When` | Action — the thing the user does |
| `Then` | Outcome — what should be true after the action |
| `And` / `But` | Continue the previous step type (avoids repetition) |
| `Background` | Steps that run before every scenario in the file |

`And`/`But` are aliases — they take the type of the step above them:
```gherkin
Given I am logged in
And my cart is empty      ← this is also a "Given"
When I add an item
And I go to checkout      ← this is also a "When"
Then I see 1 item
But I don't see 2 items   ← this is also a "Then"
```

---

## Step Definitions — Connecting Gherkin to Python

A step definition is a Python function decorated with `@given`, `@when`, or `@then`. The string in the decorator must match the feature file step text exactly.

```gherkin
# sd_login.feature
When the user logs in with username "standard_user" and password "secret_sauce"
```

```python
# conftest.py
from pytest_bdd import when

@when('the user logs in with username "standard_user" and password "secret_sauce"')
def login(login_page):
    login_page.login("standard_user", "secret_sauce")
```

But hardcoding the values is useless — you can't reuse the step. This is where **parsers** come in.

---

## Parsers — Extracting Values from Step Text

pytest-bdd has three parsers for capturing dynamic values from step text.

### 1. `parsers.parse` — Simple `{variable}` syntax

```python
from pytest_bdd import when, parsers

@when(parsers.parse('the user logs in with username "{username}" and password "{password}"'))
def login(login_page, username, password):
    login_page.login(username, password)
```

The `{username}` and `{password}` placeholders are captured and passed as function parameters automatically. Uses the `parse` library — simple, readable, good for most cases.

### 2. `parsers.re` — Full regex, named groups

```python
from pytest_bdd import when, parsers

@when(parsers.re(r'the user logs in with username "(?P<username>[^"]*)" and password "(?P<password>[^"]*)"'))
def login(login_page, username: str, password: str):
    login_page.login(username, password)
```

`(?P<username>[^"]*)` — named capture group. The name (`username`) becomes the parameter name.

Use regex when:
- You need more control over what the pattern matches
- The step text has special characters `parse` can't handle
- You want to validate format (e.g., only digits: `(?P<count>\d+)`)

### 3. `parsers.cfparse` — Typed parsing

```python
@when(parsers.cfparse('there are {count:d} items'))
def check_items(count: int):   # :d means integer — count is already an int
    assert count > 0
```

Use when you want automatic type conversion (`:d` for int, `:f` for float).

**Rule of thumb:**
- Simple strings → `parsers.parse`
- Need type conversion → `parsers.cfparse`
- Complex patterns or validation → `parsers.re`

---

## `scenarios()` — Linking a Test File to a Feature File

```python
from pytest_bdd import scenarios

scenarios("sd_login.feature")   # links ALL scenarios in this .feature file
```

This one line tells pytest-bdd: *"generate a test function for each scenario in `sd_login.feature`."* Without it, pytest wouldn't know which feature file belongs to which step file.

The path is relative to `bdd_features_base_dir` set in `pyproject.toml`.

---

## Background — Setup for Every Scenario

```gherkin
Background:
  Given the user is on the SauceDemo login page
```

`Background` runs before every scenario in the file — same as a `@pytest.fixture(autouse=True)` but written in Gherkin. Keeps scenarios DRY (Don't Repeat Yourself).

Use it for: navigating to a page, seeding test data, setting up a precondition every scenario shares.

---

## Tags — Filtering and Marking Tests

Tags in Gherkin (`@smoke`, `@regression`) become pytest marks automatically.

```gherkin
@smoke
Scenario: Successful login with valid credentials
```

Run only smoke tests:
```bash
pytest -m smoke
```

Run everything except regression:
```bash
pytest -m "not regression"
```

Tag at any level:
```gherkin
@sauce @login          ← Feature-level: applies to ALL scenarios
Feature: SauceDemo Authentication

  @smoke               ← Scenario-level: applies to this one scenario
  Scenario: Successful login
```

---

## Scenario Outline — Data-Driven Tests

When the same scenario needs to run with multiple data sets, use `Scenario Outline` + `Examples`:

```gherkin
Scenario Outline: Login failure — <scenario>
  When the user logs in with username "<username>" and password "<password>"
  Then the login error message should be displayed

  Examples: Invalid credential combinations
    | scenario          | username      | password      |
    | invalid username  | wrong_user    | secret_sauce  |
    | invalid password  | standard_user | wrong_pass    |
```

Each row in `Examples` generates a separate test. pytest-bdd names them automatically. This replaces writing two identical scenarios that differ only in data.

---

## The Full Architecture of This Project

```
tests/sd_login.feature          ← Plain English scenarios (readable by everyone)
        ↓ matched by
tests/test_sd_login_steps.py    ← @given, @then step definitions (SauceDemo-specific)
tests/conftest.py               ← @when step (shared across features)
        ↓ use
pages/sd_login_page.py          ← Page Object (browser actions, locators)
pages/sd_product_page.py        ← Page Object (product page assertions)
pages/base_page.py              ← Shared page behaviour (navigate, get_title)
```

### Execution Flow for "Successful Login"

```
1. pytest discovers test_sd_login_steps.py
2. scenarios("sd_login.feature") → generates test_successful_login_with_valid_credentials
3. Background runs:
   @given "the user is on the SauceDemo login page"
   → creates SauceLoginPage, navigates, registers as fixture "login_page"
4. @when "the user logs in with username ... and password ..."
   → conftest.py receives "login_page" fixture + parsed username/password
   → calls login_page.login("standard_user", "secret_sauce")
5. @then "the user should land on the products page"
   → creates SauceProductPage, asserts ".title" has text "Products"
```

---

## conftest.py Strategy for Large Projects

As your project grows, you'll have many features sharing steps. The rule:

| Where to put the step | Why |
|-----------------------|-----|
| `conftest.py` | Step text is **identical** across multiple features |
| `test_feature_steps.py` | Step is **specific** to one feature |

```
conftest.py
  @when "the user logs in with username ... and password ..."   ← used by SD AND PTA

test_sd_login_steps.py
  @given "the user is on the SauceDemo login page"             ← SD only
  @then  "the user should land on the products page"           ← SD only

test_pta_login_steps.py
  @given "the user is on the PTA login page"                   ← PTA only
  @then  "the dashboard should be visible"                     ← PTA only
```

The `@when` login step works for both because `target_fixture` makes `login_page` a fixture — the step doesn't care whether `login_page` is a `SauceLoginPage` or `PtaLoginPage`. It just calls `.login()`. This is **duck typing** at the architecture level.

---

## Industry Standards for BDD at Scale

**1. One feature file per user-facing capability** (not per page, not per class)
```
auth.feature        ← login, logout, password reset
checkout.feature    ← add to cart, place order, payment
profile.feature     ← edit profile, change password
```

**2. Step text describes user intent, not implementation**
```gherkin
# Bad — implementation detail
When the POST /api/login endpoint is called with body {"user": "x"}

# Good — user behaviour
When the user logs in with username "x" and password "y"
```

**3. Keep scenarios short** — 3 to 7 steps. If longer, split into smaller scenarios or extract Background.

**4. No logic in step definitions** — step definitions orchestrate, page objects act.
```python
# Bad — logic in the step
@when("login fails")
def login_fails(page):
    page.locator("#user").fill("wrong")
    page.locator("#pass").fill("wrong")
    page.locator("#btn").click()

# Good — step delegates to page object
@when("login fails")
def login_fails(login_page):
    login_page.login_with_invalid_credentials()
```

**5. Use `target_fixture` instead of global state** — never `global login_page` in a step file.

---

## Vocabulary Cheatsheet

| Term | Meaning |
|------|---------|
| **BDD** | Write scenarios in plain English before code |
| **Gherkin** | The structured English syntax (Given/When/Then) |
| **Feature file** | `.feature` file containing scenarios |
| **Step definition** | Python function decorated with `@given`/`@when`/`@then` |
| **Parser** | Extracts variables from step text (`parse`, `re`, `cfparse`) |
| **scenarios()** | Links a test file to a feature file |
| **Background** | Steps that run before every scenario in a file |
| **Scenario Outline** | One scenario template run with multiple data rows |
| **target_fixture** | Promotes a step's return value into a named fixture |
| **Tag** | `@smoke` in Gherkin → `pytest.mark.smoke` |

---

## What's Next

Doc 04 will cover **Page Object Model (POM)** — how to structure `pages/` for large projects, base page patterns, and how Playwright locators work inside page objects.
