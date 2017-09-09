

var allProjectsData = {};


$(document).ready(function() {            
	
	$.ajax({
		url: "/report/get_ultimos_proyectos/",
		data: {
            "project": globalProject,
            "suite": suite,
            "limit": 0
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
	var projectContainer = $(".proyect-container.primer-proyecto").clone().removeClass('primer-proyecto');

	// fill in project name
	//projectContainer.find(".project-name").html( project );
	projectContainer.attr('id', project);
	allProjectsData[project] = {};

	for(suite in projectData){
		var suiteContainer = projectContainer.find(".suite-container.primer-suite-container").clone().removeClass('primer-suite-container');
		suiteContainer.attr('id', suite);
		suiteContainer.find(".suite-name").html(suite);

		allProjectsData[project][suite] = [ ['date', 'total', 'error']];

		var tablaUltimasEjec = suiteContainer.find(".table.ultimas-ejecuciones");

		// fill in last executions table
		var index = 1;
		for(e in projectData[suite]){
			var execution = projectData[suite][e];
			var fila = tablaUltimasEjec.find("tr.primera-fila").clone().removeClass('primera-fila');
			fila.find(".numero").html(index.toString());
			fila.find(".fecha").html(getDateTimeFromTimestamp(execution));
			fila.find(".ambiente").html();

			fila.attr('onclick', "document.location.href='/report/project/"+project+"/"+suite+"/"+execution+"/'");

			var progressBarContainer = fila.find(".progress-bar-container");

			var barra_azul = progressBarContainer.find('.barra-azul');
			var id = guidGenerator();
			barra_azul.attr('id', id);

			completarBarraPorcentaje(project, suite, execution, id, index);

			tablaUltimasEjec.find("tbody").append(fila);
			index += 1;
		}
		tablaUltimasEjec.find("tr.primera-fila").remove();

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
			console.log(data);
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
	    //   ['2015',  660,       1120],
	    //   ['2016',  1030,      540]
	    // ]);
	    var container = $("#"+project+" #"+suite).find(".plot-chart-container")[0]

		var data = google.visualization.arrayToDataTable( allProjectsData[project][suite] );

	    var options = {
	      title: '',
	      hAxis: {title: '',  titleTextStyle: {color: '#333'}},
	      vAxis: {minValue: 0},
	      backgroundColor: '#f9f9f9'
	    };

	    var chart = new google.visualization.AreaChart(container);
	    chart.draw(data, options);
	}
	else{
		setTimeout(cargarGraficoHistorial, 100, project, suite)
	    
	}
}


function getDateTimeFromTimestamp(timestamp){
	var sp = timestamp.split('.');
	var dateTimeString = sp[0]+'/'+sp[1]+'/'+sp[2]+' '+sp[3]+':'+sp[4];
	return dateTimeString
}


function guidGenerator() {
    var S4 = function() {
       return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    };
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}