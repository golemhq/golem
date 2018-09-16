

var testRunner = new function(){
    
    this.runTestCase = function(){
        $("button#runTest").blur();
        if(unsavedChanges)
            saveTestCase({runAfter: true});
        else
            testRunner.askForEnvBeforeRun();
    };

    this.askForEnvBeforeRun = function(){
        $.ajax({
            url: "/get_environments/",
            data: {
                project: project
            },
            dataType: 'json',
            type: 'POST',
            success: function(environments) {
                if(environments.length > 1){
                    // should ask the user which env
                    var callback = function(environment){
                        testRunner._doRunTestCase(environment);
                    }
                    Main.Utils.displaySelectPromptModal('Select Environment', '', environments, 'Run', callback)
                }
                else{
                    // should not ask the user which env
                    testRunner._doRunTestCase();
                }
            }
        });
    }

    this._doRunTestCase = function(environment){
        environment = environment || '';
        Main.Utils.toast('info', 'Running test ' + testCaseName, 3000);
        $.ajax({
            url: "/run_test_case/",
            data: {
                 "project": project,
                 "testCaseName": fullTestCaseName,
                 "environment": environment
             },
             dataType: 'json',
             type: 'POST',
             success: function(timestamp) {
                testRunner.checkTestCaseResult(project, fullTestCaseName, timestamp);
             }
         });
    }
    
    this.checkTestCaseResult = function(project, fullTestCaseName, timestamp){
        $("#testRunModal").modal("show");
        $("#testRunModal .modal-title").html('Running Test Case');
        $("#loaderContainer").show();
        $("#testResults").html('');
        $("#testResultLogs").html('');
        checkDelay = 1000;
        testRunner._checkAndRecheckStatus(checkDelay, project, fullTestCaseName, timestamp);
    }

    this._checkAndRecheckStatus = function(checkDelay, project, fullTestCaseName, timestamp){
        $.ajax({
            url: "/check_test_case_run_result/",
            data: {
                 "project": project,
                 "testCaseName": fullTestCaseName,
                 "timestamp": timestamp
            },
            dataType: 'json',
            type: 'POST',
            success: function(result) {
                checkDelay += 100;
                if(!result.complete){
                    setTimeout(function(){
                        testRunner._checkAndRecheckStatus(checkDelay, project, fullTestCaseName, timestamp);
                    }, checkDelay, project, fullTestCaseName, timestamp);

                    if(result.logs.length){
                        testRunner.mergeAndDisplayLogs(result.logs);
                    }
                }
                else{
                    $("#loaderContainer").hide();
                    $("#testRunModal .modal-title").html('Result');
                    if(result.logs.length){
                        $("#loaderContainer").hide();
                        testRunner.mergeAndDisplayLogs(result.logs);
                    }
                    if(result.reports.length >= 1){
                        testRunner.displayTestResults(result.reports);
                    }
                }
            }
        });
    }

    this.mergeAndDisplayLogs = function(logs){
        for(l in logs){
            var thisLog = logs[l];
            for(line in thisLog){
                var thisLine = thisLog[line];
                // is this line already in the log area?
                var lineIsDisplayed = false;
                $("#testResultLogs div.log-line").each(function(){
                    if($(this).html() === thisLine){
                        lineIsDisplayed = true;
                    }
                });
                if(!lineIsDisplayed){
                    $("#testResultLogs").append("<div class='log-line'>"+thisLine+"</div>");

                    $('.modal-body').scrollTop($('.modal-body')[0].scrollHeight);
                }
            }
        }
    }

    this.displayTestResults = function(reports){
        for(r in reports){
            let thisReport = reports[r];
            let report = $("<div class='report-result'></div>");
            let resultIcon = Main.Utils.getResultIcon(thisReport.result);       
            report.append('<div><strong>Result:</strong> '+thisReport.result+ ' ' + resultIcon + '</div>');
            report.append('<div><strong>Errors:</strong></div>');
            if(thisReport.errors.length){
                let errorsList = $("<ol id='resultErrorList' style='margin-left: 20px'></ol>");
                for(s in thisReport.errors){
                    let thisError = thisReport.errors[s];
                    let msg = thisError.message;
                    errorsList.append('<li>'+msg+'</li>');
                }
                report.append(errorsList);
            }
            report.append('<div><strong>Elapsed Time:</strong> ' + thisReport.test_elapsed_time + '</div>');
            report.append('<div><strong>Browser:<strong> ' + thisReport.browser + '</div>');
            report.append('<div><strong>Steps:</strong></div>');
            if(thisReport.steps.length){
                let stepsList = $("<ol id='resultStepsList' style='margin-left: 20px'></ol>")
                for(s in thisReport.steps){
                    var thisStep = thisReport.steps[s];
                    let step = $('<li>' + thisStep.message + '</li>')
                    if(thisStep.error){
                        step.append(' - ' + thisStep.error.message)
                    }
                    if(thisStep.screenshot){
                        let guid = Main.Utils.guid();
                        let screenshotUrl = `/test/screenshot/${project}/${thisReport.full_name}/${thisReport.execution}/${thisReport.test_set}/${thisStep.screenshot}/`;
                        var screenshotIcon = `
                        <span class="cursor-pointer glyphicon glyphicon-picture" aria-hidden="true"
                            data-toggle="collapse" data-target="#${guid}"
                            aria-expanded="false" aria-controls="${guid}"></span>
                        <div class="collapse text-center" id="${guid}">
                            <img class="step-screenshot cursor-pointer" style="width: 100%"
                                src="${screenshotUrl}" onclick="Main.ReportUtils.expandImg(event);">
                        </div>`;
                        step.append(' ' + screenshotIcon)
                    }
                    stepsList.append(step);
                }
                report.append(stepsList)
             }
            $("#testResults").html(report.html());
        }
        $('.modal-body').scrollTop($('.modal-body')[0].scrollHeight);
    }

}


