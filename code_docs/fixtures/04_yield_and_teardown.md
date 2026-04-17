# Fixtures 04 — Yield and Teardown

> **Goal:** Understand how to write fixtures that clean up after themselves, why teardown is critical in browser testing, and patterns for reliable cleanup even when tests fail.

---

## The Problem — Tests That Leave a Mess

Without teardown:

```python
@pytest.fixture
def page(context):
    return context.new_page()    # no cleanup

# After 100 tests: 100 open browser tabs consuming memory
# After a test failure: DB records left behind, polluting the next test
# After a session: leaked processes, ports still bound
```

This causes:
- Flaky tests (state from test A bleeds into test B)
- Resource exhaustion (too many browser processes)
- Ports already in use on the next run

---

## `yield` — The Setup/Teardown Boundary

`yield` splits a fixture into two parts:

```python
@pytest.fixture
def page(context):
    p = context.new_page()    # ← SETUP: runs before the test
    yield p                   # ← TEST RUNS HERE, receives `p`
    p.close()                 # ← TEARDOWN: runs after the test
```

Think of it like this:

```
fixture setup
    ↓
yield value_to_test
    ↓
test runs (receives value_to_test)
    ↓
fixture teardown (everything after yield)
```

The value after `yield` is what the test receives. It's equivalent to `return` but with the added teardown phase.

---

## Teardown Runs Even When Tests Fail

This is the key guarantee. pytest runs teardown even if:
- The test raises an `AssertionError`
- The test raises an unexpected exception
- A previous test in the session failed

```python
@pytest.fixture
def db_record(db):
    record = db.insert({"name": "test_user"})
    yield record
    db.delete(record.id)     # ← runs even if the test crashes
```

Equivalent to:

```python
record = db.insert({"name": "test_user"})
try:
    yield record             # test runs here
finally:
    db.delete(record.id)    # guaranteed cleanup
```

pytest translates the `yield` fixture into this `try/finally` pattern internally.

---

## What if Teardown Itself Fails?

If the teardown code raises an exception, pytest reports it as an additional `ERROR` (separate from the test result), and continues running other tests. It does not swallow the error silently.

```python
@pytest.fixture
def page(context):
    p = context.new_page()
    yield p
    p.close()               # if this raises, pytest reports: ERROR in teardown
```

Best practice — protect teardown:

```python
@pytest.fixture
def page(context):
    p = context.new_page()
    yield p
    try:
        p.close()
    except Exception:
        pass                # teardown failures in browsers are often harmless
```

Only suppress teardown errors when you're certain they're safe to ignore (e.g. the browser already closed itself due to a crash).

---

## Multiple Resources — Order of Teardown

When a test uses multiple fixtures, teardown runs in **reverse order of setup**:

```python
@pytest.fixture
def browser():
    b = launch()
    yield b
    b.close()               # torn down LAST

@pytest.fixture
def context(browser):
    ctx = browser.new_context()
    yield ctx
    ctx.close()             # torn down SECOND

@pytest.fixture
def page(context):
    p = context.new_page()
    yield p
    p.close()               # torn down FIRST
```

Setup order: `browser → context → page`
Teardown order: `page → context → browser`

This is correct — you can't close the browser before closing its pages. pytest handles this automatically because it reverses the dependency chain.

---

## Patterns for Common Cleanup Tasks

### Browser page

```python
@pytest.fixture
def page(context):
    p = context.new_page()
    yield p
    p.close()
```

### Database record

```python
@pytest.fixture
def test_user(db):
    user = db.create_user({"email": "test@example.com", "role": "tester"})
    yield user
    db.delete_user(user.id)     # always cleaned up
```

### Temporary file

```python
@pytest.fixture
def temp_config(tmp_path):      # tmp_path is a built-in pytest fixture
    config_file = tmp_path / "config.json"
    config_file.write_text('{"env": "test"}')
    yield config_file
    # no teardown needed — tmp_path auto-deletes after session
```

### API resource

```python
@pytest.fixture
def created_product(api_client):
    product = api_client.create_product({"name": "Test Item", "price": 9.99})
    yield product
    api_client.delete_product(product["id"])
```

### Running test server

```python
@pytest.fixture(scope="session")
def test_server():
    server = MyTestServer(port=8080)
    server.start()
    yield server
    server.stop()
```

---

## `addfinalizer` — The Alternative to `yield`

Before `yield` was available, pytest used `request.addfinalizer()`. You'll see this in older codebases.

```python
@pytest.fixture
def page(context, request):
    p = context.new_page()
    request.addfinalizer(p.close)    # registers cleanup function
    return p                         # note: return, not yield
```

**When `addfinalizer` is still useful:**

When you need to register cleanup **conditionally** or in a loop:

```python
@pytest.fixture
def multi_page(context, request):
    pages = []
    for _ in range(3):
        p = context.new_page()
        pages.append(p)
        request.addfinalizer(p.close)   # each page gets its own finalizer
    return pages
```

With `yield` you'd need a try/finally loop. `addfinalizer` is cleaner here.

**Rule:** Prefer `yield` for simple single-resource fixtures. Use `addfinalizer` when you need conditional or loop-based cleanup registration.

---

## Teardown and Scope — When Does it Actually Run?

Teardown runs when the fixture's **scope** ends, not just when the test ends.

```python
@pytest.fixture(scope="session")
def browser():
    b = launch()
    yield b
    b.close()       # runs when ALL tests finish, not after each test
```

```python
@pytest.fixture(scope="module")
def db_connection():
    conn = connect()
    yield conn
    conn.close()    # runs when all tests in the file finish
```

```python
@pytest.fixture                 # function scope
def page(context):
    p = context.new_page()
    yield p
    p.close()       # runs immediately after each test
```

Timeline for a 3-test run:

```
session scope setup    ─────────────────────────────────────────── session scope teardown
  module scope setup   ──────────────────────── module scope teardown
    function scope setup ─ test1 ─ function scope teardown
    function scope setup ─ test2 ─ function scope teardown
    function scope setup ─ test3 ─ function scope teardown
```

---

## Real Teardown That Matters — Screenshots on Failure

A common pattern in browser testing: capture a screenshot when a test fails.

```python
@pytest.fixture
def page(context):
    p = context.new_page()
    yield p
    # check if the test failed
    if hasattr(p, '_test_failed') and p._test_failed:
        p.screenshot(path=f"reports/failure_{p.url.split('/')[-1]}.png")
    p.close()
```

Or the cleaner approach using pytest's `request` fixture:

```python
@pytest.fixture
def page(context, request):
    p = context.new_page()
    yield p
    if request.node.rep_call.failed:    # True if the test failed
        p.screenshot(path=f"reports/{request.node.name}.png")
    p.close()
```

Now every test failure automatically saves a screenshot. Zero changes to test files.

---

## What's Next

- [05 — Fixture Chaining](./05_fixture_chaining.md) — how fixtures build on each other to create powerful pipelines
