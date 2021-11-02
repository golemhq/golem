
$(document).ready(function(){

    $('.report-container')[0].ExecutionReport = ExecutionReport;

    if(global.executionData == null){
        ExecutionReport.getReportData();
    } else {
	    ExecutionReport.suiteFinished = true;
        ExecutionReport.netTime = global.executionData.net_elapsed_time;
        $(".spinner").hide()
        ExecutionReport.loadReport(global.executionData);
        GeneralTable.updateGeneralTable()
        DetailTable.updateColumnHeaderFilterOptions();
    }
	$("#generalTable").on('click', 'tr', function(){
		let moduleName = $(this).find("td[data='module']").html();
		if(moduleName.length == 0){moduleName = '-'}
		DetailTable.filterDetailTableByModule(moduleName);
	})
	DetailTable.instantiateDetailTableFilterListeners();

	TestRenderer.render();

    $("#detailTable").on('click', 'tr.test-row', function () {
        DetailTable.updateTestDetail(
            $(this).attr('test-id'), $(this).attr('test-name'),
            $(this).attr('test-file'), $(this).attr('set-name'))
    });
    $("#detailTable").on('click', 'td.tc-module>span', function (e) {
        e.stopPropagation();
    });
    $("#detailTable").on('click', 'td.tc-name>span', function (e) {
        e.stopPropagation();
    });
    $("#detailTable").on('click', 'td.link>a', function (e) {
        e.stopPropagation();
    });
});


const ExecutionReport = new function(){

	this.suiteFinished = false;
	this.queryDelay = 2500;
	this.netTime = undefined;
	this.tests = {};
	this.params = {};

	this.getReportData = function() {
	    xhr.get('/api/report/execution', {
		    project: global.project,
            execution: global.execution,
            timestamp: global.timestamp
        }, executionData => {
            if(executionData.has_finished) {
                ExecutionReport.suiteFinished = true;
                ExecutionReport.netTime = executionData.net_elapsed_time;
                $(".spinner").hide()
            } else {
                $(".spinner").show();
                if(ExecutionReport.queryDelay <= 10000) {
                    ExecutionReport.queryDelay += 50
                }
                setTimeout(function(){ExecutionReport.getReportData()}, ExecutionReport.queryDelay);
            }
            ExecutionReport.loadReport(executionData);
            GeneralTable.updateGeneralTable();
            DetailTable.updateColumnHeaderFilterOptions();
        })
	}

	this.loadReport = function(execution_data){
		for(tc in execution_data.tests){
		    let test = execution_data.tests[tc];
		    let testUniqueId = ExecutionReport.testUniqueId(test);
		    if(ExecutionReport.tests.hasOwnProperty(testUniqueId)){
		        // is the test modified?
//		        let equal = Main.Utils.shallowObjectCompare(test, ExecutionReport.tests[testUniqueId]);
		        if(test.result != ExecutionReport.tests[testUniqueId].result){
		            DetailTable.updateTest(ExecutionReport.tests[testUniqueId], test);
		            ExecutionReport.tests[testUniqueId] = test;
		        }
		    } else {
		        // add test to table
		        DetailTable.addNewTestToTable(test);
		        ExecutionReport.tests[testUniqueId] = test;
		    }
		}
		if(DetailTable.hasSetNameColumn){
		    DetailTable.displaySetNameColumn();
		}
		// load execution params
		Object.keys(execution_data.params).forEach(function(param) {
		    let value = execution_data.params[param];
		    if(ExecutionReport.params[param] !== value) {
		        ExecutionReport.params[param] = value;
		        if(value != null && value != ''){
                    if(param == 'browsers') {
                        value = value.map(b => b.name)
                    }
                    if(value.constructor == Array) {
                        value = value.join(', ')
                    }
                    $(`#configSection div[data='${param}']`).show()
                    $(`#configSection div[data='${param}']>span.param-value`).html(value);
                }
		    }
		});
//		if(ExecutionReport.suiteFinished){
//		    //DetailTable.refreshResultFilterOptions();
//		}
	}

	this.testUniqueId = function(test) {
	    let uniqueId = `${test.test_file}.${test.test}`;
	    if(test.set_name)
	        uniqueId = uniqueId + `.${test.set_name}`;
	    return uniqueId
	}

	this.testUniqueIdHref = function(uniqueId) {
	    return `${uniqueId}Collapse`.replaceAll('.', '-')
	}

	this.testModule = function(testFile) {
        // for test file 'module.submodule.test_file' module is 'module'
	    let module = ''
        let parts = testFile.split('.');
        parts.pop()
        if (parts.length) {
            module = parts[0]
        }
        return module
	}
}


