

var allProjectsData = {};


$(document).ready(function() {            
	$.ajax({
		url: "/report/get_last_executions/",
		data: {
            "project": projectName,
            "suite": suiteName,
            "limit": 5
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
	
	allProjectsData[project] = {};

	for(suite in projectData){

		if(suiteName.length > 0)
			var suiteContainer = ReportDashboard.generateExecutionsContainerSingleSuite(project, suite);
		else
			var suiteContainer = ReportDashboard.generateExecutionsContainer(project, suite);
		
		allProjectsData[project][suite] = [ ['date', 'total', 'error']];

		// fill in last executions table
		var index = 1;
		for(e in projectData[suite]){
			var execution = projectData[suite][e];
			
			var blueBarId = guidGenerator();

			var row = ReportDashboard.generateExecutionsTableRow({
				project: project,
				suite: suite,
				execution: execution,
				index: index.toString(),
				dateTime: utils.getDateTimeFromTimestamp(execution),
				environment: '',
				blueBarId: blueBarId});

			completarBarraPorcentaje(project, suite, execution, blueBarId, index);

			suiteContainer.find("tbody").append(row);

			index += 1;
		}
		projectContainer.append(suiteContainer);
	}

	projectContainer.show();
	$(".all-projects-container").append(projectContainer);
}


function completarBarraPorcentaje(project, suite, execution, id, index){

	$.post( 
		"/report/get_execution_data/",
		{
			project: project,
			suite: suite,
			execution: execution
		},
		function( data ) {
  			var okPercentage = data.execution_data.total_cases_ok * 100 / data.execution_data.total_cases;

  			$("#"+id).attr('data-transitiongoal', okPercentage);

  			animateProgressBar(id);

  			allProjectsData[project][suite].push([
  				index.toString(),
  				data.execution_data.total_cases,
  				data.execution_data.total_cases - data.execution_data.total_cases_ok]);

  			cargarGraficoHistorial(project, suite);
		});
}


function animateProgressBar(id){
	var goal = $("#"+id).attr('data-transitiongoal');
	$("#"+id).css('width', goal + '%');
}


function cargarGraficoHistorial(project, suite){


	// google charts might not be loaded yet
	if(google.visualization != undefined && 
		google.visualization.arrayToDataTable != undefined &&
		google.visualization.AreaChart != undefined){
		
		// var data = google.visualization.arrayToDataTable([
	    //   ['Year', 'Sales', 'Expenses'],
	    //   ['2013',  1000,      400],
	    //   ['2014',  1170,      460],
	    // ]);
	    var container = $("#"+project+" #"+suite).find(".plot-chart-container")[0]

		var data = google.visualization.arrayToDataTable( allProjectsData[project][suite] );

	    var options = {
	      title: '',
	      hAxis: {title: '',  titleTextStyle: {color: '#333'}},
	      vAxis: {minValue: 0},
	      height: 218,
	      backgroundColor: '#f9f9f9',
	      animation: {
	      	startup: true, 
	      	duration: 700,
	      	easing: 'in'
	      },
	      legend: {position: 'none'},
	      chartArea: {
	      	left: 5,
	      	right: 5
	      }
	      // backgroundColor: {
	      // 		fill: '#f9f9f9',
	      //   	stroke: '#d3d3d3',
	      //   	strokeWidth: 2,
    	  // 	}
	    };

	    var chart = new google.visualization.AreaChart(container);
	    chart.draw(data, options);
	}
	else{
		setTimeout(cargarGraficoHistorial, 100, project, suite)
	    
	}
}

function guidGenerator() {
    var S4 = function() {
       return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    };
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}