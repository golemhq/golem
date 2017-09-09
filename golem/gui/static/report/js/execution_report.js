
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
	for(tc in execution_data.test_cases){
		addTestToDetailTable(execution_data.test_cases[tc]);
	}
}

function addTestToDetailTable(test){
	// is this test case already added to the table?
	if(allTestCases[test.test_set] == undefined ){
		// this test case is not added yet
		var numbering = $(".table.test-list-table tbody tr").length + 1;

		if(test.result === 'pass')
			var resultString = passIcon() + ' ' +test.result;
		else if(test.result == 'fail')
			var resultString = failIcon() + ' ' + test.result;	

		var testRow = ExecutionsReport.generateTestRow({
			numbering: numbering,
			module: test.module,
			name: test.name,
			environment: test.data.environment,
			browser: test.browser,
			result: resultString,
			elapsedTime: test.test_elapsed_time});

		var link = "/report/project/"+project+"/"+suite+"/"+execution+"/"+test.full_name+"/"+test.test_set+"/";
		testRow.attr('onclick', "document.location.href='"+link+"'");

		testRow.find('td.link a').attr('href', link)

		$(".test-list-table tbody").append(testRow);

		// add this test case to allTestCases
		allTestCases[test.test_set] = test;

		// refresh the general table
		refreshGeneralTable();

		// The module in the general table should be updated
		updateModuleRowInGeneralTable(test);
	}	
}



function updateModuleRowInGeneralTable(testCase){
	// does the row for the module already exists?
	var moduleRow = getModuleRow(testCase.module);
	if(moduleRow === null){
		// add a new row

		// var testsInModule = getTestsInModule(testCase.module);
		// var testsOkInModule = getTotalTestsOkInModule(testCase.module);
		// var testsFailedInModule = testsInModule - testsOkInModule;
		// var timeInModule = getTotalModuleTime(testCase.module);


		var moduleRow = ExecutionsReport.generateModuleRow({
			moduleName: testCase.module,
			// totalTests: testsInModule,
			// testPassed: testsOkInModule,
			// testsFailed: testsFailedInModule,
			// time: timeInModule+'s'
		});

		// moduleRow.find(".module").html(testCase.module);
		// moduleRow.find(".total-tests").html(testsInModule);
		// moduleRow.find(".tests-ok").html(testsOkInModule);
		// moduleRow.find(".tests-failed").html(testsFailedInModule);
		// moduleRow.find(".total-time").html(timeInModule + 's');

		// var okPercentage = testsOkInModule * 100 / testsInModule;
		// var barra_azul = moduleRow.find('.barra-azul');
		// var id = new Date().getTime() + Math.random().toString(36).substring(7);
		// barra_azul.attr('id', id);
  		// 		barra_azul.attr('data-transitiongoal', okPercentage);

		moduleRow.insertBefore("#totalRow");

		//refreshNumbering();
		
		//setTimeout(animateProgressBar, 200, id);
	}
	

	var testsInModule = getTestsInModule(testCase.module); //testCasesByModule[module].length;
	var testsOkInModule = getTotalTestsOkInModule(testCase.module);
	var testsFailedInModule = testsInModule - testsOkInModule;
	var timeInModule = getTotalModuleTime(testCase.module);

	//row.find(".module").html(testCase.module);
	moduleRow.find(".total-tests").html(testsInModule);
	moduleRow.find(".tests-ok").html(testsOkInModule);
	moduleRow.find(".tests-failed").html(testsFailedInModule);
	moduleRow.find(".total-time").html(timeInModule + ' s');

	var okPercentage = testsOkInModule * 100 / testsInModule;
	var barra_azul = moduleRow.find('.barra-azul');
	var id = new Date().getTime() + Math.random().toString(36).substring(7);
	barra_azul.attr('id', id);
	barra_azul.attr('data-transitiongoal', okPercentage);

	setTimeout(animateProgressBar, 200, id);
}


function refreshGeneralTable(){
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


function getModuleRow(module){
	var row = null;
	$("table.general-table tbody tr").each(function(){
		if($(this).find('td.module').html() == module){
			row = $(this)
		}
	});
	return row
}


function refreshNumbering(){
	var numbering = 0;

	var rows = $(".table.general-table tbody tr");
	for(r in rows){
		$(rows[r]).find('td.module-number').html(numbering);
		numbering++
	}
}





