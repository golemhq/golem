
$(document).ready(function(){
    if(global.executionData == null){
        ExecutionReport.getReportData();
    }
    else{
	    ExecutionReport.suiteFinished = true;
        ExecutionReport.netTime = global.executionData.net_elapsed_time;
        $(".spinner").hide()
        ExecutionReport.loadReport(global.executionData);
    }

	$("#generalTable").on('click', 'tr', function(){
		let moduleName = $(this).find("td[data='module']").html();
		if(moduleName.length == 0){moduleName = '-'}
		DetailTable.filterDetailTableByModule(moduleName);
	})

	DetailTable.instantiateDetailTableFilterListeners();
});


const ExecutionReport = new function(){

	this.suiteFinished = false;
	this.queryDelay = 1500;
	this.netTime = undefined;
	this.tests = {};

	this.getReportData = function(){
		 $.ajax({
            url: "/report/get_execution_data/",
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
	  		}
        });
	}

	this.loadReport = function(execution_data){
		for(tc in execution_data.tests){
			let test = execution_data.tests[tc];
			let row = DetailTable.getTestRow(test.test_set);
			if(row.length == 0){
				// this test is not added yet
				DetailTable.addTestToDetailTable(test);
			}
			let rowResult = row.attr('result');
            if(test.result != rowResult){
                DetailTable.loadTestRowResult(test);
            }
		}
	}

	this.getTestsInModule = function(module){
		let tests = [];
		for(t in ExecutionReport.tests){
			if(ExecutionReport.tests[t].module == module){
				tests.push(ExecutionReport.tests[t]);
			}
		}
		return tests
	}

	this.getTestsInModuleWithResult = function(module, result){
		var totalOk = 0;
		for(t in ExecutionReport.tests){
			let matchModule = ExecutionReport.tests[t].module == module;
			let matchResult = ExecutionReport.tests[t].result == result;
			if(matchModule && matchResult){
				totalOk++;
			}
		}
		return totalOk
	}

	this.getTotalModuleTime = function(module){
		var totalTime = 0;
		for(t in ExecutionReport.tests){
			if(ExecutionReport.tests[t].module == module){
				totalTime += ExecutionReport.tests[t].test_elapsed_time;
			}
		}
		return Math.round(totalTime * 100) / 100
	}

	this.getTotalTestAmount = function(){
	    return Object.keys(ExecutionReport.tests).length;
	}

	this.getTotalTestsWithResult = function(result){
		let total = 0;
	    for (key in ExecutionReport.tests) {
	        if (ExecutionReport.tests[key].result == result) total++;
	    }
	    return total;
	}

	this.getTotalTime = function(){
		var totalTime = 0;
		for(t in ExecutionReport.tests){
			totalTime += ExecutionReport.tests[t].test_elapsed_time;
		}
		return Math.round(totalTime * 100) / 100
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

	this.updateGeneralTable = function(module){
		GeneralTable.updateModuleRow(module);
		GeneralTable.refreshTotalRow();
	}

	this.updateModuleRow = function(module){
		// does the row for the module already exists?
		let moduleRow = GeneralTable.getModuleRow(module);
		if(moduleRow === null){
			moduleRow = GeneralTable.addModuleRow(module);
		}
		let testsInModule = ExecutionReport.getTestsInModule(module);
		let moduleTotalsByResult = {};
		testsInModule.forEach(function(test){
			if(!Object(moduleTotalsByResult).hasOwnProperty(test.result)){
				moduleTotalsByResult[test.result] = 0;
			}
			moduleTotalsByResult[test.result] += 1;
        });
        let container = moduleRow.find("td[data='percentage']>div.progress");
        Object.keys(moduleTotalsByResult).forEach(function(result){
        	if(result != 'pending' && result != 'running'){
                // does the Detail Table has column for this test result?
                // pending and running do not have their own columns
                if(!GeneralTable.hasColumnForResult(result)){
                    GeneralTable.addColumnForResult(result)
                }
                // update column value for this result
                moduleRow.find(`td[data='result'][result='${result}']`).html(moduleTotalsByResult[result]);
        	}
        	if(!Main.ReportUtils.hasProgressBarForResult(container, result)){
        		Main.ReportUtils.createProgressBars(container, [result])
        	}
            let percentage = moduleTotalsByResult[result] * 100 / testsInModule.length;
        	Main.ReportUtils.animateProgressBar(container, result, percentage)
        })
		let timeInModule = ExecutionReport.getTotalModuleTime(module);
		moduleRow.find("td[data='total-tests']").html(testsInModule.length);
		moduleRow.find("td[data='total-time']").html(ExecutionReport.formatTimeOutput(timeInModule));
		// if(ExecutionReport.netTime != undefined){
		// 	totalRow.find("td[data='net-time']").html(ExecutionReport.formatTimeOutput(ExecutionReport.netTime));
		// }

		// check if pending progress bar is stale
		let moduleHasPending = 'pending' in moduleTotalsByResult;
		if(!moduleHasPending){
            Main.ReportUtils.animateProgressBar(container, 'pending', 0)
		}
		// check if running progress bar is stale
		let moduleHasRunning = 'running' in moduleTotalsByResult;
		if(!moduleHasRunning){
            Main.ReportUtils.animateProgressBar(container, 'running', 0)
		}
	}

	this.refreshTotalRow = function(){
		// fill in total row
		let totalTestAmount = ExecutionReport.getTotalTestAmount();
		let totalTime = ExecutionReport.getTotalTime();
		let totalRow = $("#totalRow");
		totalRow.find("td[data='total-tests']").html(totalTestAmount);
		totalRow.find("td[data='total-time']").html(ExecutionReport.formatTimeOutput(totalTime));
		if(ExecutionReport.netTime != undefined){
			totalRow.find("td[data='net-time']").html(ExecutionReport.formatTimeOutput(ExecutionReport.netTime));
		}
		let totalsByResult = {};
		Object.keys(ExecutionReport.tests).forEach(function(testSet){
			let test = ExecutionReport.tests[testSet];
			if(!Object(totalsByResult).hasOwnProperty(test.result)){
				totalsByResult[test.result] = 0;
			}
			totalsByResult[test.result] += 1;
        });
        let container = totalRow.find("td[data='percentage']>div.progress");
		Object.keys(totalsByResult).forEach(function(result){
			if(result != 'pending'){
                totalRow.find(`td[data='result'][result='${result}']`).html(totalsByResult[result]);
        	}
        	if(!Main.ReportUtils.hasProgressBarForResult(container, result)){
        		Main.ReportUtils.createProgressBars(container, [result])
        	}
            let percentage = totalsByResult[result] * 100 / totalTestAmount;
        	Main.ReportUtils.animateProgressBar(container, result, percentage)
        })
        // check if pending progress bar is stale
		let totalsHasPending = 'pending' in totalsByResult;
		if(!totalsHasPending ){
            Main.ReportUtils.animateProgressBar(container, 'pending', 0)
		}
		// check if running progress bar is stale
		let moduleHasRunning = 'running' in totalsByResult;
		if(!moduleHasRunning){
            Main.ReportUtils.animateProgressBar(container, 'running', 0)
		}
	}

	this.addModuleRow = function(module){
		let moduleRow = GeneralTable.generateModuleRow({moduleName: module});
		moduleRow.insertBefore("#totalRow");
		return moduleRow
	}

	this.getModuleRow = function(module){
		let moduleRow = null;
		$("table.general-table tbody tr").each(function(i, row){
			if($(row).find("td[data='module']").html() == module){
				moduleRow = $(row)
			}
		});
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
            <tr class="general-table-row cursor-pointer">
                <td data="module">${data.moduleName}</td>
                <td data="total-tests">${data.totalTests}</td>
        		${resultColumns}        
                <td data="percentage"><div class='progress'></div></td>\
                <td data="total-time"></td>\
                <td data="net-time"></td>\
            </tr>`;
        return $(row)
    }
}


const DetailTable = new function(){

	this.hasSetNameColumn = false;

	this.addTestToDetailTable = function(test){
		let urlToTest = `/report/project/${global.project}/${global.suite}/${global.execution}/${test.full_name}/${test.test_set}/`;
		let testRow = DetailTable.generateTestRow({
			testSet: test.test_set,
			module: test.module,
			name: test.name,
			fullName: test.full_name,
			result: 'pending',
			urlToTest: urlToTest,
			static: global.static
		});
		let testDetailRow = DetailTable.generateTestDetailRow(test.name, test.full_name, test.test_set);
		$("#detailTable tbody").append(testRow);
		$("#detailTable tbody").append(testDetailRow);
		DetailTable.updateNumbering();
		ExecutionReport.tests[test.test_set] = test;
		GeneralTable.updateGeneralTable(test.module);
	}

	this.loadTestRowResult = function(test){
		let row = DetailTable.getTestRow(test.test_set);
		let resultString = Main.Utils.getResultIcon(test.result) + ' ' + test.result;		
		row.find('.test-result').html(resultString);
		row.find('.test-browser').html(test.browser);
		row.find('.test-environment').html(test.environment);
		row.find('.test-time').html(ExecutionReport.formatTimeOutput(test.test_elapsed_time));
		if(test.set_name){
			DetailTable.hasSetNameColumn = true;
			DetailTable.displaySetNameColumn();
			row.find('.set-name').html(test.set_name.toString());
			DetailTable.updateColumnHeaderFilterOptions('set-name', test.set_name);
		}
		ExecutionReport.tests[test.test_set] = test;
		GeneralTable.updateGeneralTable(test.module);
		// add options to header dropdowns
		DetailTable.updateColumnHeaderFilterOptions('browser', test.browser);
		DetailTable.updateColumnHeaderFilterOptions('result', test.result);
		DetailTable.updateColumnHeaderFilterOptions('environment', test.environment);
		let module = test.module.length > 0 ? test.module : '';
		DetailTable.updateColumnHeaderFilterOptions('module', module);
		row.attr('result', test.result);
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
                        logContainer.append(`<div class='log-line'>${line}</div>`);
                    }
                });
            }
            loadLogs(testDetail.info_log, logPanel.find('.info-log'));
            loadLogs(testDetail.debug_log, logPanel.find('.debug-log'));

            let rightColumn = detailPanel.find('.detail-right-column');
            // add description
            let detailHasDescription = rightColumn.find('.detail-description').length > 0;
            if(testDetail.description.length > 0 && !detailHasDescription){
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
                        stepContent.append(' - ' + step.error.message)
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
                url: "/report/get_test_set_detail/",
                data: {
                    project: global.project,
                    suite: global.suite,
                    execution: global.execution,
                    testFullName: testFullName,
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

	this.updateColumnHeaderFilterOptions = function(column, value){
		if(column == 'module' && value == ''){ value = '-' }
		if(value == undefined || value == ''){ return }
		let colHeader = $(`#detailTable th[colname='${column}']`);
		let optionList = colHeader.find("ul>form");
		let options = optionList.find("li>div.checkbox>label>span");
		let optionExists = false;
		options.each(function(){
			if($(this).html() == value){
				optionExists = true
			}
		});
		if(!optionExists){
			let newOption = `
				<li>
				    <div class="checkbox"><label><input type="checkbox" value="${value}"> <span>${value}</span></label></div>
				</li>`;
			optionList.append(newOption);
		}
		// show funnel icon if there are two or more options
		if(options.length > 1){ colHeader.find('.funnel-icon').show() }
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
		// remove all filters in module column,
		// apply the filter provided
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
		let setNameStyle = DetailTable.hasSetNameColumn ? '' : 'display: none';
        var row = $(`
    <tr test-name="${data.name}" test-full-name="${data.fullName}" test-set="${data.testSet}" result="${data.result}" class="test-row cursor-pointer"
            data-toggle="collapse" href="#${data.testSet}Collapse" aria-expanded="false">
        <td class="tc-number"></td>
        <td class="tc-module">${data.module}</td>
        <td class="tc-name">${data.name}</td>
        <td class="set-name" style="${setNameStyle}"></td>
        <td class="test-environment"></td>
        <td class="test-browser"></td>
        <td class="test-result">${data.result}</td>
        <td class="test-time"></td>
        <td class="link" style="${ data.static ? 'display: None' : '' }">
        	<a href="${data.urlToTest}">
            	<span class="glyphicon glyphicon-new-window" aria-hidden="true"></span>
        	</a>
        </td>
    </tr>`);
        row.find('.link>a').on('click', function (e) {
            e.stopPropagation();
        });
        return row
    }

    this.generateTestDetailRow = function(testName, testFullName, testSet){
        let id = `${testSet}Collapse`;
        let onclick = "$(this).siblings().removeClass('active');$(this).addClass('active');"
        let row = $(`
            <tr test-name="${testName}" test-full-name="${testFullName}" test-set="${testSet}" class="test-detail-row">
                <td colspan="100%">
                    <div id="${id}" class="collapse row test-detail">
                        <div class="logs col-md-6 test-detail-box">
                            <div class="test-detail-box-title">
                                Logs
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
            </tr>`);
        row.find('div').on('show.bs.collapse', function () {
            DetailTable.updateTestDetail(testFullName, testSet)
        })
        return row
    }

    this.displaySetNameColumn = function(){
        $("#detailTable th[colname='set-name'").show();
        $("#detailTable tr").each(function(i, row){
            $(row).find(".set-name").show();
        })
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
