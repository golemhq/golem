

// var allProjectsData = {};

var charts = {}
var chartData = {}


$(document).ready(function() {

	var limit;
	if(projectName == "") limit = 5;
	else if(suiteName == "") limit = 10
	else limit = 50;

	$.ajax({
		url: "/report/get_last_executions/",
		data: {
            "project": projectName,
            "suite": suiteName,
            "limit": limit
        },
        dataType: 'json',
        type: 'POST',
		success: function( data ) {	
	  		for(project in data.projects){
	  			loadProject(project, data.projects[project]);
	  		}
	  	}
	});
});


function loadProject(project, projectData){
	if(suiteName)
		var projectContainer = ReportDashboard.generateProjectContainerSingleSuite(project);
	else
		var projectContainer = ReportDashboard.generateProjectContainer(project);
	
	//allProjectsData[project] = {};

	for(suite in projectData){

		if(suiteName)
			var suiteContainer = ReportDashboard.generateExecutionsContainerSingleSuite(project, suite);
		else
			var suiteContainer = ReportDashboard.generateExecutionsContainer(project, suite);
		
		//allProjectsData[project][suite] = [ ['date', 'total', 'error']];

		// fill in last executions table
		var index = 1;
		var executions = []

		for(e in projectData[suite]){
			var execution = projectData[suite][e];
			var dateTime = utils.getDateTimeFromTimestamp(execution);
			executions.push(dateTime)

			//var blueBarId = guidGenerator();

			var row = ReportDashboard.generateExecutionsTableRow({
				project: project,
				suite: suite,
				execution: execution,
				index: index.toString(),
				dateTime: dateTime,
				environment: ''
			});

			var okBar = row.find('.ok-bar');
			var failBar = row.find('.fail-bar');
			completarBarraPorcentaje(project, suite, execution, okBar, failBar, index);

			suiteContainer.find("tbody").append(row);

			index += 1;
		}
		projectContainer.append(suiteContainer);


		// create chart for suite
		var ctx = suiteContainer.find('canvas')[0].getContext('2d');
		var chart = new Chart(ctx, {
		    type: 'line',
		    data: {
		        labels: executions,
		        datasets: [
		        {
		            label: "Failed",
		            backgroundColor: 'rgb(217, 83, 79)',
		            borderColor: 'rgb(217, 83, 79)',
		            data: [],
		        },
		        {
		            label: "Passed",
		            backgroundColor: 'rgb(66, 139, 202)',
		            borderColor: 'rgb(66, 139, 202)',
		            data: [],
		        },
		    	]
	    	},
	    	options: {
	    		scales: {
		            yAxes: [{
		                stacked: true,
		                ticks: {
		                    beginAtZero: true
		                }
		            }],
		             xAxes: [{
		                display: false
		            }]
		        },
		        elements: {
		            line: {
		                tension: 0, // disables bezier curves
		            },

		        },
		        maintainAspectRatio: false,
	    	}
		});

		charts[project+suite] = chart;
	}

	projectContainer.show();
	$(".all-projects-container").append(projectContainer);
}


function completarBarraPorcentaje(project, suite, execution, okBar, failBar, index){
	var dateTime = utils.getDateTimeFromTimestamp(execution);

	$.post( 
		"/report/get_execution_data/",
		{
			project: project,
			suite: suite,
			execution: execution
		},
		function( executionData ) {
  			var okPercentage = executionData.total_cases_ok * 100 / executionData.total_cases;
			var failPercentage = executionData.total_cases_fail * 100 / executionData.total_cases + okPercentage;
  			utils.animateProgressBar(okBar, okPercentage);
  			utils.animateProgressBar(failBar, failPercentage);

  			// if(chartData[project+suite] === undefined){
  			// 	chartData[project+suite] = {}
  			// }

  			//chartData[project+suite][dateTime] = {passed: executionData.total_cases_ok};
  			//chartData[project+suite] = und

  			// allProjectsData[project][suite].push([
  			// 	index.toString(),
  			// 	data.execution_data.total_cases,
  			// 	data.execution_data.total_cases - data.execution_data.total_cases_ok]);

  			cargarGraficoHistorial(project, suite, dateTime, executionData.total_cases_ok, executionData.total_cases - executionData.total_cases_ok);
		});
}


// function animateProgressBar(id){
// 	var goal = $("#"+id).attr('data-transitiongoal');
// 	$("#"+id).css('width', goal + '%');
// }

// function animateProgressBar(bar, percentage){
// 	// var goal = $("#"+id).attr('data-transitiongoal');
// 	// $("#"+id).css('width', goal + '%');
// 	bar.css('width', percentage+'%');
// }



function cargarGraficoHistorial(project, suite, label, passed, failed){
	var indexOfLabel = charts[project+suite].data.labels.indexOf(label);

	var indexOfDatasetLabelPassed = charts[project+suite].data.datasets.map(function(o) { return o.label; }).indexOf('Passed');
	var indexOfDatasetLabelFailed = charts[project+suite].data.datasets.map(function(o) { return o.label; }).indexOf('Failed');

	charts[project+suite].data.datasets[indexOfDatasetLabelPassed].data[indexOfLabel] = passed;
	charts[project+suite].data.datasets[indexOfDatasetLabelFailed].data[indexOfLabel] = failed;

	charts[project+suite].update();

	return

	// google charts might not be loaded yet
	// if(google.visualization != undefined && 
	// 	google.visualization.arrayToDataTable != undefined &&
	// 	google.visualization.AreaChart != undefined){
		
	// 	// var data = google.visualization.arrayToDataTable([
	//     //   ['Year', 'Sales', 'Expenses'],
	//     //   ['2013',  1000,      400],
	//     //   ['2014',  1170,      460],
	//     // ]);
	//     var container = $("#"+project+" #"+suite).find(".plot-chart-container")[0]

	// 	var data = google.visualization.arrayToDataTable( allProjectsData[project][suite] );

	//     var options = {
	//       title: '',
	//       hAxis: {title: '',  titleTextStyle: {color: '#333'}},
	//       vAxis: {minValue: 0},
	//       height: 218,
	//       backgroundColor: '#f9f9f9',
	//       animation: {
	//       	startup: true, 
	//       	duration: 700,
	//       	easing: 'in'
	//       },
	//       legend: {position: 'none'},
	//       chartArea: {
	//       	left: 5,
	//       	right: 5
	//       }
	//       // backgroundColor: {
	//       // 		fill: '#f9f9f9',
	//       //   	stroke: '#d3d3d3',
	//       //   	strokeWidth: 2,
 //    	  // 	}
	//     };

	//     var chart = new google.visualization.AreaChart(container);
	//     chart.draw(data, options);
	// }
	// else{
	// 	setTimeout(cargarGraficoHistorial, 100, project, suite)
	    
	// }
}

// function guidGenerator() {
//     var S4 = function() {
//        return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
//     };
//     return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
// }