
$(document).ready(function() {
	let limit;
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
	  			ReportDashboardMain.loadProject(project, data.projects[project]);
	  		}
	  	}
	});
});


const ReportDashboardMain = new function(){

    this.charts = {}

    this.loadProject = function(project, projectData){
        let projectContainer;
        if(suiteName || projectName)
            projectContainer = ReportDashboard.generateProjectContainerSingleSuite(project);
        else
            projectContainer = ReportDashboard.generateProjectContainer(project);
        for(suite in projectData){
            let suiteContainer;
            if(suiteName)
                suiteContainer = ReportDashboard.generateExecutionsContainerSingleSuite(project, suite);
            else
                suiteContainer = ReportDashboard.generateExecutionsContainer(project, suite);
            // fill in last executions table
            let index = 1;
            let executions = []
            for(e in projectData[suite]){
                let execution = projectData[suite][e];
                let dateTime = Main.Utils.getDateTimeFromTimestamp(execution);
                executions.push(execution)
                let row = ReportDashboard.generateExecutionsTableRow({
                    project: project,
                    suite: suite,
                    execution: execution,
                    index: index.toString(),
                    dateTime: dateTime,
                    environment: ''
                });
                ReportDashboardMain.loadChartAndBars(project, suite, execution, row);
                suiteContainer.find("tbody").append(row);
                index += 1;
            }
            projectContainer.append(suiteContainer);
            // create chart for suite
            let ctx = suiteContainer.find('canvas')[0].getContext('2d');
            let chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: executions,
                    datasets: []
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
                               return Main.Utils.getDateTimeFromTimestamp(data.labels[tooltipItems[0].index]);
                             }
                        }
                    },
                    maintainAspectRatio: false,
                }
            });
            ReportDashboardMain.charts[project+suite] = chart;
        }
        $(".all-projects-container").append(projectContainer);
    }

    this.loadChartAndBars = function(project, suite, execution, row){

        $.post(
            "/report/get_execution_data/",
            {
                project: project,
                suite: suite,
                execution: execution
            },
            function( executionData ) {
                let results = Object.keys(executionData.totals_by_result).sort()
                let container = row.find('td.result>div.progress');
                // Create a progress bar for each result
                Main.ReportUtils.createProgressBars(container, results)
                results.forEach(function(result){
                    let percentage = executionData.totals_by_result[result] * 100 / executionData.total_tests;
                    Main.ReportUtils.animateProgressBar(container, result, percentage);
                });
                ReportDashboardMain.updateChart({
                    project: project,
                    suite: suite,
                    label: execution,
                    totalsByResult: executionData.totals_by_result
                });
            }
        );
    }

    this.updateChart = function(data){
        let chart = ReportDashboardMain.charts[data.project+data.suite];
        let indexOfLabel = chart.data.labels.indexOf(data.label);

        for(result in data.totalsByResult){
            let dataSetIndex = chart.data.datasets.map(function(o) { return o.label; }).indexOf(result);
            // Add data set if it´s not already present
            if(dataSetIndex === -1){
                let color =  Main.ReportUtils.getResultColor(result);
                // because not all executions have values for all
                // results, this causes steps in the chart lines.
                // Initialize the values for this dataset to 0
                let defaultData = [];
                chart.data.labels.forEach(() => defaultData.push(0));
                let dataSet = {
                    label: result,
                    backgroundColor: color,
                    borderColor: color,
                    data: defaultData,
                }
               chart.data.datasets.push(dataSet);
            }
            let indexOfDatasetLabel = chart.data.datasets.map(function(o) { return o.label; }).indexOf(result);
            chart.data.datasets[indexOfDatasetLabel].data[indexOfLabel] = data.totalsByResult[result];
        };
        chart.update();
    }
}


const ReportDashboard = new function(){

    this.generateProjectContainer = function(projectName){
        let projectContainer = " \
            <div class='col-md-12 project-container' id='"+projectName+"'> \
                <h3 class='no-margin-top'> \
                    <a href='/report/project/"+projectName+"/' class='link-without-underline'>"+projectName.replace('_',' ')+"</a> \
                </h3> \
            </div>";
        return $(projectContainer)
    };

    this.generateProjectContainerSingleSuite = function(projectName){
        let projectContainer = " \
            <div class='col-md-12 project-container' id='"+projectName.replace('_',' ')+"'></div>";
        return $(projectContainer)
    };

    this.generateExecutionsContainer = function(projectName, suiteName){
        let executionsContainer = "\
            <div class='suite-container' id='"+suiteName+"'> \
                <div class='widget widget-table'> \
                    <div class='widget-header'> \
                        <h3><i class='fa fa-table'></i><span class='suite-name'> \
                            <a href='/report/project/"+projectName+"/suite/"+suiteName+"/' \
                                class='link-without-underline'>"+suiteName+"</a> \
                        </span></h3> \
                    </div> \
                    <div class='flex-row'>\
                        <div class='widget-content table-content col-sm-7'> \
                            <div class='table-responsive last-execution-table'> \
                                <table class='table no-margin-bottom'> \
                                    <thead> \
                                        <tr> \
                                            <th>#</th> \
                                            <th>Date & Time</th> \
                                            <th>Environment</th> \
                                            <th>Result &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp</th> \
                                        </tr> \
                                    </thead> \
                                    <tbody></tbody> \
                                </table> \
                            </div> \
                        </div> \
                        <div class='col-sm-5 table-content chart-container'> \
                            <div class='chart-inner-container'>\
                                <canvas></canvas>\
                            </div>\
                        </div> \
                    </div>\
                </div> \
            </div>";
        return $(executionsContainer)
    };

    this.generateExecutionsContainerSingleSuite = function(projectName, suiteName){
        let executionsContainer = "\
            <div class='suite-container' id='"+suiteName+"'> \
                <div class='widget widget-table'> \
                    <div class='' style='height: 218px'> \
                        <canvas></canvas>\
                    </div> \
                    <div class='widget-content table-content'> \
                        <div class='table-responsive last-execution-table'> \
                            <table class='table no-margin-bottom'> \
                                <thead> \
                                    <tr> \
                                        <th>#</th> \
                                        <th>Date & Time</th> \
                                        <th>Environment</th> \
                                        <th>Result &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp</th> \
                                    </tr> \
                                </thead> \
                                <tbody></tbody> \
                            </table> \
                        </div> \
                    </div> \
                </div> \
            </div>";
        return $(executionsContainer)
    };

    this.generateExecutionsTableRow = function(data){
        let suiteReportUrl = `document.location.href='/report/project/${data.project}/suite/${data.suite}/${data.execution}'`;
        let row = `
            <tr class="cursor-pointer" onclick="${suiteReportUrl}">
                <td class="index">${data.index}</td>
                <td class="date">${data.dateTime}</td>
                <td class="environment">${data.environment}</td>
                <td class="result"><div class="progress"></div></td>
            </tr>`;
        return $(row);
    };
}
