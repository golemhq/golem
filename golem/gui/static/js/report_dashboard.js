
$(document).ready(function() {
    if(projectName === null) {
        getAllProjectsLastExecutions();
    } else {
        if(executionName === null)
            getProjectLastExecutions(projectName);
        else
            getLastExecutions(projectName, executionName);
    }
})


function getAllProjectsLastExecutions() {
    xhr.get('/api/report/last-executions', {}, data => {
        for(project in data.projects) {
            ReportDashboardMain.loadProject(project, data.projects[project]);
        }
    })
}


function getProjectLastExecutions(project) {
    xhr.get('/api/report/project/last-executions', {project}, data => {
        for(project in data.projects) {
            ReportDashboardMain.loadProject(project, data.projects[project]);
        }
    })
}


function getLastExecutions(project, execution) {
    xhr.get('/api/report/execution/last-executions', {project, execution}, data => {
        for(project in data.projects) {
            ReportDashboardMain.loadProject(project, data.projects[project]);
        }
    })
}


const ReportDashboardMain = new function(){

    this.charts = {}

    this.loadProject = function(project, projectData){
        let projectContainer;
        if(projectName !== null)
            projectContainer = ReportDashboard.generateProjectContainerSingleExecution(project);
        else
            projectContainer = ReportDashboard.generateProjectContainer(project);
        if(Object.keys(projectData).length == 0){
            projectContainer.append('<p>There are no executions for this project</p>')
        }
        for(execution in projectData){
            let executionContainer;
            if(executionName)
                executionContainer = ReportDashboard.generateExecutionsContainerSingleExecution(project, execution);
            else
                executionContainer = ReportDashboard.generateExecutionsContainer(project, execution);
            // fill in last executions table
            let index = 1;
            let timestamps = []
            for(e in projectData[execution]){
                let timestamp = projectData[execution][e];
                let dateTime = Main.Utils.getDateTimeFromTimestamp(timestamp);
                timestamps.push(timestamp)
                let row = ReportDashboard.generateExecutionsTableRow({
                    project: project,
                    execution: execution,
                    timestamp: timestamp,
                    index: index.toString(),
                    dateTime: dateTime,
                    environment: ''
                });
                ReportDashboardMain.loadChartAndBars(project, execution, timestamp, row);
                executionContainer.find("tbody").append(row);
                index++;
            }
            projectContainer.append(executionContainer);
            // create chart for execution
            let ctx = executionContainer.find('canvas')[0].getContext('2d');
            let chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: timestamps,
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
                    animation: { duration: 500 },
                    maintainAspectRatio: false
                }
            });
            ReportDashboardMain.charts[project+execution] = chart;
        }
        $(".all-projects-container").append(projectContainer);
    }

    this.loadChartAndBars = function(project, execution, timestamp, row){
        xhr.get('/api/report/execution', {project, execution, timestamp}, executionData => {
            let results = Object.keys(executionData.totals_by_result).sort();
            let container = row.find('td.result>div.progress');
            results.forEach(result => {
                if(!Main.ReportUtils.hasProgressBarForResult(container, result)) {
                    Main.ReportUtils.createProgressBars(container, [result])
                }
                let percentage = executionData.totals_by_result[result] * 100 / executionData.total_tests;
                Main.ReportUtils.animateProgressBar(container, result, percentage);
            });
            if(!('pending' in executionData.totals_by_result)) {
                Main.ReportUtils.animateProgressBar(container, 'pending', 0);
            }
            ReportDashboardMain.updateChart({
                project: project,
                execution: execution,
                label: timestamp,
                totalsByResult: executionData.totals_by_result
            });
            if(executionData.has_finished) {
                row.find('.spinner').hide();
                if(Global.user.projectWeight >= Main.PermissionWeightsEnum.admin) {
                    row.find('.glyphicon-trash').show()
                }
            } else {
                row.find('.spinner').show();
                window.setTimeout(function() {
                    ReportDashboardMain.loadChartAndBars(project, execution, timestamp, row);
                }, 2000, project, execution, timestamp, row)
            }
        })
    }

    this.updateChart = function(data){
        let chart = ReportDashboardMain.charts[data.project+data.execution];
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

            if(!('pending' in data.totalsByResult)){
                // when execution finishes, set pending to 0
                indexOfDatasetLabel = chart.data.datasets.map(function(o) { return o.label; }).indexOf('pending');
                let pendingDataset = chart.data.datasets[indexOfDatasetLabel];
                if(pendingDataset != undefined){
                    pendingDataset.data[indexOfLabel] = 0;
                }
            }
        };
        chart.update();
    }

    this.deleteExecutionConfirm = function(elem){
        let executionContainer = $(elem).closest('.execution-container');
        let execution = executionContainer.attr('id');
        let project = $(elem).closest('.project-container').attr('id');
        let message = `<span style="word-break: break-all">Are you sure you want to delete all reports in this execution? This action cannot be undone.</span>`;
        let callback = function(){
            ReportDashboardMain.deleteExecution(executionContainer, project, execution);
        }
        Main.Utils.displayConfirmModal('Delete', message, callback);
    }

    this.deleteExecution = function(executionContainer, project, execution){
        xhr.delete('/api/report/execution', {project, execution}, errors => {
            if(errors.length) {
                errors.forEach(error => Main.Utils.toast('error', error, 3000));
            } else {
                executionContainer.remove();
                Main.Utils.toast('info', 'Execution deleted', 2000)
            }
        })
        return false
    }

    this.deleteExecutionTimestampConfirm = function(elem) {
        let row = $(elem).closest('tr');
        let project = $(elem).closest('.project-container').attr('id');
        let execution = row.attr('execution-name');
        let timestamp = row.attr('timestamp');
        let message = `<span style="word-break: break-all">Are you sure you want to delete this execution? This action cannot be undone.</span>`;
        let callback = function() {
            ReportDashboardMain.deleteExecutionTimestamp(row, project, execution, timestamp);
        }
        Main.Utils.displayConfirmModal('Delete', message, callback);
    }

    this.deleteExecutionTimestamp = function(row, project, execution, timestamp){
        xhr.delete('/api/report/execution/timestamp', {project, execution, timestamp}, errors => {
            if(errors.length) {
                errors.forEach(error => Main.Utils.toast('error', error, 3000));
            } else {
                row.remove();
                Main.Utils.toast('info', 'Execution deleted', 2000)
            }
        });
        return false
    }
}


