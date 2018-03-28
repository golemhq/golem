# Changelog


## [Unreleased]

### Added
- actions: verify_alert_is_present, verify_alert_is_not_present, accept_alert, dismiss_alert

### Fixed
- #93

## [0.4.6] - 2018-03-12

### Added
- actions: set_browser_capability, add_cookie, delete_cookie, delete_all_cookies, get_cookie, get_cookies, verify_cookie_value, verify_cookie_exists

### Fixed
- #78

## [0.4.5] - 2017-12-19

### Added
- 'golem' script to start the framework instead of 'python golem.py'
- get_current_url action

### Changed
- 'golem.py' changed to 'golem_start.py', however it's not needed, just use 'golem run' or 'golem gui' instead.

## [0.4.2] - 2017-12-15

### Added
- Filter execution report table by column values (#74)

## [0.4.1] - 2017-12-03

### Added
- Can open multiple browsers for the same test.
- New actions: open_browser, activate_browser
- Add INFO and DEBUG logs to test report

### Fixed
- #59, added syntax validation for test builder and page builder

### Deprecated
- Removed 'file_log_level' setting, by default two log files are generated: execution_info.log, execution_debug.log

## [0.4.0] - 2017-11-26

### Changed
- csv files are created in the same folder as the test. Csv files in /data/ folder will keep working with a deprecation warning

### Added
- Rename button for suites, tests and pages
- 'test_data' setting, options are 'csv' and 'infile'
- Tests can store data inside the test itself


## [0.3.1] - 2017-11-08

### Changed
- Split project dashboard into suites, tests and pages
- Can add new pages from the test builder
- Can edit pages from the test builder in a modal dialog
- Add file button & add folder button in Suites, Tests and Pages

## [0.3.0] - 2017-10-26

### Added
- get(url) action for consistency with Selenium API
- Add set name to report, to differentiate when a single test is run with multiple data sets

### Changed
- It is required to surround strings with quotes in test builder
- Changed actions: get -> http_get and post -> http_post

## [0.2.2] - 2017-10-16

### Added
- Environments support
- 'refresh' action to golem.actions
- 'set_window_size' action to golem.actions (thanks to danielmaddern)
- IE driver support
- 'screenshot_on_end' setting
- The user can define remote browsers

### Changed
- New layout design


## [0.2.1] - 2017-10-06
### Added
- Documented the Golem Public API
- UP, DOWN, LEFT, RIGHT options to actions.press_key (thanks to danielmaddern)
- Add counter of total and selected tests in suite view
- golem.execution module to track data for current execution

### Changed
- golem.selenium is now golem.browser
- golem.selenium.get_driver is now golem.browser.get_browser


## [0.1.22] - 2017-09-27
### Added
- 'clear' action to golem.actions

### Fixed
- Missing js files in manifest.in



### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security