
var codeEditor;
var unsavedChanges = false;

$(document).ready(function() {

    codeEditor = CodeMirror($("#codeEditorContainer")[0], {
      value: testCaseCode,
      mode:  "python",
      //theme: "default",
      lineNumbers: true,
      styleActiveLine: true,
      matchBrackets: true
    });

    // set unsaved changes watcher
    watchForUnsavedChanges();

});


function saveTestCase(){
    if(!unsavedChanges && codeEditor.isClean()){
        return
    }

    var content = codeEditor.getValue();

    var testData = [];
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

    var data = {
        'content': content,
        'testData': testData,
        'project': project,
        'testCaseName': fullTestCaseName
    }

    $.ajax({
        url: "/save_test_case_code/",
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        success: function(data) {
            unsavedChanges = false;
            toastr.options = {
                "positionClass": "toast-top-center",
                "timeOut": "3000",
                "hideDuration": "100"
            }
            toastr.success("Test case "+testCaseName+" saved");
            unsavedChanges = false;
            codeEditor.markClean();
        },
        error: function() {
        }
    });
}


function runTestCase(){
    toastr.options = {
        "positionClass": "toast-top-center",
        "timeOut": "3000",
        "hideDuration": "100"}
    toastr.info('Running test case ' + testCaseName);
    $.ajax({
        url: "/run_test_case/",
        data: {
             "project": project,
             "testCaseName": fullTestCaseName,
         },
         dataType: 'json',
         type: 'POST',
         success: function(data) {
            var timestamp = data;
            checkTestCaseResult(project, fullTestCaseName, timestamp);
         },
         error: function() {}
     });
}


function addColumnToDataTable(){
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

function addRowToDataTable(){
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


function watchForUnsavedChanges(){
    
    $("#dataTable").on("change keyup paste", function(){
        unsavedChanges = true;
    });

    window.addEventListener("beforeunload", function (e) {
        if(unsavedChanges || !codeEditor.isClean()){
            var confirmationMessage = 'There are unsaved changes';
            (e || window.event).returnValue = confirmationMessage; //Gecko + IE
            return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
        }
    });
}


function checkTestCaseResult(project, fullTestCaseName, timestamp){

    $("#testRunModal").modal("show");

    $("#testRunModal .modal-title").html('Running Test Case');

    $("#loaderContainer").show();

    $("#testResultContainer").html('');

    checkAndRecheckStatus(project, fullTestCaseName, timestamp);
}

function checkAndRecheckStatus(project, fullTestCaseName, timestamp){

    $.ajax({
        url: "/check_test_case_run_result/",
        data: {
             "project": project,
             "testCaseName": fullTestCaseName,
             "timestamp": timestamp
         },
         dataType: 'json',
         type: 'POST',
         success: function(data) {
            if(data.status == 'not_complete'){
                setTimeout(function(){
                    checkAndRecheckStatus(project, fullTestCaseName, timestamp);
                }, 2000, project, fullTestCaseName, timestamp);
            }
            else{
                $("#loaderContainer").hide();

                $("#testRunModal .modal-title").html('Result');

                $("#testResultContainer").html('');

                $("#testResultContainer").append('<span><strong>Result:</strong> ' + data.report_data.result + '</span><br>');
                $("#testResultContainer").append('<span><strong>Error:</strong> ' + data.report_data.short_error + '</span><br>');
                $("#testResultContainer").append('<span><strong>Elapsed Time:</strong> ' + data.report_data.test_elapsed_time + '</span><br>');
                $("#testResultContainer").append('<span><strong>Browser:<strong> ' + data.report_data.browser + '</span><br>');
                $("#testResultContainer").append('<span><strong>Steps:</strong></span>');
                $("#testResultContainer").append("<ol style='margin-left: 20px'></ol>");
                for(s in data.report_data.steps){
                    $("#testResultContainer ol").append('<li>' + data.report_data.steps[s] + '</li>')
                }
                $("#testResultContainer").append('</ol>')
            }
         },
         error: function() {}
     });
}


function loadGuiView(){
    if(!codeEditor.isClean()){
        saveTestCase();
    }

    codeEditor.markClean();
    unsavedChanges = false;

    // redirect to gui view
    window.location.replace("/p/"+project+"/test/"+fullTestCaseName+"/");
}

