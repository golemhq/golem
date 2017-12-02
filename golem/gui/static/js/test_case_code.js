
var codeEditor;
var unsavedChanges = false;


$(document).ready(function() {

    if(codeError.length > 0){
        $(".error-container").show();
        $(".error-container pre").html(codeError);
    }

    codeEditor = CodeMirror($("#codeEditorContainer")[0], {
        value: testCaseCode,
        mode:  "python",
        //theme: "default",
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,
        indentUnit: 4,
        indentWithTabs: false,
        extraKeys: {
            Tab: convertTabToSpaces
        }
    });

    // set unsaved changes watcher
    watchForUnsavedChanges();
    
});


function convertTabToSpaces(cm) {
  if (cm.somethingSelected()) {
    cm.indentSelection("add");
  } else {
    cm.replaceSelection(cm.getOption("indentWithTabs")? "\t":
      Array(cm.getOption("indentUnit") + 1).join(" "), "end", "+input");
  }
}

function saveTestCase(){
    // if(!unsavedChanges && codeEditor.isClean()){
    //     return
    // }
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
            codeEditor.markClean();
            utils.toast('success', "Test "+testCaseName+" saved", 3000);
            if(data.error.length > 0){
                $(".error-container").show();
                $(".error-container pre").html(codeError);
                utils.toast('info', "There are errors in the code", 3000)
            }
            else{
                $(".error-container").hide();
                $(".error-container pre").html('');
            }
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
    window.location.replace("/project/"+project+"/test/"+fullTestCaseName+"/");
}

