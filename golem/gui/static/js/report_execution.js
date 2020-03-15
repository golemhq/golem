
$(document).ready(function(){

    $('.report-container')[0].ExecutionReport = ExecutionReport;

    if(global.executionData == null){
        ExecutionReport.getReportData();
    }
    else{
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
        DetailTable.updateTestDetail($(this).attr('test-full-name'), $(this).attr('test-set'))
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

	this.getReportData = function(){
		 $.ajax({
            url: "/api/report/suite/execution",
            data: {
                project: global.project,
                suite: global.suite,
                execution: global.execution
            },
            dataType: 'json',
            type: 'GET',
            success: function(executionData){
	  			if(executionData.has_finished){
	  				ExecutionReport.suiteFinished = true;
	  				ExecutionReport.netTime = executionData.net_elapsed_time;
                    $(".spinner").hide()
	  			}
	  			else{
	  			    $(".spinner").show();
					if(ExecutionReport.queryDelay <= 10000){
						ExecutionReport.queryDelay += 50
					}
					setTimeout(function(){ExecutionReport.getReportData()}, ExecutionReport.queryDelay);
				}
	  			ExecutionReport.loadReport(executionData);
	  			GeneralTable.updateGeneralTable();
	  			DetailTable.updateColumnHeaderFilterOptions();
	  		}
        });
	}

	this.loadReport = function(execution_data){
		for(tc in execution_data.tests){
		    let test = execution_data.tests[tc];
		    if(ExecutionReport.tests.hasOwnProperty(test.test_set)){
		        // is the test modified?
		        let equal = Main.Utils.shallowObjectCompare(test, ExecutionReport.tests[test.test_set]);
		        if(!equal){
		            DetailTable.updateTest(ExecutionReport.tests[test.test_set], test);
		            ExecutionReport.tests[test.test_set] = test;
		        }
		    }
		    else{
		        // add test to table
		        DetailTable.addNewTestToTable(test);
		        ExecutionReport.tests[test.test_set] = test;
		    }
		}
		if(DetailTable.hasSetNameColumn){
		    DetailTable.displaySetNameColumn();
		}
		// load execution params
		Object.keys(execution_data.params).forEach(function(param){
		    let value = execution_data.params[param];
		    if(ExecutionReport.params[param] !== value){
		        ExecutionReport.params[param] = value;
		        if(value != null){
                    if(param == 'browsers'){
                        value = value.map(b => b.name)
                    }
                    if(value.constructor == Array){
                        value = value.join(', ')
                    }
                    $(`#configSection div[data='${param}']>span.param-value`).html(value);
                }
		    }
		});
//		if(ExecutionReport.suiteFinished){
//		    //DetailTable.refreshResultFilterOptions();
//		}
	}

	this.formatTimeOutput = function(seconds){
		let final = '';
		let min, sec, ms;
		if(seconds >= 60){
			min = Math.floor(seconds/60);
			min = Math.round(min * 10) / 10;
			remainder = seconds % 60
			if(remainder != 0){
				sec = remainder;
				sec = Math.round(sec * 10) / 10;
			}
		}
		else{
			sec = Math.round(seconds * 10) / 10;
		}
		if(min != undefined){
			final += min + 'm '
		}
		if(sec != undefined){
			final += sec + 's'
		}
		return final
	}
}


const GeneralTable = new function(){

	this.resultColumns = [
		Main.ResultsEnum.success.code,
		Main.ResultsEnum.failure.code
	]

	this.updateGeneralTable = function(){
        let moduleData = {};
        let generalData = {
            resultTotals: {},
            tests: 0,
            moduleElapsedTime: 0
        };
        for(t in ExecutionReport.tests){
            let test = ExecutionReport.tests[t];
            if(!moduleData.hasOwnProperty(test.module)){
                moduleData[test.module] = {
                    resultTotals: {},
                    tests: 0,
                    moduleElapsedTime: 0
                }
            }
            if(!moduleData[test.module].resultTotals.hasOwnProperty(test.result)){
                moduleData[test.module].resultTotals[test.result] = 0
            }
            moduleData[test.module].resultTotals[test.result] += 1;
            moduleData[test.module].tests += 1;
            moduleData[test.module].moduleElapsedTime += test.test_elapsed_time;
            // general data
            if(!generalData.resultTotals.hasOwnProperty(test.result)){
                generalData.resultTotals[test.result] = 0
            }
            generalData.resultTotals[test.result] += 1;
            generalData.tests += 1;
            generalData.moduleElapsedTime += test.test_elapsed_time;
        }
        moduleData['totalModuleRow'] = generalData;

        Object.keys(moduleData).forEach(function(module){
            let thisModuleData = moduleData[module];
            let moduleRow = GeneralTable.getModuleRow(module);
            let progressContainer = moduleRow.find("td[data='percentage']>div.progress");

            Object.keys(thisModuleData.resultTotals).forEach(function(result){
                // pending and running do not have their own columns
                if(result != 'pending' && result != 'running'){
                    // does the Detail Table has column for this test result?
                    if(!GeneralTable.hasColumnForResult(result)){
                        GeneralTable.addColumnForResult(result)
                    }
                    // update column value for this result
                    moduleRow.find(`td[data='result'][result='${result}']`).html(thisModuleData.resultTotals[result]);
                }
                if(!Main.ReportUtils.hasProgressBarForResult(progressContainer, result)){
                    Main.ReportUtils.createProgressBars(progressContainer, [result])
                }
                let percentage = thisModuleData.resultTotals[result] * 100 / thisModuleData.tests;
                Main.ReportUtils.animateProgressBar(progressContainer, result, percentage)
            })
            moduleRow.find("td[data='total-tests']").html(thisModuleData.tests);
            moduleRow.find("td[data='total-time']").html(ExecutionReport.formatTimeOutput(thisModuleData.moduleElapsedTime));

            // check if pending progress bar is stale
            let moduleHasPending = 'pending' in thisModuleData.resultTotals;
            if(!moduleHasPending){
                Main.ReportUtils.animateProgressBar(progressContainer, 'pending', 0)
            }
            // check if running progress bar is stale
            let moduleHasRunning = 'running' in thisModuleData.resultTotals;
            if(!moduleHasRunning){
                Main.ReportUtils.animateProgressBar(progressContainer, 'running', 0)
            }
        });

        if(ExecutionReport.netTime != undefined){
            $("#totalRow td[data='net-time']").html(ExecutionReport.formatTimeOutput(ExecutionReport.netTime))
        }
	}

	this.addModuleRow = function(module){
		let moduleRow = GeneralTable.generateModuleRow({moduleName: module});
		moduleRow.insertBefore("#totalRow");
		return moduleRow
	}

	this.getModuleRow = function(module){
	    let moduleRow = $(`#generalTable tr[module-name='${module}']`);
		if(moduleRow.length == 0){
			moduleRow = GeneralTable.addModuleRow(module);
		}
		return moduleRow
	}

	this.hasColumnForResult = function(result){
		let columnHeader = $(`#generalTable th[result='${result}']`);
		return columnHeader.length != 0
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

	this.generateModuleRow = function(data){
		let resultColumns = '';
		GeneralTable.resultColumns.forEach(function(result){
			resultColumns += (`<td data="result" result="${result}">0</td>`)
		});
        var row = `
            <tr class="general-table-row cursor-pointer" module-name="${data.moduleName}">
                <td data="module">${data.moduleName}</td>
                <td data="total-tests">${data.totalTests}</td>
        		${resultColumns}        
                <td data="percentage"><div class='progress'></div></td>
                <td data="total-time"></td>
                <td data="net-time"></td>
            </tr>`;
        return $(row)
    }
}


const DetailTable = new function(){

	this.hasSetNameColumn = false;

	this.addNewTestToTable = function(test){
		let urlToTest = `/report/project/${global.project}/${global.suite}/${global.execution}/${test.full_name}/${test.test_set}/`;
		let number = Object.keys(ExecutionReport.tests).length + 1;
		let testRow = DetailTable.generateTestRow({
		    number: number,
			testSet: test.test_set,
			module: test.module,
			name: test.name,
			fullName: test.full_name,
			browser: test.browser,
			environment: test.environment,
			elapsedTime: test.test_elapsed_time,
			setName: test.set_name,
			result: test.result,
			urlToTest: urlToTest,
			static: global.static
		});
		if(test.set_name.length > 0 && !DetailTable.hasSetNameColumn){
		    DetailTable.hasSetNameColumn = true;
		}
		TestRenderer.queueTest(testRow);
		return testRow
	}

    this.updateTest = function(oldTest, newTest){
        let testRow = DetailTable.getTestRow(newTest.test_set);
		if(oldTest.result != newTest.result){
		    let resultString = `${Main.Utils.getResultIcon(newTest.result)} ${newTest.result}`;
		    testRow.find('.test-result').html(resultString);
		    testRow.attr('result', newTest.result);
		    DetailTable.updateColumnHeaderFilterOptions('result', newTest.result);
		}
		if(oldTest.browser != newTest.browser){
		    testRow.find('.test-browser').html(newTest.browser);
		    DetailTable.updateColumnHeaderFilterOptions('browser', newTest.browser);
		}
		if(oldTest.environment != newTest.environment){
		    testRow.find('.test-environment').html(newTest.environment);
		    DetailTable.updateColumnHeaderFilterOptions('environment', newTest.environment);
		}
		if(oldTest.test_elapsed_time != newTest.test_elapsed_time){
		    testRow.find('.test-time').html(ExecutionReport.formatTimeOutput(newTest.test_elapsed_time));
		}
		if(oldTest.set_name != newTest.set_name){
		    DetailTable.hasSetNameColumn = true;
			DetailTable.displaySetNameColumn();
			testRow.find('.set-name').html(newTest.set_name.toString());
			DetailTable.updateColumnHeaderFilterOptions('set-name', newTest.set_name);

		}
		if(oldTest.module != newTest.module){
		    let module = newTest.module.length > 0 ? newTest.module : '';
		    DetailTable.updateColumnHeaderFilterOptions('module', module);
		}
	}

	this.updateTestDetail = function(testFullName, testSet){
	    let _loadTest = function(testDetail){
	        let detailPanel = $(`#${testSet}Collapse`);
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
            loadLogs(testDetail.info_log, logPanel.find('.info-log'));
            loadLogs(testDetail.debug_log, logPanel.find('.debug-log'));

            let rightColumn = detailPanel.find('.detail-right-column');
            // add description
            let detailHasDescription = rightColumn.find('.detail-description').length > 0;
            if(testDetail.description && !detailHasDescription){
                let descriptionBox = $(
                    `<div class="detail-description test-detail-box">
                        <div class="test-detail-box-title">Description</div>
                        <div class="detail-description-value">${testDetail.description}</div>
                    </div>`);
                rightColumn.append(descriptionBox)
            }
            // update steps
            let stepBox = rightColumn.find('div.step-list');
            if(testDetail.steps.length > 0 && stepBox.length == 0){
                let stepBox = $(`
                    <div class="step-list test-detail-box">
                        <div class="test-detail-box-title">Steps</div>
                        <ol></ol>
                    </div>`);
                testDetail.steps.forEach(function(step){
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

	    if(global.static){
	        _loadTest(global.detailTestData[testSet])
	    }
	    else{
            $.ajax({
                url: "/api/report/test-set",
                data: {
                    project: global.project,
                    suite: global.suite,
                    execution: global.execution,
                    testName: testFullName,
                    testSet: testSet
                },
                dataType: 'json',
                contentType: 'application/json; charset=utf-8',
                type: 'GET',
                success: function( testDetail ) {
                    _loadTest(testDetail)
                    if(testDetail.result == 'pending' || testDetail.result == 'running' || testDetail.result == ''){
                        setTimeout(() => DetailTable.updateTestDetail(testFullName, testSet), 1500, testFullName, testSet);
                    }
                }
            });
        }
	}

	this.updateColumnHeaderFilterOptions = function(){
	    let columns = {
	        'module': [],
	        'browser': [],
	        'result': [],
	        'environment': [],
	        'set-name': []
	    }
	    let modules = Object.values(ExecutionReport.tests).map(value => value.module );
        modules = [...new Set(modules)];
        let index = modules.findIndex(x => x === "");
        if(index != -1){
            modules[index] = "-"
        }
        columns.module = modules;

	    let browsers = Object.values(ExecutionReport.tests).map(value => value.browser );
        columns.browser = [...new Set(browsers)];
        if(columns.browser.indexOf('') > -1){ columns.browser.splice(index, 1) }

        let results = Object.values(ExecutionReport.tests).map(value => value.result);
        columns.result = [...new Set(results)];
        if(columns.result.indexOf('') > -1){ columns.result.splice(index, 1) }

        let environments = Object.values(ExecutionReport.tests).map(value => value.environment);
        columns.environment = [...new Set(environments)];
        if(columns.environment.indexOf('') > -1){ columns.environment.splice(index, 1) }

        let setNames = Object.values(ExecutionReport.tests).map(value => value.set_name);
        columns['set-name'] = [...new Set(setNames)];
        if(columns['set-name'].indexOf('') > -1){ columns['set-name'].splice(index, 1) }

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
			if(checkedCheckboxes.length > 0){
				// mark this column header as 'filtered'
				thisColumnHeader.addClass('filtered');
				let checkedValues = [];
				checkedCheckboxes.each(function(i, checkbox){
				    let value = $(checkbox).attr('value')
				    if(value == '-'){ value = '' }
					checkedValues.push(value);
				});
				// for reach row
				testTableRows.each(function(){
					let thisRow = $(this);
					let thisCellValue = $(this).find('td').get(columnIndex).innerText;
					if(!checkedValues.includes(thisCellValue.trim())){
						thisRow.hide();
						let setName = thisRow.attr('test-set');
						DetailTable.getTestDetailRow(setName).hide()
					}
				})
			}
			else {
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

	// Expects the following data: testSet, fullName, module, name, result, urlToTest
	this.generateTestRow = function(data){
		let resultString = `${Main.Utils.getResultIcon(data.result)} ${data.result}`;
		let testDetailRow = DetailTable.generateTestDetailRow(data.name, data.fullName, data.testSet);
        var row = `
            <tr test-name="${data.name}" test-full-name="${data.fullName}" test-set="${data.testSet}" result="${data.result}" class="test-row cursor-pointer"
                    data-toggle="collapse" href="#${data.testSet}Collapse" aria-expanded="false">
                <td class="tc-number">${data.number}</td>
                <td class="tc-module">${data.module}</td>
                <td class="tc-name"><span class="cursor-auto">${data.name}</span></td>
                <td class="set-name">${data.setName}</td>
                <td class="test-environment">${data.environment}</td>
                <td class="test-browser">${data.browser}</td>
                <td class="test-result">${resultString}</td>
                <td class="test-time">${data.elapsedTime}</td>
                <td class="link" style="${ data.static ? 'display: None' : '' }">
                    <a href="${data.urlToTest}">
                        <span class="glyphicon glyphicon-new-window" aria-hidden="true"></span>
                    </a>
                </td>
            </tr>${testDetailRow}`;
        return row
    }

    this.generateTestDetailRow = function(testName, testFullName, testSet){
        let id = `${testSet}Collapse`;
        let onclick = "$(this).siblings().removeClass('active');$(this).addClass('active');"
        let row = `
            <tr test-name="${testName}" test-full-name="${testFullName}" test-set="${testSet}" class="test-detail-row">
                <td colspan="100%">
                    <div id="${id}" class="collapse row test-detail">
                        <div class="logs col-md-6 test-detail-box">
                            <div class="test-detail-box-title">
                                Logs &nbsp;
                                <a href="#${testSet}InfoLog" aria-controls="${testSet}InfoLog" class="active link-without-underline" role="tab"
                                    data-toggle="tab" onclick="${onclick}">info</a>
                                <a href="#${testSet}DebugLog" aria-controls="${testSet}DebugLog" class="link-without-underline" role="tab"
                                    data-toggle="tab" onclick="${onclick}">debug</a>
                            </div>
                            <div class="tab-content">
                                <div role="tabpanel" class="tab-pane info-log active" id="${testSet}InfoLog"></div>
                                <div role="tabpanel" class="tab-pane debug-log" id="${testSet}DebugLog"></div>
                            </div>
                        </div>
                        <div class='detail-right-column col-md-6'></div>
                    </div>
                </td>
            </tr>`;
        return row
    }

    this.displaySetNameColumn = function(){
        let detailTable = $("#detailTable");
        if(!detailTable.hasClass('set-name-displayed')){
            $("#detailTable").addClass('set-name-displayed')
        }
    }

    this.getTestRow = function(setName){
        return $(`tr.test-row[test-set='${setName}']`)
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
