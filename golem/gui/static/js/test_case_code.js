
var codeEditor;
var unsavedChanges = false;


$(document).ready(function() {

    if(codeError != null){
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
            Tab: TestCommon.Utils.convertTabToSpaces
        }
    });

    if(Global.user.projectWeight < Main.PermissionWeightsEnum.standard){
        codeEditor.setOption('readOnly', 'nocursor')
    }

    // set unsaved changes watcher
    watchForUnsavedChanges();
    
});


function saveTestCase(callback){
    var content = codeEditor.getValue();
    // get data from table
    var testData = TestCommon.DataTable.getData();
    var data = {
        'content': content,
        'testData': testData,
        'project': Global.project,
        'testName': fullTestCaseName
    }
    $.ajax({
        url: "/api/test/code/save",
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'PUT',
        success: function(data) {
            unsavedChanges = false;
            codeEditor.markClean();
            Main.Utils.toast('success', `Test ${testCaseName} saved`, 3000);
            if(data.error != null){
                $(".error-container").show();
                $(".error-container pre").html(data.error);
                Main.Utils.toast('info', "There are errors in the code", 3000)
            }
            else{
                $(".error-container").hide();
                $(".error-container pre").html('');
                if(callback != undefined){
                    callback()
                }
            }
        }
    });
}


function watchForUnsavedChanges(){
    
    $("#dataTable").on("change keyup paste", function(){
        unsavedChanges = true;
    });

    window.addEventListener("beforeunload", function (e) {
        if(hasUnsavedChanges()){
            var confirmationMessage = 'There are unsaved changes';
            (e || window.event).returnValue = confirmationMessage; //Gecko + IE
            return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
        }
    });
}


function runTest(){
    let run = () => Main.TestRunner.runTest(Global.project, fullTestCaseName);
    if(hasUnsavedChanges())
        saveTestCase(run)
    else
        run()
}


function hasUnsavedChanges(){
    return !codeEditor.isClean() || unsavedChanges
}