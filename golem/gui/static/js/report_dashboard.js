
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
	if(suiteName || projectName)
		var projectContainer = ReportDashboard.generateProjectContainerSingleSuite(project);
	else
		var projectContainer = ReportDashboard.generateProjectContainer(project);

	for(suite in projectData){

		if(suiteName)
			var suiteContainer = ReportDashboard.generateExecutionsContainerSingleSuite(project, suite);
		else
			var suiteContainer = ReportDashboard.generateExecutionsContainer(project, suite);
		
		// fill in last executions table
		var index = 1;
		var executions = []

		for(e in projectData[suite]){
			var execution = projectData[suite][e];
			var dateTime = utils.getDateTimeFromTimestamp(execution);
			executions.push(execution)

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
			loadChartAndBars(project, suite, execution, okBar, failBar, index);
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
			            backgroundColor: '#fd5a3e',
			            borderColor: '#fd5a3e',
			            data: [],
			        },
			        {
			            label: "Passed",
			            backgroundColor: '#95BD65',
			            borderColor: '#95BD65',
			            data: [],
			        },
			        {
			            label: "Pending",
			            backgroundColor: '#b3b3b3',
			            borderColor: '#b3b3b3',
			            data: [],
			        }
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
		            }
		        },
		        tooltips: {
		        	callbacks: {
		        		title: function(tooltipItems, data) {
					       return utils.getDateTimeFromTimestamp(data.labels[tooltipItems[0].index]);
					     }
                	}
		        },
		        maintainAspectRatio: false,
	    	}
		});
		charts[project+suite] = chart;
	}
	$(".all-projects-container").append(projectContainer);
}


function loadChartAndBars(project, suite, execution, okBar, failBar, index){
	//var dateTime = utils.getDateTimeFromTimestamp(execution);

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

  			updateChart({
  				project: project,
  				suite: suite,
  				label: execution,
  				totalOk: executionData.total_cases_ok,
  				totalFailed: executionData.total_cases_fail,
  				totalPending: executionData.total_pending
  			});
		});
}


function updateChart(data){
	var chart = charts[data.project+data.suite];
	var indexOfLabel = chart.data.labels.indexOf(data.label);

	var indexOfDatasetLabelPassed = chart.data.datasets.map(function(o) { return o.label; }).indexOf('Passed');
	var indexOfDatasetLabelFailed = chart.data.datasets.map(function(o) { return o.label; }).indexOf('Failed');
	var indexOfDatasetLabelPending = chart.data.datasets.map(function(o) { return o.label; }).indexOf('Pending');

	chart.data.datasets[indexOfDatasetLabelPassed].data[indexOfLabel] = data.totalOk;
	chart.data.datasets[indexOfDatasetLabelFailed].data[indexOfLabel] = data.totalFailed;
	chart.data.datasets[indexOfDatasetLabelPending].data[indexOfLabel] = data.totalPending;

	chart.update();
	return
}