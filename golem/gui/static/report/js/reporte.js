
var allTestCases = {};
var maxNumberOfSubModules = 0;
var baseDelay = 2000;


$(document).ready(function() {            
	getReportData();
});


function getReportData(){

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

	if(baseDelay <= 10000){
		baseDelay += 50;
	}

	setTimeout(function(){
		getReportData()
	}, baseDelay);
}


function loadReport(execution_data){
	//loadDetailTable(execution_data.test_cases);
	//loadGeneralTable(execution_data.test_cases);


	for(tc in execution_data.test_cases){
		addTestCaseToDetailTable(execution_data.test_cases[tc]);
	}
}


// function loadDetailTable(test_cases){
// 	var maxNumberOfSubModules = getMaxNumberOfSubModules(test_cases);
// 	if(maxNumberOfSubModules > 0){
// 		// append columns for submodules
// 		var newColsString = '';
// 		for(var i = 1; i <= maxNumberOfSubModules; i++){
// 			newColsString += '<th>' + 'Sub Module ' + i.toString() + '</th>';
// 		}
// 		$(newColsString).insertAfter("table.por-CP thead .module-col-header");
// 	}

// 	for(idx in test_cases){
// 		var testCase = test_cases[idx];

// 		var testCaseRow = $("table.por-CP .primera-fila").clone().removeClass('primera-fila');

// 		testCaseRow.find("td.tc-number").html(parseInt(idx) + 1);
// 		if(testCase.module.length > 0){
// 			testCaseRow.find("td.tc-module").html(testCase.module);	
// 		}
// 		else{
// 			testCaseRow.find("td.tc-module").html('-');	
// 		}
// 		if(maxNumberOfSubModules > 0){
// 			var newColsString = '';
// 			for(var i = 1; i <= maxNumberOfSubModules; i++){
// 				if(testCase.sub_modules[i-1] != undefined){
// 					newColsString += '<td class\"tc-submodule\">'+testCase.sub_modules[i-1]+'</td>';
// 				}
// 				else{
// 					newColsString += '<td class\"tc-submodule\"></td>';
// 				}
// 			}
// 			$(newColsString).insertAfter(testCaseRow.find("td.tc-module"));
// 		}
// 		testCaseRow.find("td.tc-name").html(testCase.name);
// 		testCaseRow.find("td.tc-result").html(testCase.result);
// 		testCaseRow.find("td.tc-time").html(testCase.test_elapsed_time);
// 		testCaseRow.find("td.tc-reporte").html(
// 			"<a target='_blank' href='/report/project/"+project+"/"+suite+"/"+execution+"/"+testCase.full_name+"/"+testCase.test_set+"'>See Report</a>");		
// 		//testCaseRow.find("td.tcp-log");

// 		$("table.por-CP tbody").append(testCaseRow);
// 	}
// }


// function loadGeneralTable(testCases){
// 	var testCasesByModule = {}

// 	// group test cases by module
// 	for(t in testCases){
// 		if(!testCasesByModule[testCases[t].module]){
// 			testCasesByModule[testCases[t].module] = [];
// 		}
// 		testCasesByModule[testCases[t].module].push(testCases[t])
// 	}
// 	var index = 1;
// 	var totalTestCases = 0;
// 	var totalTestsOk = 0;
// 	var totalTestsFailed = 0;
// 	var totalTime = 0;
// 	for(module in testCasesByModule){
// 		var moduleRow = $("table.por-modulo .primera-fila").clone().removeClass('primera-fila');
// 		var testsInModule = testCasesByModule[module].length;
// 		var testsOkInModule = getTotalTestsOkInModule(testCasesByModule[module]);
// 		var testsFailedInModule = testsInModule - testsOkInModule;
// 		var timeInModule = getTotalModuleTime(testCasesByModule[module]);
// 		totalTestCases += testsInModule;
// 		totalTestsOk += testsOkInModule;
// 		totalTestsFailed += totalTestsFailed;
// 		totalTime += timeInModule;

// 		moduleRow.find(".module-number").html(index);
// 		moduleRow.find(".module").html(module);
// 		moduleRow.find(".total-tests").html(testsInModule);
// 		moduleRow.find(".tests-ok").html(testsOkInModule);
// 		moduleRow.find(".tests-failed").html(testsFailedInModule);
// 		moduleRow.find(".total-time").html(timeInModule);

// 		var okPercentage = testsOkInModule * 100 / testsInModule;
// 		var barra_azul = moduleRow.find('.barra-azul');
// 		var id = new Date().getTime() + Math.random().toString(36).substring(7);
// 		barra_azul.attr('id', id);
//   		barra_azul.attr('data-transitiongoal', okPercentage);

