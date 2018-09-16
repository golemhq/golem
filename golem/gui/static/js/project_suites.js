
$(document).ready(function() {
    getSuites(project);
    generateHealthChart(project);
});


function getSuites(projectName){
    $.ajax({
        url: "/project/get_suites/",
        data: {
            "project": projectName
        },
        dataType: 'json',
        type: 'POST',
        success: function(suites) {
            $("#suitesTree").append(Project.newElementForm('.'));
            Project.loadTreeElements($("#suitesTree"), suites.sub_elements, 'suite');
        },
    });
}


function generateHealthChart(projectName){
    $.ajax({
        url: "/report/get_project_health_data/",
        data: {
            "project": projectName,
        },
        dataType: 'json',
        type: 'POST',
        success: function( healthData ) { 
            if($.isEmptyObject(healthData)){
                $("#healthContainer").html("<div class='text-center' style='padding-top: 0px; color: darkgrey'>no previous executions</div>");
            }
            else{
                loadHealthData(healthData);
            }
        }
    });
}


function loadHealthData(healthData){
    // use the dataContainer to store result
    // totals and colors used to generate 
    // the doughnut chart afterwards
    let dataContainer = {};

    let table = "\
        <table id='healthTable' class='table no-margin-bottom last-execution-table'>\
            <thead>\
                <tr>\
                    <th>Suite</th>\
                    <th>Date &amp; Time</th>\
                    <th>Result</th>\
                </tr>\
            </thead>\
            <tbody>\
            </tbody>\
        </table>";
    $("#healthTableContainer").append(table);

    $.each(healthData, function(suite){
        let suiteData = healthData[suite];
        let dateTime = Main.Utils.getDateTimeFromTimestamp(suiteData.execution);
        let newRow = $(`
            <tr class="cursor-pointer" onclick="">
                <td class="">${suite}</td>
                <td class="">${dateTime}</td>
                <td class="result"><div class="progress"></div></td>
            </tr>`);
        newRow.attr('onclick', `document.location.href='/report/project/${project}/suite/${suite}/${suiteData.execution}/'`);
        $("#healthTable tbody").append(newRow);
        let results = Object.keys(suiteData.totals_by_result).sort()
        let container = newRow.find('td.result>div.progress');
        Main.ReportUtils.createProgressBars(container, results)
        results.forEach(function(result){
            let thisResultTotal = suiteData.totals_by_result[result];
            let percentage = thisResultTotal * 100 / suiteData.total;
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