const ReportDashboard = new function(){

    this.generateProjectContainer = function(projectName){
        let projectContainer = `
            <div class="col-md-12 project-container" id="${projectName}">
                <h3 class="no-margin-top">
                    <a href="/report/${projectName}/" class="link-without-decoration">${projectName.replace('_',' ')}</a>
                </h3>
            </div>`;
        return $(projectContainer)
    };

    this.generateProjectContainerSingleExecution = function(projectName){
        let projectContainer = `<div class="col-md-12 project-container" id="${projectName}"></div>`;
        return $(projectContainer)
    };

    this.generateExecutionsContainer = function(projectName, executionName){
        let executionsContainer = `
            <div class="execution-container" id="${executionName}">
                <div class="widget widget-table">
                    <div class="widget-header">
                        <h3>
                            <i class="fa fa-table"></i><span class="suite-name">
                                <a href="/report/${projectName}/${executionName}/" class="link-without-decoration">
                                    <strong>${executionName}</strong>
                                </a>
                            </span>
                        </h3>
                        <h3 style="float: right">
                            <i class="glyphicon glyphicon-trash cursor-pointer" style="color: #b3b3b3"
                                onclick="event.stopPropagation(); ReportDashboardMain.deleteExecutionConfirm(this)"></i>
                        </h3>
                    </div>
                    <div class="flex-row">
                        <div class="widget-content table-content col-sm-7">
                            <div class="table-responsive last-execution-table">
                                <table class="table no-margin-bottom">
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Date & Time</th>
                                            <th>Environment</th>
                                            <th>Result &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>
                        <div class="col-sm-5 table-content chart-container">
                            <div class="chart-inner-container"><canvas></canvas></div>
                        </div>
                    </div>
                </div>
            </div>`;
        return $(executionsContainer)
    };

    this.generateExecutionsContainerSingleExecution = function(projectName, executionName){
        let executionsContainer = `
            <div class="suite-container" id="${executionName}">
                <div class="widget widget-table">
                    <div style="height: 218px; padding: 10px"><canvas></canvas></div>
                    <div class="widget-content table-content">
                        <div class="table-responsive last-execution-table">
                            <table class="table no-margin-bottom">
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>Date & Time</th>
                                        <th>Environment</th>
                                        <th>Result &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp</th>
                                        <th></th>
                                    </tr>
                                </thead>
                                <tbody></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>`;
        return $(executionsContainer)
    };

    this.generateExecutionsTableRow = function(data){
        let executionReportUrl = `document.location.href='/report/${data.project}/${data.execution}/${data.timestamp}/'`;
        let row = `
            <tr class="cursor-pointer" execution-name="${data.execution}" timestamp="${data.timestamp}" onclick="${executionReportUrl}">
                <td class="index">${data.index}</td>
                <td class="date">${data.dateTime}</td>
                <td class="environment">${data.environment}</td>
                <td class="result"><div class="progress"></div></td>
                <td class="spinner-container">
                    <i class="glyphicon glyphicon-trash" style="display: none; color: #b3b3b3"
                        onclick="event.stopPropagation(); ReportDashboardMain.deleteExecutionTimestampConfirm(this)"></i>
                    <i class="fa fa-cog fa-spin spinner" style="display: none;"></i>
                </td>
            </tr>`;
        return $(row);
    };
}
