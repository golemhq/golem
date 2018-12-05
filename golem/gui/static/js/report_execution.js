
$(document).ready(function(){            
	ExecutionReport.getReportData();

	$("#generalTable").on('click', 'tr', function(){
		let moduleName = $(this).find("td[data='module']").html();
		DetailTable.filterDetailTableByModule(moduleName);
	})

	DetailTable.instantiateDetailTableFilterListeners();
});


const ExecutionReport = new function(){

	this.suiteFinished = false;
	this.queryDelay = 2000;
	this.netTime = undefined;
	this.tests = {};

	this.getReportData = function(){
		 $.ajax({
            url: "/report/get_execution_data/",
            data: {
                project: project,
                suite: suite,
                execution: execution
            },
            dataType: 'json',
            type: 'GET',
            success: function(executionData) {
	  			if(executionData.has_finished){
	  				ExecutionReport.suiteFinished = true;
	  				ExecutionReport.netTime = executionData.net_elapsed_time;
	  			}
	  			ExecutionReport.loadReport(executionData);
				if(ExecutionReport.suiteFinished){
                    $(".spinner").hide()
				}
				else{
				    $(".spinner").show()
					if(ExecutionReport.queryDelay <= 10000){
						ExecutionReport.queryDelay += 50;
					}
					setTimeout(function(){ExecutionReport.getReportData()}, ExecutionReport.queryDelay);
				}
	  		}
        });
	}

	this.loadReport = function(execution_data){
		for(tc in execution_data.tests){
			let test = execution_data.tests[tc];
			let row = $(`#${test.test_set}`);
			if(row.length == 0){
				// this test is not added yet
				DetailTable.addTestToDetailTable(test);
			}
			else if(row.attr('pending') == 'pending' && test.result != 'pending'){
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
		'success',
		'failure'
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
        	if(result != 'pending'){
                // does the Detail Table has column for this test result?
                // pending does not have its own column
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
		let numbering = $("#detailTable tbody tr").length + 1;
		let urlToTest = `/report/project/${project}/${suite}/${execution}/${test.full_name}/${test.test_set}/`;
		let testRow = DetailTable.generateTestRow({
			testSet: test.test_set,
			numbering: numbering,
			module: test.module,
			name: test.name,
			result: 'pending',
			urlToTest: urlToTest
		});
		$("#detailTable tbody").append(testRow);
		ExecutionReport.tests[test.test_set] = test;
		if(test.result != 'pending'){
			DetailTable.loadTestRowResult(test);
		}
		// add options to header dropdowns
		DetailTable.updateColumnHeaderFilterOptions('module', test.module);
		DetailTable.updateColumnHeaderFilterOptions('browser', test.browser);
		DetailTable.updateColumnHeaderFilterOptions('result', test.result);
		// update general table
		GeneralTable.updateGeneralTable(test.module);
	}

	this.loadTestRowResult = function(test){
		let row = $(`#${test.test_set}`);
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
		row.removeAttr('pending');
	}

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
			DetailTable.applyFilters()
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

	// Expects the following data: testSet, numbering, module, name, result, urlToTest
	this.generateTestRow = function(data){
		let setNameStyle = DetailTable.hasSetNameColumn ? '' : 'display: none';
        var row = `
    <tr id="${data.testSet}" pending="pending" class="cursor-pointer" onclick="document.location.href='${data.urlToTest}'">
        <td class="tc-number">${data.numbering}</td>
        <td class="tc-module">${data.module}</td>
        <td class="tc-name">${data.name}</td>
        <td class="set-name" style="${setNameStyle}"></td>
        <td class="test-environment"></td>
        <td class="test-browser"></td>
        <td class="test-result">${data.result}</td>
        <td class="test-time"></td>
        <td class="link">
        	<a href="${data.urlToTest}" target="blank">
            	<span class="glyphicon glyphicon-new-window" aria-hidden="true"></span>
        	</a>
        </td>
    </tr>`;
        return $(row)
    }

    this.displaySetNameColumn = function(){
        $("#detailTable th[colname='set-name'").show();
        $("#detailTable tr").each(function(i, row){
            $(row).find(".set-name").show();
        })
    }
}
