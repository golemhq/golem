
var allTestCases = {};
var baseDelay = 2000;

var suiteFinished = false;
var netTime = undefined;

$(document).ready(function() {            
	getReportData();

	$("#generalTable").on('click', 'tr', function(){
		let moduleName = $(this).find("td.module").html();
		detailTable.filterDetailTableByModule(moduleName);
	})

	detailTable.instantiateDetailTableFilterListeners();
});


function getReportData(){
	$.post(
		"/report/get_execution_data/",
		{ 
			project: project,
			suite: suite,
			execution: execution,
		},
		function(executionData) {	
  			if(executionData.has_finished){
  				suiteFinished = true;
  				netTime = executionData.net_elapsed_time;
  			}
  			loadReport(executionData);
  		}
	);
	if(baseDelay <= 10000){
		baseDelay += 50;
	}
	if(!suiteFinished){
		setTimeout(function(){getReportData()}, baseDelay);
	}
}


function loadReport(execution_data){
	for(tc in execution_data.test_cases){
		var test = execution_data.test_cases[tc];
		var row = $("#"+test.test_set);
		if(row.length == 0){
			// this test case is not added yet
			addTestToDetailTable(test);
		}
		else if(row.attr('pending') == 'pending' && test.result != 'pending'){
			loadTestRowResult(test);
		}
	}
}

function addTestToDetailTable(test){
	
	var numbering = $("#detailTable tbody tr").length + 1;

	if(test.result == 'pass')
		var resultString = passIcon() + ' ' + test.result;
	else if(test.result == 'fail')
		var resultString = failIcon() + ' ' + test.result;
	else if(test.result == 'pending')
		var resultString = 'pending';

	var testRow = ExecutionsReport.generateTestRow({
		testSet: test.test_set,
		numbering: numbering,
		module: test.module,
		name: test.name,
		environment: test.env,
		//browser: test.browser,
		result: resultString,
		//elapsedTime: test.test_elapsed_time
	});

	var link = "/report/project/"+project+"/"+suite+"/"+execution+"/"+test.full_name+"/"+test.test_set+"/";
	testRow.attr('onclick', "document.location.href='"+link+"'");
	testRow.find('td.link a').attr('href', link)

	$("#detailTable tbody").append(testRow);

	//add this test case to allTestCases
	allTestCases[test.test_set] = test;

	if(test.result != 'pending'){
		loadTestRowResult(test);
	}

	// add options to header dropdowns
	detailTable.updateColumnHeaderFilterOptions('module', test.module);
	// detailTable.updateColumnHeaderFilterOptions('environment', test.environment);
	detailTable.updateColumnHeaderFilterOptions('browser', test.browser);
	detailTable.updateColumnHeaderFilterOptions('result', test.result);

	updateModuleRowInGeneralTable(test);
	refreshGeneralTable();
}


function loadTestRowResult(test){
	var row = $("#"+test.test_set);

	if(test.result == 'pass')
		var resultString = passIcon() + ' ' + test.result;
	else if(test.result == 'fail')
		var resultString = failIcon() + ' ' + test.result;

	row.find('.test-result').html(resultString);
	row.find('.test-browser').html(test.browser);
	row.find('.test-environment').html(test.environment);
	row.find('.test-time').html(formatTimeOutput(test.test_elapsed_time));
	if(test.set_name){
		ExecutionsReport.hasSetNameColumn = true;
		ExecutionsReport.addSetNameColumnToTable();
		row.find('.set-name').html(test.set_name);
		detailTable.updateColumnHeaderFilterOptions('set-name', test.set_name);
	}

	//add this test case to allTestCases
	allTestCases[test.test_set] = test;

	//refresh the general table
	refreshGeneralTable();

	//The module in the general table should be updated
	updateModuleRowInGeneralTable(test);

	// add options to header dropdowns
	detailTable.updateColumnHeaderFilterOptions('browser', test.browser);
	detailTable.updateColumnHeaderFilterOptions('result', test.result);
	detailTable.updateColumnHeaderFilterOptions('environment', test.environment);

	row.removeAttr('pending');
}


function updateModuleRowInGeneralTable(testCase){
	// does the row for the module already exists?
	var moduleRow = getModuleRow(testCase.module);
	if(moduleRow === null){
		// add a new row
		var moduleRow = ExecutionsReport.generateModuleRow({
			moduleName: testCase.module,
		});
		moduleRow.insertBefore("#totalRow");
	}
	var testsInModule = getTestsInModule(testCase.module); //testCasesByModule[module].length;
	var testsOkInModule = getTestsInModuleWithResult(testCase.module, 'pass');
	var testsFailedInModule = getTestsInModuleWithResult(testCase.module, 'fail');
	var timeInModule = getTotalModuleTime(testCase.module);

	moduleRow.find(".total-tests").html(testsInModule);
	moduleRow.find(".tests-ok").html(testsOkInModule);
	moduleRow.find(".tests-failed").html(testsFailedInModule);
	//moduleRow.find(".total-time").html(timeInModule + ' s');
	//moduleRow.find(".total-time").html('');

	var okPercentage = testsOkInModule * 100 / testsInModule;
	var failPercentage = testsFailedInModule * 100 / testsInModule + okPercentage;
	
	var okBar = moduleRow.find('.ok-bar');
	var failBar = moduleRow.find('.fail-bar');

	utils.animateProgressBar(okBar, okPercentage);
	utils.animateProgressBar(failBar, failPercentage);
}


