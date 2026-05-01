# Playwright Pytest BDD Demo

This is a small learning project for practicing browser automation with:

- Playwright for browser automation
- pytest as the test runner
- pytest-bdd for Gherkin-style BDD scenarios
- allure-pytest-bdd for Allure reporting
- pytest-html for a simple standalone HTML report
- pytest-playwright for traces, videos, screenshots, and browser fixtures

The goal is not to build a large automation framework. The goal is to keep everything basic, readable, and easy to experiment with.

## Demo Sites

This project uses two small public demo websites:

- SauceDemo: https://www.saucedemo.com/
- Practice Test Automation: https://practicetestautomation.com/practice-test-login/

These sites are intentionally simple, which makes them good for learning selectors, page objects, fixtures, pytest markers, pytest-bdd step definitions, and reporting.

## Project Structure

```text
pages/
  base_page.py
  sd_login_page.py
  sd_product_page.py
  pta_login_page.py
  pta_successful_page.py

tests/
  conftest.py
  features/
    saucedemo_login.feature
    practice_test_automation_login.feature
    parser_examples.feature
  steps/
    test_saucedemo_login_steps.py
    test_practice_test_automation_login_steps.py
    test_parser_example_steps.py

reports/
  html/
  allure-results/
  playwright-artifacts/
```

## Important Files

`pages/` contains page objects. A page object keeps page selectors and page actions in one place, so the step definitions stay clean.

`tests/features/` contains `.feature` files written in Gherkin syntax.

`tests/steps/` contains pytest-bdd step definitions that connect Gherkin steps to Python code.

`tests/conftest.py` contains shared pytest fixtures and shared steps. For example, both login features reuse the same login step:

```gherkin
When the user logs in with username "student" and password "Password123"
```

`pyproject.toml` contains project dependencies and pytest configuration.

## Setup

Install dependencies:

```powershell
uv sync
```

Install Playwright browsers:

```powershell
uv run playwright install
```

Install Java and the Java-based Allure 2 command-line tool:

```powershell
scoop install openjdk
scoop install allure
```

Verify Allure is available:

```powershell
allure --version
```

This project uses the Java-based Allure 2 CLI. It has behaved more reliably for this pytest-bdd demo than the newer npm-based Allure 3 CLI, especially while experimenting with broken scenarios and retry-style runs.

## Run Tests

Run the full test suite:

```powershell
uv run pytest
```

Run only SauceDemo tests:

```powershell
uv run pytest -m sauce
```

Run only Practice Test Automation tests:

```powershell
uv run pytest -m pta
```

Run only parser learning examples:

```powershell
uv run pytest -m parsers
```

Run smoke login tests:

```powershell
uv run pytest -m "login and smoke"
```

Run negative login tests:

```powershell
uv run pytest -m negative
```

## Debug Tests With PWDEBUG

Playwright can run in debug mode by setting `PWDEBUG=1`.

In PowerShell:

```powershell
$env:PWDEBUG=1
uv run pytest -m sauce
```

This opens the browser in headed mode and lets you step through Playwright actions with the Playwright Inspector.

To debug one specific test, use `-k`:

```powershell
$env:PWDEBUG=1
uv run pytest -k "Successful login"
```

Turn debug mode off when you are done:

```powershell
Remove-Item Env:PWDEBUG
```

## Pytest Markers

Markers help select groups of tests.

```text
smoke       critical path checks
regression  full regression suite
sauce       SauceDemo tests
pta         Practice Test Automation tests
learning    non-browser learning examples
parsers     pytest-bdd parser examples
login       authentication tests
negative    negative-path scenarios
```

## Default Reports And Artifacts

The default pytest command is configured in `pyproject.toml`.

When you run:

```powershell
uv run pytest
```

the project generates:

```text
reports/html/report.html
reports/allure-results/
reports/playwright-artifacts/
```

Playwright is configured to create:

```text
traces:      on
videos:      on
screenshots: only on failure
```

The browser is also configured to start maximized instead of using a fixed `1920x1080` viewport.

This is done in `tests/conftest.py` with:

```text
--start-maximized
no_viewport=True
```