// 		moduleRow.insertBefore("#totalRow");
		
// 		setTimeout(animateProgressBar, 10, id);

// 		index += 1;
// 	}

// 	// fill in total row
// 	var totalRow = $("#totalRow");
// 	totalRow.find(".total-tests").html(totalTestCases);
// 	totalRow.find(".tests-ok").html(totalTestsOk);
// 	totalRow.find(".tests-failed").html(totalTestsFailed);
// 	totalRow.find(".total-time").html(totalTime);
	
// 	var okPercentage = totalTestsOk * 100 / totalTestCases;
// 	var barra_azul = totalRow.find('.barra-azul');
// 	var id = new Date().getTime() + Math.random().toString(36).substring(7);
// 	barra_azul.attr('id', id);
// 	barra_azul.attr('data-transitiongoal', okPercentage);
// 	setTimeout(animateProgressBar, 10, id);
// }





// ===================





function addTestCaseToDetailTable(testCase){
	// is this test case already added to the table?
	if(allTestCases[testCase.test_set] == undefined ){
		// this test case is not added yet

		var testCaseRow = $("table.por-CP .primera-fila").clone().removeClass('primera-fila');

		var numbering = $(".table.por-CP tbody tr").length;
		testCaseRow.find("td.tc-number").html(numbering);

		if(testCase.module.length > 0){
			testCaseRow.find("td.tc-module").html(testCase.module);	
		}
		else{
			testCaseRow.find("td.tc-module").html('-');	
		}

		if(testCase.result === 'pass'){
			var resultString = passIcon() + ' ' +testCase.result;
		}
		else if(testCase.result == 'fail'){
			var resultString = failIcon() + ' ' + testCase.result;	
		}

		testCaseRow.find("td.tc-name").html(testCase.name);
		testCaseRow.find("td.tc-browser").html(testCase.browser);
		testCaseRow.find("td.tc-result").html(resultString);
		testCaseRow.find("td.tc-time").html(testCase.test_elapsed_time + ' s');
		testCaseRow.find("td.tc-reporte").html(
			"<a href='/report/project/"+project+"/"+suite+"/"+execution+"/"+testCase.full_name+"/"+testCase.test_set+"'>See Report</a>");


		$("table.por-CP tbody").append(testCaseRow);

		// add this test case to allTestCases
		allTestCases[testCase.test_set] = testCase;

		// refresh the general table
		refreshGeneralTable();

		// The module in the general table should be updated
		updateModuleRowInGeneralTable(testCase);
	}	
}



function updateModuleRowInGeneralTable(testCase){
	// does the row for the module already exists?
	var moduleRowExists = moduleRowAlreadyExists(testCase.module);
	if(!moduleRowExists){
		// I have to add the row

		var moduleRow = $("table.por-modulo .primera-fila").clone().removeClass('primera-fila');
		var testsInModule = getTestsInModule(testCase.module); //testCasesByModule[module].length;
		var testsOkInModule = getTotalTestsOkInModule(testCase.module);
		var testsFailedInModule = testsInModule - testsOkInModule;
		var timeInModule = getTotalModuleTime(testCase.module);

		//moduleRow.find(".module-number").html(numbering);
		moduleRow.find(".module").html(testCase.module);
		moduleRow.find(".total-tests").html(testsInModule);
		moduleRow.find(".tests-ok").html(testsOkInModule);
		moduleRow.find(".tests-failed").html(testsFailedInModule);
		moduleRow.find(".total-time").html(timeInModule + 's');

		var okPercentage = testsOkInModule * 100 / testsInModule;
		var barra_azul = moduleRow.find('.barra-azul');
		var id = new Date().getTime() + Math.random().toString(36).substring(7);
		barra_azul.attr('id', id);
  		barra_azul.attr('data-transitiongoal', okPercentage);

		moduleRow.insertBefore("#totalRow");

		//refreshNumbering();
		
		setTimeout(animateProgressBar, 200, id);
	}
	else{
		// the row already exists, find it
		var row = getModuleRow(testCase.module);

		var testsInModule = getTestsInModule(testCase.module); //testCasesByModule[module].length;
		var testsOkInModule = getTotalTestsOkInModule(testCase.module);
		var testsFailedInModule = testsInModule - testsOkInModule;
		var timeInModule = getTotalModuleTime(testCase.module);

		row.find(".module").html(testCase.module);
		row.find(".total-tests").html(testsInModule);
		row.find(".tests-ok").html(testsOkInModule);
		row.find(".tests-failed").html(testsFailedInModule);
		row.find(".total-time").html(timeInModule + ' s');

		var okPercentage = testsOkInModule * 100 / testsInModule;
		var barra_azul = row.find('.barra-azul');
		var id = new Date().getTime() + Math.random().toString(36).substring(7);
		barra_azul.attr('id', id);
  		barra_azul.attr('data-transitiongoal', okPercentage);

  		setTimeout(animateProgressBar, 200, id);
	}
}