var dataTable = new function(){

    this.addRowToDataTable = function(){
        var amountOfColumns = $("#dataTable thead tr th").length -1;
        var amountOfRows = $("#dataTable tbody tr").length;
        var newCells = "";
        for(var i = 0; i < amountOfColumns; i++){
            newCells += "<td> \
                            <div class='input-group'> \
                                <input class='form-control' type='text'> \
                            </div> \
                        </td>";
        }
        
        $("#dataTable tbody").append(
            "<tr> \
                <th scope='row' class='index'>"+(amountOfRows+1)+"</th> \
                " + newCells + " \
            </tr>");
    }

    this.addColumnToDataTable = function(){
        $("#dataTable thead tr").append(
            "<th> \
                <div class='input-group'> \
                    <input class='form-control' type='text' onchange='dataTableHeaderInputChange()'> \
                </div> \
            </th>"
        );

        $("#dataTable tbody tr").each(function(){
            $(this).append(
                "<td> \
                    <div class='input-group'> \
                        <input class='form-control' type='text'> \
                    </div> \
                </td>"
            );
        });
    }

    this.getData = function(){
        var testData = []
        var headerInputs = $("#dataTable thead input")    
        var tableRows = $("#dataTable tbody tr");
        tableRows.each(function(){
            var currentRow = $(this);
            var rowCells = currentRow.find("td input");
            var rowDict = {}
            rowCells.each(function(i){
                if($(headerInputs[i]).val().length > 0){
                    rowDict[$(headerInputs[i]).val()] = $(this).val();
                }
            });
            if(!jQuery.isEmptyObject(rowDict)){
                testData.push(rowDict)
            }
        });
        // empty values are allowed but only for one row of data
        var tempTestData = [];
        for(var i = 0; i <= testData.length - 1; i++){
            var allEmpty = true;
            for(key in testData[i]){
                if(testData[i][key].length > 0){
                    allEmpty = false
                }
            }
            if(!allEmpty){
                tempTestData.push(testData[i])
            }
        }
        testData = tempTestData;
        return testData
    }
}


var header = new function(){

    this.startEditTestName = function(){
        $("#testNameInput input").val(fullTestCaseName);
        $("#testNameInput").show();
        $("#testName").hide();
        $("#testNameInput input").focus();
        $("#testNameInput input").unbind('blur');
        $("#testNameInput input").unbind('keyup');
        $("#testNameInput input").on('blur', function(e){
            header.saveEdition();
        });
        $("#testNameInput input").on('keyup', function(e){
            if(e.keyCode == '13') $(this).blur();
        });
    };

    this.saveEdition = function(){
        var newTestNameValue = $("#testNameInput input").val();

        newTestNameValue = newTestNameValue.trim();

        if(newTestNameValue == fullTestCaseName){
            $("#testNameInput").hide();
            $("#testName").show();
            return
        }
        // TO DO: validate
        newTestNameValue = newTestNameValue.replace(' ', '_');

        $.ajax({
            url: "/rename_element/",
            data: {
                 "project": project,
                 "elemType": 'test',
                 "fullFilename": fullTestCaseName,
                 "newFullFilename": newTestNameValue,
                 
             },
             dataType: 'json',
             type: 'POST',
             success: function(error) {
                if(error.length == 0){
                    fullTestCaseName = newTestNameValue;
                    $("#testNameInput input").val('');
                    $("#testNameInput").hide();
                    $("#testName").html(newTestNameValue).show();

                    var new_url = "/project/" + project + "/test/" + newTestNameValue + "/";
                    window.history.pushState("object or string", "", new_url);
                }
                else{
                    Main.Utils.toast('error', error, 2000);
                    $("#testNameInput").hide();
                    $("#testName").show();
                }
             },
         });
    };
}

var testManager = new function(){

    this.setFileLockInterval = function(){
        testManager.lockFile();
        setInterval(function(){testManager.lockFile();}, 60000);
    }

    this.lockFile = function(){
        $.ajax({
            url: "/lock_file/",
            data: {
                 "project": project,
                 "userName": username,
                 "fullTestCaseName": fullTestCaseName
             },
             dataType: 'json',
             type: 'POST',
             success: function(result) {}
         });
    }

    this.setUnlockFileOnUnload = function(){
        $( window ).bind('beforeunload', function() {
            testManager.unlockFile();
        });
    }

    this.unlockFile = function(){
        $.ajax({
            url: "/unlock_file/",
            data: {
                 "project": project,
                 "userName": username,
                 "fullTestCaseName": fullTestCaseName
             },
             dataType: 'json',
             type: 'POST',
             success: function(result) {}
         });
    }

}