That means Playwright does not force an artificial viewport size. The page uses the available browser window size.

## Open The HTML Report

The pytest-html report is created here:

```text
reports/html/report.html
```

Open it from PowerShell:

```powershell
Start-Process reports\html\report.html
```

Or open the file manually in your browser.

## Open The Allure Report

Allure results are created here:

```text
reports/allure-results/
```

To quickly view the report:

```powershell
allure serve reports\allure-results
```

This starts a local Allure server and opens the report in your browser.

You can also generate a static report first:

```powershell
allure generate reports\allure-results -o reports\allure-report --clean
```

Then open the generated report:

```powershell
allure open reports\allure-report
```

If `allure` is not recognized, install Java and Allure with Scoop:

```powershell
scoop install openjdk
scoop install allure
```

Playwright trace files are also attached to the matching Allure test result.

In the Allure report:

```text
Open a test result -> Attachments -> trace.zip
```

Download the attached `trace.zip`, then open it with Playwright:

```powershell
uv run playwright show-trace "path\to\downloaded\trace.zip"
```

## Open Playwright Traces

Trace files are saved under:

```text
reports/playwright-artifacts/
```

Each test gets its own artifact folder. Inside that folder, look for:

```text
trace.zip
```

Find trace files:

```powershell
Get-ChildItem reports\playwright-artifacts -Recurse -Filter trace.zip
```

Open a trace:

```powershell
uv run playwright show-trace "reports\playwright-artifacts\<test-folder>\trace.zip"
```

Example:

```powershell
uv run playwright show-trace "reports\playwright-artifacts\tests-steps-test-saucedemo-login-steps-py-test-successful-login-with-valid-credentials-chromium\trace.zip"
```

The trace viewer lets you inspect:

- browser actions
- DOM snapshots
- screenshots at each step
- network calls
- console messages
- timing information

This is usually the best debugging tool when a Playwright test fails.

The same `trace.zip` file is attached to the matching Allure test result, so you can also download it directly from the Allure report.

Do not manually edit or format files inside `reports/allure-results/`. These JSON files are generated machine output, and changing them can make Allure reports unreliable.

## Open Playwright Videos

Videos are saved under:

```text
reports/playwright-artifacts/
```

Each test artifact folder may contain:

```text
video.webm
```

Find videos:

```powershell
Get-ChildItem reports\playwright-artifacts -Recurse -Filter video.webm
```

Open a video:

```powershell
Start-Process "reports\playwright-artifacts\<test-folder>\video.webm"
```

## Open Failure Screenshots

Screenshots are configured as:

```text
--screenshot=only-on-failure
```

That means screenshots are created only when a test fails.

Find screenshots:

```powershell
Get-ChildItem reports\playwright-artifacts -Recurse -Filter *.png
```

Open a screenshot:

```powershell
Start-Process "reports\playwright-artifacts\<test-folder>\test-failed-1.png"
```

## Parser Examples

The parser examples are intentionally separated from the real browser tests.

Feature file:

```text
tests/features/parser_examples.feature
```

Step file:

```text
tests/steps/test_parser_example_steps.py
```

These examples show:

- plain string step matching
- `parsers.parse`
- `parsers.re`
- `parsers.cfparse`
- typed values like `int` and `float`
- `target_fixture`

Run them with:

```powershell
uv run pytest -m parsers
```

## Notes For Learning

Keep feature files readable. A feature should describe user behavior, not implementation details.

Keep step definitions small. A step should usually call a page object method or make one clear assertion.

Keep page objects simple. They should store locators and page-specific actions.

Use traces when a browser test fails. They show much more than a screenshot.

Use Allure when you want a nicer report organized around features and scenarios.

Use the parser examples only for learning pytest-bdd syntax. They should not be mixed into real site tests.

## References

- Playwright Python docs: https://playwright.dev/python/docs/intro
- pytest docs: https://docs.pytest.org/
- pytest-bdd docs: https://pytest-bdd.readthedocs.io/
- Allure pytest-bdd docs: https://allurereport.org/docs/pytest-bdd/
- pytest-playwright docs: https://playwright.dev/python/docs/test-runners
