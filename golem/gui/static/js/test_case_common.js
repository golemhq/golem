

var testRunner = new function(){
    
    this.runTestCase = function(){
        if(unsavedChanges)
            saveTestCase(true);
        else
            testRunner._doRunTestCase();
    };

    this._doRunTestCase = function(){
        toastr.options = {
            "positionClass": "toast-top-center",
            "timeOut": "3000",
            "hideDuration": "100"}
        toastr.info('Running test ' + testCaseName);
        $.ajax({
            url: "/run_test_case/",
            data: {
                 "project": project,
                 "testCaseName": fullTestCaseName,
             },
             dataType: 'json',
             type: 'POST',
             success: function(timestamp) {
                testRunner.checkTestCaseResult(project, fullTestCaseName, timestamp);
             },
             error: function() {}
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
             },
             error: function() {}
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
            var thisReport = reports[r];
            var report = $("<div class='report-result'></div>");
            if(thisReport.result === 'pass'){
                var resultIcon = '<span class="pass-icon"><span class="glyphicon glyphicon-ok-circle" aria-hidden="true"></span></span>';
            }
            else{
                var resultIcon = '<span class="fail-icon"><span class="glyphicon glyphicon-remove-circle" aria-hidden="true"></span></span>';
            }
            report.append('<span><strong>Result:</strong> ' + thisReport.result + ' ' + resultIcon + '</span><br>');
            report.append('<span><strong>Error:</strong> ' + thisReport.short_error + '</span><br>');
            report.append('<span><strong>Elapsed Time:</strong> ' + thisReport.test_elapsed_time + '</span><br>');
            report.append('<span><strong>Browser:<strong> ' + thisReport.browser + '</span><br>');
            report.append('<span><strong>Steps:</strong></span>');
            report.append("<ol style='margin-left: 20px'></ol>");
            for(s in thisReport.steps){
                var thisStep = thisReport.steps[s];
                

                if(thisStep.screenshot){
                    var msg = "<span class='hand-icon' data-toggle='collapse' data-target='#"+thisStep.screenshot+"' \
                        aria-expanded='false' aria-controls='"+thisStep.screenshot+"'>'"+thisStep.message+"' \
                        <span class='glyphicon glyphicon-picture' aria-hidden='true'></span></span> \
                    <div class='collapse text-center' id='"+ thisStep.screenshot + "'> \
                        <img class='step-screenshot hand-icon' style='width: 100%;' src='/test/screenshot/"+ project +"/"+ thisReport.name +"/"+thisReport.execution+ "/"+thisReport.test_set+ "/"+ thisStep.screenshot +"/' onclick='expandImg(event);'> \
                    </div>";
                }
                else{
                    var msg = thisStep.message;
                }

                report.find("ol").append('<li>' + msg + '</li>');
            }
            report.append('</ol>');
            $("#testResults").append(report);
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
                    <input class='form-control' type='text'> \
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
        var tempTestData = [testData[0]];
        for(var i = 1; i <= testData.length - 1; i++){
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

        $("#testNameInput input").on('blur', function(e){
            header.saveEdition();
        });

        $("#testNameInput input").on('keyup', function(e){
            if(e.keyCode == '13') $(this).blur();
        });
    }

    this.saveEdition = function(){
        var newTestNameValue = $("#testNameInput input").val();
        console.log(newTestNameValue, fullTestCaseName);
        if(newTestNameValue == fullTestCaseName){
            $("#testNameInput").hide();
            $("#testName").show();
            return
        }
        // TO DO: validate

        $.ajax({
            url: "/change_test_name/",
            data: {
                 "project": project,
                 "testName": fullTestCaseName,
                 "newTestName": newTestNameValue
             },
             dataType: 'json',
             type: 'POST',
             success: function(result) {
                if(result == 'ok'){
                    fullTestCaseName = newTestNameValue;
                    $("#testNameInput input").val('');
                    $("#testNameInput").hide();
                    $("#testName").html(newTestNameValue).show();

                    var new_url = "/p/" + project + "/test/" + newTestNameValue + "/";
                    window.history.pushState("object or string", "", new_url);
                }
                else{
                    $("#testNameInput").hide();
                    $("#testName").show();
                }
             },
             error: function() {}
         });

    }

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
