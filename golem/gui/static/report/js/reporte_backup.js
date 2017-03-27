var allTestCases = [];

$(document).ready(function() {            
	$.post(
		"/report/get_execution_data/",
		{ 
			project: project,
			suite: suite,
			execution: execution,
		},
		function( data ) {	
  			loadReport(data.execution_data);
  		}
	);
});


function loadReport(execution_data){
	loadDetailTable(execution_data.test_cases);
	loadGeneralTable(execution_data.test_cases);
}


function loadDetailTable(test_cases){
	var maxNumberOfSubModules = getMaxNumberOfSubModules(test_cases);
	if(maxNumberOfSubModules > 0){
		// append columns for submodules
		var newColsString = '';
		for(var i = 1; i <= maxNumberOfSubModules; i++){
			newColsString += '<th>' + 'Sub Module ' + i.toString() + '</th>';
		}
		$(newColsString).insertAfter("table.por-CP thead .module-col-header");
	}
	
	for(idx in test_cases){
		var testCase = test_cases[idx];

		console.log(testCase);

		var testCaseRow = $("table.por-CP .primera-fila").clone().removeClass('primera-fila');

		testCaseRow.find("td.tc-number").html(parseInt(idx) + 1);
		if(testCase.module.length > 0){
			testCaseRow.find("td.tc-module").html(testCase.module);	
		}
		else{
			testCaseRow.find("td.tc-module").html('-');	
		}
		if(maxNumberOfSubModules > 0){
			var newColsString = '';
			for(var i = 1; i <= maxNumberOfSubModules; i++){
				if(testCase.sub_modules[i-1] != undefined){
					newColsString += '<td class\"tc-submodule\">'+testCase.sub_modules[i-1]+'</td>';
				}
				else{
					newColsString += '<td class\"tc-submodule\"></td>';
				}
			}
			$(newColsString).insertAfter(testCaseRow.find("td.tc-module"));
		}
		testCaseRow.find("td.tc-name").html(testCase.name);
		testCaseRow.find("td.tc-result").html(testCase.result);
		testCaseRow.find("td.tc-time").html(testCase.test_elapsed_time);
		testCaseRow.find("td.tc-reporte").html(
			"<a target='_blank' href='/report/project/"+project+"/"+suite+"/"+execution+"/"+testCase.full_name+"/"+testCase.test_set+"'>See Report</a>");		
		//testCaseRow.find("td.tcp-log");

		$("table.por-CP tbody").append(testCaseRow);
	}
}


function loadGeneralTable(testCases){
	var testCasesByModule = {}

	// group test cases by module
	for(t in testCases){
		if(!testCasesByModule[testCases[t].module]){
			testCasesByModule[testCases[t].module] = [];
		}
		testCasesByModule[testCases[t].module].push(testCases[t])
	}
	var index = 1;
	var totalTestCases = 0;
	var totalTestsOk = 0;
	var totalTestsFailed = 0;
	var totalTime = 0;
	for(module in testCasesByModule){
		var moduleRow = $("table.por-modulo .primera-fila").clone().removeClass('primera-fila');
		var testsInModule = testCasesByModule[module].length;
		var testsOkInModule = getTotalTestsOkInModule(testCasesByModule[module]);
		var testsFailedInModule = testsInModule - testsOkInModule;
		var timeInModule = getTotalModuleTime(testCasesByModule[module]);
		console.log(timeInModule);
		totalTestCases += testsInModule;
		totalTestsOk += testsOkInModule;
		totalTestsFailed += totalTestsFailed;
		totalTime += timeInModule;

		moduleRow.find(".module-number").html(index);
		moduleRow.find(".module").html(module);
		moduleRow.find(".total-tests").html(testsInModule);
		moduleRow.find(".tests-ok").html(testsOkInModule);
		moduleRow.find(".tests-failed").html(testsFailedInModule);
		moduleRow.find(".total-time").html(timeInModule);

		var okPercentage = testsOkInModule * 100 / testsInModule;
		var barra_azul = moduleRow.find('.barra-azul');
		var id = new Date().getTime() + Math.random().toString(36).substring(7);
		barra_azul.attr('id', id);
  		barra_azul.attr('data-transitiongoal', okPercentage);

		moduleRow.insertBefore("#totalRow");
		
		setTimeout(animateProgressBar, 10, id);

		index += 1;
	}

	// fill in total row
	var totalRow = $("#totalRow");
	totalRow.find(".total-tests").html(totalTestCases);
	totalRow.find(".tests-ok").html(totalTestsOk);
	totalRow.find(".tests-failed").html(totalTestsFailed);
	console.log(totalTime)
	totalRow.find(".total-time").html(totalTime);
	
	var okPercentage = totalTestsOk * 100 / totalTestCases;
	var barra_azul = totalRow.find('.barra-azul');
	var id = new Date().getTime() + Math.random().toString(36).substring(7);
	barra_azul.attr('id', id);
	barra_azul.attr('data-transitiongoal', okPercentage);
	setTimeout(animateProgressBar, 10, id);
}

function animateProgressBar(id){
	var goal = $("#"+id).attr('data-transitiongoal');
	$("#"+id).css('width', goal + '%');
}


function getMaxNumberOfSubModules(testCases){
	var maxAmount = 0;
	for(t in testCases){
		if(testCases[t].sub_modules.length > maxAmount){
			maxAmount = testCases[t].sub_modules.length;
		}
	}
	return maxAmount
}


function getTotalTestsOkInModule(module){
	var totalOk = 0;
	for(t in module){
		if(module[t].result == 'pass'){
			totalOk += 1;
		}
	}
	return totalOk
}


function getTotalModuleTime(module){
	var totalTime = 0;
	for(t in module){
		totalTime += module[t].test_elapsed_time;
	}
	return Math.round(totalTime * 100) / 100
}