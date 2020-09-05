# Changelog

## [Unreleased]

### Added

- Suite code view

## [0.9.1] - 2020-08-03

### Added

- Rename/Delete folders; improved file list navigation [#179](https://github.com/golemhq/golem/issues/179)

- Remove executions from report dashboard

- Skip flag to test [#146](https://github.com/golemhq/golem/issues/146)

- Actions: log, random_str, random_int, random_float

- *--cli-log-level* arg to golem run command

- Document golem.execution module

### Fixed

- [#112](https://github.com/golemhq/golem/issues/112)

- [#186](https://github.com/golemhq/golem/issues/186) :: ignaciocabeza

- [#169](https://github.com/golemhq/golem/issues/169)

### Deprecated

- console_log_level setting, renamed to: cli_log_level

## [0.9.0] - 2019-06-30

### Added

- createsuperuser command

- User management page, user profile page

- Implicit/explicit actions import [#136](https://github.com/golemhq/golem/issues/136)
     
     * Actions can now be imported explicitly.
     * New setting key: *implicit_actions_import*, default is true.

- Implicit/explicit page import [#137](https://github.com/golemhq/golem/issues/137)
     
     * Pages can now be imported explicitly.
     * New setting key: *implicit_page_import*, default is true.

### Removed

- createuser command

### Changed

- A file named **.golem** must exist in the test directory. Migrate steps: 
    
    1. Create a file named **.golem** in the test directory root with the following content:
    
    ```
    [gui]
    secret_key = your_secret_key_string
    ```

- Passwords are now hashed. Migrate steps:
   
   1. Delete old **users.json** file
   2. Create a super user using the ```golem createsuperuser``` command
   3. Non superusers must be created using the */users/* page

- *admin* user role changed to *superuser*
    
    User roles are: superuser, admin, standard, read-only, reports-only

- Improved test step parser [#168](https://github.com/golemhq/golem/issues/168)
    
    * Non function calls are shown as code blocks (using a code editor)
    * Added **code_block** action to insert new code blocks

- golem.execution.workspace -> golem.execution.testdir

## [0.8.0] - 2019-04-10

### Changed

- **-t, \-\-threads** argument changed to **-p, \-\-processes**

### Deprecated

Python 3.4

### Added

- Filter tests by tags :: r-roos, Luciano Renzi
    * New argument for *golem run* command: ```-t, --tags```
    * Add and edit tags using the UI
    * Accept *tag expressions* for complex comparisons 
    * Docs: [Filter Tests by Tags](https://golem-framework.readthedocs.io/en/latest/running-tests.html#filter-tests-by-tags)
- New args to ```golem gui``` command: --host (default 127.0.0.1), -d|--debug (default False)
- New actions: assert_element_value, assert_element_value_is_not, verify_element_value, verify_element_value_is_not, send_keys_with_delay
- New WebElement methods: inner_html, outer_html, send_keys_with_delay

## [0.7.0] - 2019-01-21

### Added

- Generate JUnit (XML) report :: Daniel Maddern
- Generate JUnit and HTML reports after execution
    * report options: 'junit', 'json', 'html', 'html-no-images'
- Specify name and location for the generated reports
- Modify screenshot format, size and compression
- Exit with status code = 1 when execution has errors/failures :: r-roos
- Document Golem standalone generation using PyInstaller
- Actions: timer_start, timer_stop

### Changed

- Report filename from 'execution_report.json' to 'report.json'

## [0.6.2] - 2018-12-05

### Added
- Secrets data feature :: r-roos
    * https://golem-framework.readthedocs.io/en/latest/test-data.html#secrets
- GUI improvements #149 :: Luciano Renzi

### Fixed

- Maximize Chrome in macOS issue #130 :: Filip Richtárik, r-roos

## [0.6.1] - 2018-11-14

### Added
- 'start_maximized' setting key
- Firefox headless ('firefox-headless' and 'firefox-remote-headless')
- Run every test in tests folder: ```golem run <project> .```
- Run every test in a sub-folder: ```golem run <project> foo/bar/```
- Run test or suite from relative path: ```golem run <project> path/to/test.py```

## [0.6.0] - 2018-09-30

### Added

- New actions: go_back, set_search_timeout, get_search_timeout, double_click, focus_element, set_trace, error,
execute_javascript, fail, javascript_click, verify_selected_option_by_text, verify_selected_option_by_value,
get_alert_text, send_text_to_alert, submit_prompt_alert, verify_alert_text, verify_alert_text_is_not, wait_for_alert_present
verify_element_has_attribute, verify_element_has_not_attribute, verify_element_has_focus, verify_element_has_not_focus,
verify_page_not_contains_text, verify_element_text, verify_element_text_is_not, verify_element_text_not_contains, verify_title
verify_title_contains, verify_title_is_not, verify_title_not_contains, verify_url, verify_url_contains, verify_url_is_not
verify_url_not_contains, wait_for_element_present, wait_for_element_not_enabled, wait_for_page_contains_text,
wait_for_page_not_contains_text, wait_for_element_text, wait_for_element_text_is_not, wait_for_element_text_contains,
wait_for_element_text_not_contains, wait_for_element_has_attribute, wait_for_element_has_not_attribute, wait_for_title,
wait_for_title_is_not, wait_for_title_contains, wait_for_title_not_contains, verify_element_attribute_value,
verify_element_attribute_is_not, go_forward, check_element, uncheck_element, submit_form, switch_to_frame, switch_to_parent_frame
get_active_element, get_window_title, get_window_titles, get_window_handle, get_window_handles, get_window_index,
switch_to_window_by_index, switch_to_first_window, switch_to_last_window, switch_to_window_by_title, switch_to_window_by_partial_title
switch_to_window_by_url, switch_to_window_by_partial_url, verify_amount_of_windows, close_window
verify_window_present_by_title, verify_window_present_by_partial_title, maximize_window, get_page_source, switch_to_next_window
switch_to_previous_window, close_window_by_index, close_window_by_title, close_window_by_url, close_window_by_partial_title,
close_window_by_partial_url, get_element_attribute, get_element_value, get_element_text, wait_for_window_present_by_title,
wait_for_window_present_by_partial_title, get_window_size, get_data, send_secure_keys

- Added verify_* actions for soft assertions and assert_* for hard assertions

### Changed

- Renamed actions:
  - capture -> take_screenshot
  - clear -> clear_element
  - close -> close_browser
  - debug -> interactive_mode
  - mouse_hover -> mouse_over
  - select_by_index -> select_option_by_index
  - select_by_text -> select_option_by_text
  - select_by_value -> select_option_by_value
  - verify_alert_is_present -> verify_alert_present
  - verify_alert_is_not_present -> verify_alert_not_present
  - verify_cookie_exists -> verify_cookie_present
  - verify_is_enabled -> verify_element_enabled
  - verify_is_not_enabled -> verify_element_not_enabled
  - verify_is_selected -> verify_element_checked
  - verify_is_not_selected -> verify_element_not_checked
  - verify_is_visible -> verify_element_displayed
  - verify_is_not_visible -> verify_element_not_displayed
  - verify_exists -> verify_element_present
  - verify_not_exists -> verify_element_not_present
  - verify_text -> verify_page_contains_text
  - verify_text_in_element -> verify_element_text_contains
  - wait_for_element_not_exist -> wait_for_element_not_present
  - wait_for_element_visible -> wait_for_element_displayed
  - wait_for_element_not_visible -> wait_for_element_not_displayed

- Changed test results: 'pass' -> 'success'; 'fail' -> 'failure', 'error', 'code error'.
- report.json format changed. NOTE: previous reports (<0.6.0) won´t work in the UI report viewer
- Docs were rewritten

### Removed
- Deprecated actions: assert_contains, assert_equals, assert_false, assert_true, verify_selected_option

## [0.5.0] - 2018-05-12

### Added
- Support for Edge and Opera
- Extend WebDriver and WebElement
- wait_displayed arg to find method, wait_displayed setting

### Changed
- Renamed 'implicit_wait' setting to 'search_timeout'
- CSV data files will only store strings and won't cast values to other types

### Removed
- selector by 'text'


## [0.4.8] - 2018-05-12

### Fixed

- Issues: #78 #98

## [0.4.7] - 2018-05-07

### Added
- actions: verify_alert_is_present, verify_alert_is_not_present, accept_alert, dismiss_alert
- Download report as HTML (@danielmaddern)
- Integrate with py-webdriver-manager

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