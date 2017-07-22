
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

    // get data from table
    var testData = dataTable.getData();

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
            toastr.success("Test "+testCaseName+" saved");
            unsavedChanges = false;
            codeEditor.markClean();
        },
        error: function() {
        }
    });
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


function loadGuiView(){
    if(!codeEditor.isClean()){
        saveTestCase();
    }

    codeEditor.markClean();
    unsavedChanges = false;

    // redirect to gui view
    window.location.replace("/p/"+project+"/test/"+fullTestCaseName+"/");
}

