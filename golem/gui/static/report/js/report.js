

var ReportDashboard = new function(){

    this.generateProjectContainer = function(projectName){
        var projectContainer = " \
            <div class='col-md-12 project-container' id='"+projectName+"'> \
                <h3 class='no-margin-top'> \
                    <a href='/report/project/"+projectName+"/' class='link-without-underline'>"+projectName+"</a> \
                </h3> \
            </div>";
        return $(projectContainer)
    };

    this.generateProjectContainerSingleSuite = function(projectName){
        var projectContainer = " \
            <div class='col-md-12 project-container' id='"+projectName+"'></div>";
        return $(projectContainer)
    };

    this.generateExecutionsContainer = function(projectName, suiteName){
        var executionsContainer = "\
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
        var executionsContainer = "\
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
        var row = "\
            <tr class='last-execution-row'> \
                <td class='numero'>"+data.index+"</td> \
                <td class='fecha'>"+data.dateTime+"</td> \
                <td class='ambiente'>"+data.environment+"</td> \
                <td class='resultado'> \
                    <div class='progress progress-bar-container'> \
                        <div aria-valuenow='10' style='width: 100%;'\
                            class='progress-bar progress-bar-danger barra-roja'\
                            data-transitiongoal='10'></div>\
                        <div aria-valuenow='20' style='width: 50%;' \
                            class='progress-bar barra-azul' \
                            data-transitiongoal='20' id='"+data.blueBarId+"'></div>\
                    </div>\
                </td>\
            </tr>";
        row = $(row);
        row.attr('onclick', "document.location.href='/report/project/"+data.project+"/"+data.suite+"/"+data.execution+"/'");
        return row
    };
}


var ExecutionsReport = new function(){

    this.generateTestRow = function(data){
        var row = "\
            <tr class='primera-fila'>\
                <td class='tc-number'>"+data.numbering+"</td>\
                <td class='tc-module'>"+data.module+"</td>\
                <td class='tc-name'>"+data.name+"</td>\
                <td class='tc-environment'>"+data.environment+"</td>\
                <td class='tc-browser'>"+data.browser+"</td>\
                <td class='tc-result'>"+data.result+"</td>\
                <td class='tc-time'>"+data.elapsedTime+"</td>\
                <td class='link'><a href='' target='blank'>\
                    <span class='glyphicon glyphicon-new-window' aria-hidden='true'></span></a></td>\
            </tr>";
        return $(row)
    };

    this.generateModuleRow = function(data){
        var row = "\
            <tr>\
                <td class='module'>"+data.moduleName+"</td>\
                <td class='total-tests'>"+data.totalTests+"</td>\
                <td class='tests-ok'>"+data.testsPassed+"</td>\
                <td class='tests-failed'>"+data.testsFailed+"</td>\
                <td class='percentage'>\
                    <div class='progress'>\
                        <div aria-valuenow='10' style='width: 100%;' \
                            class='progress-bar progress-bar-danger' \
                            data-transitiongoal='10'></div>\
                        <div aria-valuenow='20' style='width: 50%;' \
                            class='progress-bar barra-azul' data-transitiongoal='20'></div>\
                    </div>\
                </td>\
                <td class='total-time'></td>\
            </tr>";
        return $(row)
    }

}