function refreshGeneralTable(){
	// fill in total row
	var totalTestCases = getTotalTestCases();
	var totalTestsOk = getTotalTestsWithResult('pass');
	var totalTestsFailed = getTotalTestsWithResult('fail');
	//var totalTestsFailed = totalTestCases - totalTestsOk;
	var totalTime = getTotalTime();

	var totalRow = $("#totalRow");
	totalRow.find(".total-tests").html(totalTestCases);
	totalRow.find(".tests-ok").html(totalTestsOk);
	totalRow.find(".tests-failed").html(totalTestsFailed);
	totalRow.find(".total-time").html(formatTimeOutput(totalTime));
	if(netTime != undefined){
		totalRow.find(".net-time").html(formatTimeOutput(netTime));
	}
	
	var okPercentage = totalTestsOk * 100 / totalTestCases;
	var failPercentage = totalTestsFailed * 100 / totalTestCases + okPercentage;

	var okBar = totalRow.find('.ok-bar');
	var failBar = totalRow.find('.fail-bar');

	utils.animateProgressBar(okBar, okPercentage);
	utils.animateProgressBar(failBar, failPercentage);
}

function getTestsInModule(module){
	var tests = 0;
	for(t in allTestCases){
		if(allTestCases[t].module == module){
			tests++
		}
	}
	return tests
}


function getTestsInModuleWithResult(module, result){
	var totalOk = 0;
	for(t in allTestCases){
		if(allTestCases[t].module == module && allTestCases[t].result == result){
			totalOk++;
		}
	}
	return totalOk
}


function getTotalModuleTime(module){
	var totalTime = 0;
	for(t in allTestCases){
		if(allTestCases[t].module == module){
			totalTime += allTestCases[t].test_elapsed_time;
		}
	}
	return Math.round(totalTime * 100) / 100
}


function getTotalTestCases(){
	var size = 0, key;
    for (key in allTestCases) {
        if (allTestCases.hasOwnProperty(key)) size++;
    }
    return size;
}

function getTotalTestsWithResult(result){
	var totalOk = 0;
    for (key in allTestCases) {
        if (allTestCases[key].result == result) totalOk++;
    }
    return totalOk;
}

function getTotalTime(){
	var totalTime = 0;
	for(t in allTestCases){
		totalTime += allTestCases[t].test_elapsed_time;
	}
	return Math.round(totalTime * 100) / 100
}


function getModuleRow(module){
	var row = null;
	$("table.general-table tbody tr").each(function(){
		if($(this).find('td.module').html() == module){
			row = $(this)
		}
	});
	return row
}

function formatTimeOutput(seconds){
	var final = '';
	var min;
	var sec;
	var ms;
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


var detailTable = new function(){

	this.updateColumnHeaderFilterOptions = function(column, value){
		if([undefined, ''].includes(value)){
			return
		}
		let colHeader = $("#detailTable th[colname='"+column+"']");
		let optionList = colHeader.find("ul>form");
		let options = optionList.find("li>div.checkbox>label>span");
		let optionExists = false;
		options.each(function(){
			if($(this).html() == value){
				optionExists = true
			}
		});
		if(!optionExists){
			let newOption = "\
				<li>\
					<div class='checkbox'>\
				    	<label>\
				      		<input type='checkbox'> <span>"+value+"</span>\
				    	</label>\
			  		</div>\
				</li>";
			optionList.append(newOption);
			// show funnel icon
			colHeader.find('.funnel-icon').show();
		}
	}


	this.instantiateDetailTableFilterListeners = function(){
		$("#detailTable").on('change', "th input:checkbox", function(){
			detailTable.applyFilters()
		})
	}


	this.applyFilters = function(){
		// display all columns
		$("#detailTable tr").show();

		let tableRows = $("#detailTable>tbody>tr");

		// for each column header
		$("#detailTable th").each(function($index){
			let thisColumnHeader = $(this);
			let checkedCheckboxes = thisColumnHeader.find("input[type='checkbox']:checked");
			let columnIndex = $index;
			if(checkedCheckboxes.length > 0){
				// mark this column header as 'filtered'
				thisColumnHeader.addClass('filtered');

				let checkedValues = [];
				checkedCheckboxes.each(function(){
					checkedValues.push($(this).parent().find('span').html());
				});
				// for reach row
				tableRows.each(function(){
					let thisRow = $(this);
					let thisCellValue = $(this).find('td').get(columnIndex).innerText;
					if(!checkedValues.includes(thisCellValue.trim())){
						thisRow.hide();
					}
				})
			}
			else {
				// mark column header as not filtered
				thisColumnHeader.removeClass('filtered');
			}
		});
	}


	this.filterDetailTableByModule = function(moduleName){
		// remove all filters in module column,
		// apply the filter provided
		// keep any other filters
		let moduleColumnHeader = $("#detailTable th:contains('Module')");
		moduleColumnHeader.find('input:checkbox')
						  .prop('checked', false).change();
		if(moduleName != 'Total'){
			moduleColumnHeader.find(`div.checkbox label:contains('${moduleName}') input`)
						  	  .prop('checked', true).change();
		}
	}
}
