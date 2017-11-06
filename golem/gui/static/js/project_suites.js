
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

    var totalOk = 0;
    var totalFail = 0;
    var totalPending = 0;

    var table = "\
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
        var okPercentage = healthData[suite].total_ok * 100 / healthData[suite].total;
        var failPercentage = healthData[suite].total_fail * 100 / healthData[suite].total + okPercentage;
        totalOk += healthData[suite].total_ok;
        totalFail += healthData[suite].total_fail;
        totalPending += healthData[suite].total_pending;
        var newRow = "\
            <tr class='cursor-pointer' onclick=''>\
                <td class=''>"+suite+"</td>\
                <td class=''>"+utils.getDateTimeFromTimestamp(healthData[suite].execution)+"</td>\
                <td class=''>\
                    "+reportUtils.generateProgressBars()+"\
                </td>\
            </tr>";
        newRow = $(newRow);

        newRow.attr('onclick', "document.location.href='/report/project/"+project+"/suite/"+suite+"/"+healthData[suite].execution+"/'");

        $("#healthTable tbody").append(newRow);

        var okBar = newRow.find('.ok-bar');
        var failBar = newRow.find('.fail-bar');
        utils.animateProgressBar(okBar, okPercentage)
        utils.animateProgressBar(failBar, failPercentage)
    });

    var ctx = document.getElementById('healthChartCanvas').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Passed', 'Failed', 'Pending'],
            datasets: [
                {
                    data: [totalOk, totalFail, totalPending],
                    backgroundColor: [
                        "#95BD65",
                        "#fd5a3e",
                        "#b3b3b3"
                    ],
                    hoverBackgroundColor: [
                        "#95BD65",
                        "#fd5a3e",
                        "#b3b3b3"
                    ]
                }
            ]
        },
        options: {
            animation: {
                //animateScale: true,
                animateRotate: true
            },
            responsive: true,
            maintainAspectRatio : true,
        }
    });
}