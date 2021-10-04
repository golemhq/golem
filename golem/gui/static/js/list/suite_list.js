
$(document).ready(function() {
    SuiteList.getSuites(Global.project);
    SuiteList.generateHealthChart(Global.project);
    SuiteList.checkIfProjectHasNoTests();
});


const SuiteList = new function(){

    this.getSuites = function(projectName) {
        xhr.get('/api/project/suite-tree', {'project': projectName}, suites => {
            FileExplorer.initialize(suites, 'suite', $('#fileExporerContainer')[0]);
        })
    }

    this.generateHealthChart = function(projectName) {
        xhr.get('/api/project/health', {'project': projectName}, healthData => {
            if(Object.keys(healthData).length) {
                SuiteList.loadHealthData(healthData);
            } else {
                $("#healthContainer").html("<div class='text-center' style='padding-top: 0px; color: darkgrey'>no previous executions</div>");
            }
        })
    }

    this.loadHealthData = function(healthData){
        // use the dataContainer to store result
        // totals and colors used to generate
        // the doughnut chart afterwards
        let dataContainer = {};

        let table = `
            <table id="healthTable" class="table no-margin-bottom last-execution-table">
                <thead>
                    <tr>
                        <th>Suite</th>
                        <th>Date &amp; Time</th>
                        <th>Result</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>`;
        $("#healthTableContainer").append(table);

        $.each(healthData, function(execution){
            let executionData = healthData[execution];
            let dateTime = Main.Utils.getDateTimeFromTimestamp(executionData.execution);
            let newRow = $(`
                <tr class="cursor-pointer" onclick="">
                    <td class="suite-name"><span class="suite-name-span">${execution}</span></td>
                    <td>${dateTime}</td>
                    <td class="result"><div class="progress"></div></td>
                </tr>`);
            newRow.attr('onclick', `document.location.href='/report/${Global.project}/${execution}/${executionData.execution}/'`);
            $("#healthTable tbody").append(newRow);
            let results = Object.keys(executionData.totals_by_result).sort()
            let container = newRow.find('td.result>div.progress');
            Main.ReportUtils.createProgressBars(container, results)
            results.forEach(function(result){
                let thisResultTotal = executionData.totals_by_result[result];
                let percentage = thisResultTotal * 100 / executionData.total;
                if(result in dataContainer){
                    dataContainer[result]['total'] += thisResultTotal
                }
                else{
                    dataContainer[result] = {
                        'total': thisResultTotal,
                        'color': Main.ReportUtils.getResultColor(result)
                    }
                }
                Main.ReportUtils.animateProgressBar(container, result, percentage);
            });
        });
        let ctx = document.getElementById('healthChartCanvas').getContext('2d');
        let data = [];
        let colors = []
        Object.keys(dataContainer).forEach(function(result){
            data.push(dataContainer[result]['total']);
            colors.push(dataContainer[result]['color'])
        });
        let chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(dataContainer),
                datasets: [
                    {
                        data: data,  // array of result total values
                        backgroundColor: colors,  // array of result colors
                        hoverBackgroundColor: colors  // array of result colors
                    }
                ]
            },
            options: {
                animation: {
                    animateRotate: true
                },
                responsive: true,
                maintainAspectRatio : true,
            }
        });
    }

    this.checkIfProjectHasNoTests = function() {
        xhr.get('/api/project/has-tests', {'project': Global.project}, projectHasTests => {
            if(!projectHasTests) {
                let content = `This project has no tests. Create the first test <strong><a href="/project/${Global.project}/tests/" class="alert-link">here</a>.</strong>`;
                Main.Utils.infoBar($("#infoBarContainer"), content)
            }
        })
    }
}
