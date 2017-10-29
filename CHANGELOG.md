# Changelog


## [Unreleased]

### Changed
- Split project dashboard into suites, tests and pages

## [0.3.0] - 2017-10-16

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