function refreshGeneralTable(){
	// var testCasesByModule = {}

	// // group test cases by module
	// for(t in allTestCases){
	// 	if(!testCasesByModule[allTestCases[t].module]){
	// 		testCasesByModule[allTestCases[t].module] = [];
	// 	}
	// 	testCasesByModule[allTestCases[t].module].push(allTestCases[t])
	// }
	// var index = 1;
	// for(module in testCasesByModule){
	// 	var moduleRow = $("table.por-modulo .primera-fila").clone().removeClass('primera-fila');
	// 	var testsInModule = testCasesByModule[module].length;
	// 	var testsOkInModule = getTotalTestsOkInModule(testCasesByModule[module]);
	// 	var testsFailedInModule = testsInModule - testsOkInModule;
	// 	var timeInModule = getTotalModuleTime(testCasesByModule[module]);
	// 	//totalTestCases += testsInModule;
	// 	//totalTestsOk += testsOkInModule;
	// 	//totalTestsFailed += totalTestsFailed;
	// 	//totalTime += timeInModule;

	// 	moduleRow.find(".module-number").html(index);
	// 	moduleRow.find(".module").html(module);
	// 	moduleRow.find(".total-tests").html(testsInModule);
	// 	moduleRow.find(".tests-ok").html(testsOkInModule);
	// 	moduleRow.find(".tests-failed").html(testsFailedInModule);
	// 	moduleRow.find(".total-time").html(timeInModule);

	// 	var okPercentage = testsOkInModule * 100 / testsInModule;
	// 	var barra_azul = moduleRow.find('.barra-azul');
	// 	var id = new Date().getTime() + Math.random().toString(36).substring(7);
	// 	barra_azul.attr('id', id);
 //  		barra_azul.attr('data-transitiongoal', okPercentage);

	// 	moduleRow.insertBefore("#totalRow");
		
	// 	setTimeout(animateProgressBar, 10, id);

	// 	index += 1;
	// }

	// fill in total row
	var totalTestCases = getTotalTestCases();
	var totalTestsOk = getTotalTestsOk();
	var totalTestsFailed = totalTestCases - totalTestsOk;
	var totalTime = getTotalTime();

	var totalRow = $("#totalRow");
	totalRow.find(".total-tests").html(totalTestCases);
	totalRow.find(".tests-ok").html(totalTestsOk);
	totalRow.find(".tests-failed").html(totalTestsFailed);
	totalRow.find(".total-time").html(totalTime + ' s');
	
	var okPercentage = totalTestsOk * 100 / totalTestCases;
	var barra_azul = totalRow.find('.barra-azul');
	var id = new Date().getTime() + Math.random().toString(36).substring(7);
	barra_azul.attr('id', id);
	barra_azul.attr('data-transitiongoal', okPercentage);
	setTimeout(animateProgressBar, 10, id);
}










// =================

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


function getTestsInModule(module){
	var tests = 0;
	for(t in allTestCases){
		if(allTestCases[t].module == module){
			tests++
		}
	}
	return tests
}


function getTotalTestsOkInModule(module){
	var totalOk = 0;
	for(t in allTestCases){
		if(allTestCases[t].module == module && allTestCases[t].result == 'pass'){
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

function getTotalTestsOk(){
	var totalOk = 0;
    for (key in allTestCases) {
        if (allTestCases[key].result == 'pass') totalOk++;
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


function moduleRowAlreadyExists(module){
	var exists = false;
	$("table.por-modulo tbody td.module").each(function(){
		if($(this).html() == module){
			exists = true
		}
	});
	return exists
}	


function getModuleRow(module){
	var row;
	$("table.por-modulo tbody tr").each(function(){
		if($(this).find('td.module').html() == module){
			row = $(this)
		}
	});
	return row
}


function refreshNumbering(){
	var numbering = 0;

	var rows = $(".table.por-modulo tbody tr");
	for(r in rows){
		$(rows[r]).find('td.module-number').html(numbering);
		numbering++
	}
}