const GeneralTable = new function(){

	this.resultColumns = [
		Main.ResultsEnum.success.code,
		Main.ResultsEnum.failure.code
	]

	this.updateGeneralTable = function() {
        let moduleData = {};
        let generalData = {
            resultTotals: {},
            tests: 0,
            moduleElapsedTime: 0
        };
        for(t in ExecutionReport.tests) {
            let test = ExecutionReport.tests[t];
            let module = ExecutionReport.testModule(test.test_file);

            if(!moduleData.hasOwnProperty(module)) {
                moduleData[module] = {
                    resultTotals: {},
                    tests: 0,
                    moduleElapsedTime: 0
                }
            }
            if(!moduleData[module].resultTotals.hasOwnProperty(test.result)) {
                moduleData[module].resultTotals[test.result] = 0
            }
            moduleData[module].resultTotals[test.result] += 1;
            moduleData[module].tests += 1;
            moduleData[module].moduleElapsedTime += test.elapsed_time;
            // general data
            if(!generalData.resultTotals.hasOwnProperty(test.result)) {
                generalData.resultTotals[test.result] = 0
            }
            generalData.resultTotals[test.result] += 1;
            generalData.tests += 1;
            generalData.moduleElapsedTime += test.elapsed_time;
        }
        moduleData['totalModuleRow'] = generalData;

        for (const module in moduleData) {
            let thisModuleData = moduleData[module];
            let moduleRow = GeneralTable.getOrAddModuleRow(module);
            let progressContainer = moduleRow.find("td[data='percentage']>div.progress");

            for (const result in thisModuleData.resultTotals) {
                if(!Main.ReportUtils.hasProgressBarForResult(progressContainer, result)) {
                    Main.ReportUtils.createProgressBars(progressContainer, [result])
                }
                let percentage = thisModuleData.resultTotals[result] * 100 / thisModuleData.tests;
                Main.ReportUtils.animateProgressBar(progressContainer, result, percentage, thisModuleData.resultTotals[result])
            }
            moduleRow.find("td[data='total-tests']").html(thisModuleData.tests);
            moduleRow.find("td[data='total-time']").html(
                Main.Utils.secondsToReadableString(thisModuleData.moduleElapsedTime));

            // check if pending progress bar is stale
            let moduleHasPending = 'pending' in thisModuleData.resultTotals;
            if(!moduleHasPending) {
                Main.ReportUtils.animateProgressBar(progressContainer, 'pending', 0)
            }
            // check if running progress bar is stale
            let moduleHasRunning = 'running' in thisModuleData.resultTotals;
            if(!moduleHasRunning) {
                Main.ReportUtils.animateProgressBar(progressContainer, 'running', 0)
            }

            // If there are more than 2 modules then the
            // "" module should be displayed
            if(Object.keys(moduleData).length > 2 && GeneralTable.hasModuleRow('')) {
                GeneralTable.getModuleRow('').show();
            }
        };

        if(ExecutionReport.netTime != undefined) {
            $("#totalRow td[data='net-time']").html(
                Main.Utils.secondsToReadableString(ExecutionReport.netTime))
        }
	}

    this.getModuleRow = function(moduleName) {
        return $(`#generalTable tr[module-name='${moduleName}']`);
    }

	this.addModuleRow = function(moduleName) {
		let moduleRow = GeneralTable.generateModuleRow({moduleName: moduleName});
		moduleRow.insertBefore("#totalRow");
		return moduleRow
	}

    this.hasModuleRow = function(moduleName) {
        return this.getModuleRow(moduleName).length == 1
    }

	this.getOrAddModuleRow = function(moduleName) {
	    if(this.hasModuleRow(moduleName)) {
	        return this.getModuleRow(moduleName)
	    } else {
	        return this.addModuleRow(moduleName)
	    }
	}

	// Add a new column to GeneralTable for result
	this.addColumnForResult = function(result){
		GeneralTable.resultColumns.push(result);
		let headerTh = $(`<th result="${result}">${Main.Utils.capitalizeWords(result)}</th>`)
		// insert th for new result column
		$("#generalTable th[data='percentage']").before(headerTh);
		// insert td for each tr for new result column
		$("#generalTable tr").each(function(i, tr){
			let td = $(`<td data='result' result="${result}">0</td>`);
			$(tr).find("td[data='percentage']").before(td);
		})
	}

	this.generateModuleRow = function(data) {
		let resultColumns = '';
		GeneralTable.resultColumns.forEach(function(result) {
			resultColumns += (`<td data="result" result="${result}">0</td>`)
		});
		// if module name == '' the row is hidden by default.
		// it should be un-hidden when there are other module names
		let hideRow = '';
		if(data.moduleName == '') {
		    hideRow = 'style="display: none"';
		}
        var row = `
            <tr class="general-table-row cursor-pointer" module-name="${data.moduleName}" ${hideRow}>
                <td data="module">${data.moduleName}</td>
                <td data="total-tests">${data.totalTests}</td>
                <td data="percentage"><div class='progress'></div></td>
                <td data="total-time"></td>
            </tr>`;
        return $(row)
    }
}


