# 01 — pytest Basics

> **Goal:** Understand what pytest is, how it finds and runs tests, and the core vocabulary you will use every day.

---

## What is pytest?

pytest is a Python testing framework. You write plain Python functions, decorate or name them in a way pytest recognizes, run one command, and pytest does the rest — discovers tests, runs them, reports results.

It replaces writing `if result == expected: print("PASS")` by hand.

---

## How pytest Finds Tests (Test Discovery)

pytest follows these rules automatically when you run `pytest`:

| Rule | Example |
|------|---------|
| Files named `test_*.py` or `*_test.py` | `test_sd_login_steps.py` ✓ |
| Functions named `test_*` inside those files | `def test_login():` ✓ |
| Classes named `Test*` (no `__init__`) | `class TestLogin:` ✓ |

You can also point pytest at a specific file or test:
```bash
pytest tests/test_sd_login_steps.py                          # whole file
pytest tests/test_sd_login_steps.py::test_successful_login   # one test
pytest -k "login"                                            # any test whose name contains "login"
```

---

## The Simplest Possible Test

```python
# test_math.py
def test_addition():
    assert 1 + 1 == 2          # passes

def test_subtraction():
    assert 10 - 3 == 8         # fails — pytest shows exactly what was wrong
```

`assert` is plain Python. pytest rewrites it internally to produce a detailed failure message showing the actual vs expected values.

---

## Key CLI Flags You Will Use Daily

```bash
pytest                          # run all tests
pytest -v                       # verbose — show each test name
pytest -s                       # show print() output (don't capture stdout)
pytest -v -s                    # both
pytest --headed                 # playwright: open browser window during tests
pytest -k "login and not error" # run tests matching expression
pytest --tb=short               # shorter traceback on failure
pytest -x                       # stop after first failure
pytest --lf                     # re-run only tests that failed last time
```

---

## Assertions — What to Use

pytest uses plain `assert`. You don't need special assertion methods like JUnit's `assertEquals`.

```python
assert result == expected          # equality
assert result != expected          # not equal
assert result is None              # identity check
assert "Products" in page_title    # substring
assert len(items) == 5             # length
assert price > 0                   # comparison
```

When an assertion fails, pytest shows:
```
AssertionError: assert 'Sauce Labs' == 'Products'
  - Sauce Labs
  + Products
```

---

## Test Outcomes

| Outcome | Meaning |
|---------|---------|
| `PASSED` | assertion succeeded |
| `FAILED` | assertion failed, or an exception was raised |
| `ERROR` | something broke in setup/teardown (fixture problem), not in the test itself |
| `SKIPPED` | test was skipped with `@pytest.mark.skip` |
| `XFAIL` | test was expected to fail and did (`@pytest.mark.xfail`) |

---

## Marks — Tagging Tests

Marks let you group and filter tests without touching filenames.

```python
import pytest

@pytest.mark.smoke
def test_login():
    ...

@pytest.mark.regression
def test_error_message():
    ...
```

Run only smoke tests:
```bash
pytest -m smoke
```

In this project the marks come from the `.feature` file tags (`@smoke`, `@regression`). pytest-bdd converts those into pytest marks automatically.

---

## pyproject.toml — Project Configuration

pytest reads settings from `pyproject.toml`. In this project:

```toml
[tool.pytest.ini_options]
bdd_features_base_dir = "tests/"   # where .feature files live
markers = ["smoke", "regression"]  # register custom marks
```

This is where you control test discovery paths, default options, and plugin settings — one config file for the whole project.

---

## Vocabulary Cheatsheet

| Term | Meaning |
|------|---------|
| **Test** | A function that verifies one behaviour |
| **Suite** | A collection of tests (a file, a folder) |
| **Assertion** | The check — `assert x == y` |
| **Mark** | A tag on a test (`@pytest.mark.smoke`) |
| **Fixture** | Shared setup/teardown — covered in doc 02 |
| **conftest.py** | Special file pytest loads automatically for fixtures and hooks |
| **Plugin** | An extension to pytest (`pytest-bdd`, `pytest-playwright`) |

---

## What's Next

Doc 02 covers **fixtures** — how pytest shares setup (like a browser page, a logged-in user, a database connection) across tests without repeating code.