const DetailTable = new function(){

	this.hasSetNameColumn = false;

	this.addNewTestToTable = function(test){
		let urlToTest = `/report/${global.project}/${global.execution}/${global.timestamp}/${test.test_file}/${test.set_name}/`;
		let number = Object.keys(ExecutionReport.tests).length + 1;
		let testRow = DetailTable.generateTestRow({
		    number: number,
			test: test.test,
			testFile: test.test_file,
			browser: test.browser,
			environment: test.environment,
			elapsedTime: test.elapsed_time,
			setName: test.set_name,
			result: test.result,
			urlToTest: urlToTest,
			static: global.static,
			testUniqueId: ExecutionReport.testUniqueId(test)
		});
		if(test.set_name.length > 0 && !DetailTable.hasSetNameColumn){
		    DetailTable.hasSetNameColumn = true;
		}
		TestRenderer.queueTest(testRow);
		return testRow
	}

    this.updateTest = function(oldTest, newTest){
        let testRow = DetailTable.getTestRow(ExecutionReport.testUniqueId(oldTest));
		if(oldTest.result != newTest.result){
		    let resultString = `${Main.Utils.getResultIcon(newTest.result)} ${newTest.result}`;
		    testRow.find('.test-result').html(resultString);
		    testRow.attr('result', newTest.result);
		}
		if(oldTest.browser != newTest.browser){
		    testRow.find('.test-browser').html(newTest.browser);
		}
		if(oldTest.environment != newTest.environment){
		    testRow.find('.test-environment').html(newTest.environment);
		}
		if(oldTest.test_elapsed_time != newTest.elapsed_time){
		    testRow.find('.test-time').html(
		        Main.Utils.secondsToReadableString(newTest.elapsed_time));
		}
		if(oldTest.set_name != newTest.set_name){
		    DetailTable.hasSetNameColumn = true;
			DetailTable.displaySetNameColumn();
			testRow.find('.set-name').html(newTest.set_name.toString());

		}
//		if(oldTest.module != newTest.module){
//		    let module = newTest.module.length > 0 ? newTest.module : '';
//		    DetailTable.updateColumnHeaderFilterOptions('module', module);
//		}
        DetailTable.updateColumnHeaderFilterOptions();
	}

	this.updateTestDetail = function(testId, testName, testFile, setName){
	    let _loadTest = function(report){
	        let detailPanel = $(`#${ExecutionReport.testUniqueIdHref(testId)}`);
            // update logs
            let logPanel = detailPanel.find('div.logs');
            let loadLogs = function(logs, logContainer){
                logs.forEach(function(line){
                    let displayedLinesStrings = [];
                    logContainer.find('div.log-line').each(function(){
                        displayedLinesStrings.push($(this).html())
                    });
                    if(!displayedLinesStrings.includes(line)){
                        let logLine = $("<div class='log-line'></div>");
                        logLine.text(line);
                        logContainer.append(logLine);
                    }
                });
            }
            loadLogs(report.info_log, logPanel.find('.info-log'));
            loadLogs(report.debug_log, logPanel.find('.debug-log'));

            let rightColumn = detailPanel.find('.detail-right-column');
            // add description
            let detailHasDescription = rightColumn.find('.detail-description').length > 0;
            if(report.description && !detailHasDescription){
                let descriptionBox = $(
                    `<div class="detail-description test-detail-box">
                        <div class="test-detail-box-title">Description</div>
                        <div class="detail-description-value">${report.description}</div>
                    </div>`);
                rightColumn.append(descriptionBox)
            }
            // update steps
            let stepBox = rightColumn.find('div.step-list');
            if(report.steps.length > 0 && stepBox.length == 0){
                let stepBox = $(`
                    <div class="step-list test-detail-box">
                        <div class="test-detail-box-title">Steps</div>
                        <ol></ol>
                    </div>`);
                report.steps.forEach(function(step){
                    let stepContent = $(`<li>${step.message}</li>`);
                    if(step.error){
                        stepContent.append(' - ');
                        stepContent.text(step.error.message)
                    }
                    if(step.screenshot){
                        let guid = Main.Utils.guid();
                        let screenshotIcon = `
                            <span class="icon cursor-pointer" aria-hidden="true" data-toggle="collapse" data-target="#${guid}" aria-expanded="false" aria-controls="${guid}">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                                </span>
                            <div class="collapse text-center" id="${guid}">
                                <img class="step-screenshot cursor-pointer" style="width: 100%"
                                    src="data:image/png;base64,${step.screenshot}" onclick="Main.ReportUtils.expandImg(event);">
                            </div>`;
                        stepContent.append(' ' + screenshotIcon)
                    }
                    stepBox.find('ol').append(stepContent);
                });
                rightColumn.append(stepBox)
            }
	    }

	    if(global.static) {
	        _loadTest(global.detailTestData[testId])
	    } else {
	        xhr.get('/api/report/test', {
                project: global.project,
                execution: global.execution,
                timestamp: global.timestamp,
                testFile: testFile,
                test: testName,
                setName: setName
            }, report => {
                _loadTest(report)
                if(report.result == 'pending' || report.result == 'running' || report.result == '') {
                    setTimeout(() => DetailTable.updateTestDetail(testId, testName, testFile, setName), 1500);
                }
            })
        }
	}

	this.updateColumnHeaderFilterOptions = function(){
	    let columns = {
	        'module': [],
	        'browser': [],
	        'result': [],
	        'environment': []
	    }
        let modules = Object.values(ExecutionReport.tests).map(value => ExecutionReport.testModule(value.test_file) );
        columns.module = [...new Set(modules)];
        let index = columns.module.findIndex(x => x === '');
        if(index != -1){
            columns.module[index] = '-'
        }

	    let browsers = Object.values(ExecutionReport.tests).map(value => value.browser );
        columns.browser = [...new Set(browsers)];
        if(columns.browser.indexOf('') > -1){ columns.browser.splice(index, 1) }

        let results = Object.values(ExecutionReport.tests).map(value => value.result);
        columns.result = [...new Set(results)];
        if(columns.result.indexOf('') > -1){ columns.result.splice(index, 1) }

        let environments = Object.values(ExecutionReport.tests).map(value => value.environment);
        columns.environment = [...new Set(environments)];
        if(columns.environment.indexOf('') > -1){ columns.environment.splice(index, 1) }

//        let setNames = Object.values(ExecutionReport.tests).map(value => value.set_name);
//        columns['set-name'] = [...new Set(setNames)];
//        if(columns['set-name'].indexOf('') > -1){ columns['set-name'].splice(index, 1) }

        for(column in columns){
            let columnOptions = columns[column];
            let colHeader = $(`#detailTable th[colname='${column}']`);
            let optionList = colHeader.find("ul>form");
            let currentOptions = optionList.find("li>div.checkbox>label>span");
            let currentOptionNames = currentOptions.toArray().map(option => option.innerText);
            columnOptions.forEach(function(option){
                if(!currentOptionNames.includes(option)){
                    let newOption = `
                        <li>
                            <div class="checkbox">
                                <label><input type="checkbox" value="${option}"> <span>${option}</span></label>
                            </div>
                        </li>`;
                    optionList.append(newOption);
                }
            })
            // remove stale options
            currentOptions.each(function(){
                if(!columnOptions.includes($(this).html())){
                    $(this).closest('li').remove()
                }
            })
            // show funnel icon if there are two or more options
            if(columnOptions.length +1 > 1){ colHeader.find('.funnel-icon').show() }
        }
	}

	this.instantiateDetailTableFilterListeners = function(){
		$("#detailTable").on('change', "th input:checkbox", function(){
			DetailTable.applyFilters()
		})
	}

	this.applyFilters = function(){
		// display all columns
		$("#detailTable tr").show();
		let testTableRows = $("#detailTable>tbody>tr.test-row");
		// for each column header
		$("#detailTable th").each(function($index){
			let thisColumnHeader = $(this);
			let checkedCheckboxes = thisColumnHeader.find("input[type='checkbox']:checked");
			let columnIndex = $index;
			let colname = $(this).attr('colname');
			if(checkedCheckboxes.length){
				// mark this column header as 'filtered'
				thisColumnHeader.addClass('filtered');
				let checkedValues = [];
				checkedCheckboxes.each(function(i, checkbox){
				    let value = $(checkbox).attr('value')
					checkedValues.push(value);
				});
				// for reach row
				testTableRows.each(function(){
					let thisRow = $(this);
					let thisCellValue = $(this).find('td').get(columnIndex).innerText;

                    let showRow = false;
                    if(colname == 'module' && checkedValues.includes('-') && ExecutionReport.testModule(thisCellValue.trim()) == '') {
					    // Hide if it's the module column, '-' option is checked and current
					    // test has a module
					    showRow = true;
					}
					if(checkedValues.some(value => thisCellValue.trim().includes(value))){
                        showRow = true
                    }
					if(!showRow){
						thisRow.hide();
						let testId = thisRow.attr('test-id');
						DetailTable.getTestDetailRow(testId).hide()
					}
				})
			} else {
				// mark column header as not filtered
				thisColumnHeader.removeClass('filtered');
			}
		});
		DetailTable.updateNumbering()
	}

	this.filterDetailTableByModule = function(moduleName){
		// remove all filters in module column, apply the filter provided
		// keep any other filters
		let moduleColumnHeader = $("#detailTable th[colname='module']");
		moduleColumnHeader.find('input:checkbox').prop('checked', false).change();
		if(moduleName != 'Total'){
			moduleColumnHeader.find(`div.checkbox label:contains('${moduleName}') input`)
			                  .prop('checked', true).change();
		}
	}

	this.generateTestRow = function(data){
		let resultString = `${Main.Utils.getResultIcon(data.result)} ${data.result}`;
		let href = ExecutionReport.testUniqueIdHref(data.testUniqueId);
		let testDetailRow = DetailTable.generateTestDetailRow(data.test, data.testFile, data.setName, data.testUniqueId, href);
        let elapsedTime;
        if(data.elapsedTime == null) {
            elapsedTime = ''
        } else {
            elapsedTime = Main.Utils.secondsToReadableString(data.elapsedTime)
        }
        var row = `
            <tr test-id="${data.testUniqueId}" test-name="${data.test}" test-file="${data.testFile}"
                    set-name="${data.setName}" result="${data.result}" class="test-row cursor-pointer"
                    data-toggle="collapse" href="#${href}" aria-expanded="false">
                <td class="tc-number">${data.number}</td>
                <td class="tc-module"><span class="cursor-auto">${data.testFile}</span></td>
                <td class="tc-name"><span class="cursor-auto">${data.test}</span></td>
                <td class="set-name">${data.setName}</td>
                <td class="test-environment">${data.environment}</td>
                <td class="test-browser">${data.browser}</td>
                <td class="test-result">${resultString}</td>
                <td class="test-time">${elapsedTime}</td>
                <td class="link" style="${ data.static ? 'display: None' : '' }">
                    <a href="${data.urlToTest}">
                        <span class="glyphicon glyphicon-new-window" aria-hidden="true"></span>
                    </a>
                </td>
            </tr>
            ${testDetailRow}`;
        return row
    }

    this.generateTestDetailRow = function(testName, testFile, setName, testUniqueId, href){
        let id = `${testUniqueId}Collapse`;
        let safeTestUniqueId = ExecutionReport.testUniqueIdHref(testUniqueId);
        let onclick = "$(this).siblings().removeClass('active');$(this).addClass('active');"
        let row = `
            <tr test-id="${testUniqueId}" test-name="${testName}" test-file="${testFile}" set-name="${setName}" class="test-detail-row">
                <td colspan="100%">
                    <div id="${href}" class="collapse row test-detail">
                        <div class="logs col-md-6 test-detail-box">
                            <div class="test-detail-box-title">
                                Logs &nbsp;
                                <a href="#${safeTestUniqueId}DebugLog" class="link-without-underline" role="tab"
                                    data-toggle="tab" onclick="${onclick}">debug</a>
                                <a href="#${safeTestUniqueId}InfoLog" class="active link-without-underline" role="tab"
                                    data-toggle="tab" onclick="${onclick}">info</a>
                            </div>
                            <div class="tab-content">
                                <div role="tabpanel" class="tab-pane info-log active" id="${safeTestUniqueId}InfoLog"></div>
                                <div role="tabpanel" class="tab-pane debug-log" id="${safeTestUniqueId}DebugLog"></div>
                            </div>
                        </div>
                        <div class='detail-right-column col-md-6'></div>
                    </div>
                </td>
            </tr>`;

        $(row).find('.test-detail-box-title a').click(function (e) {
          e.preventDefault()
          $(this).tab('show')
        })
        return row
    }

    this.displaySetNameColumn = function(){
        let detailTable = $("#detailTable");
        if(!detailTable.hasClass('set-name-displayed')){
            $("#detailTable").addClass('set-name-displayed')
        }
    }

    this.getTestRow = function(testId){
        return $(`tr.test-row[test-id='${testId}']`)
    }

    this.getTestDetailRow = function(setName){
        return $(`tr.test-detail-row[test-set='${setName}']`)
    }

    this.updateNumbering = function(){
        let number = 1;
        $("#detailTable tbody tr.test-row:visible").each(function(i, row){
            $(row).find('.tc-number').html(i+1)
        })
    }
}


const TestRenderer = new function(){

    this.queue = [];
    this.rendering = false;
    this.tbody = document.querySelector('#detailTable tbody');

    this.queueTest = function(row){
        TestRenderer.queue.push(row)
    }

    this.render = function(){
        if(!TestRenderer.rendering){
            TestRenderer.rendering = true;
            if(TestRenderer.queue.length > 0){
                let queue_ = TestRenderer.queue.splice(0, 50);
                let s = queue_.join('');
                TestRenderer.tbody.innerHTML += s;
            }
            TestRenderer.rendering = false;
        }

        if(!ExecutionReport.suiteFinished || TestRenderer.queue.length != 0){
            setTimeout(function(){TestRenderer.render()}, 300)
        }
    }
}
