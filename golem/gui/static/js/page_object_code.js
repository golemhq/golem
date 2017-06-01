var codeEditor;


$(document).ready(function() {      

   codeEditor = CodeMirror($("#codeEditorContainer")[0], {
      value: pageObjectCode,
      mode:  "python",
      //theme: "default",
      lineNumbers: true,
      styleActiveLine: true,
      matchBrackets: true
    });

    // set unsaved changes watcher
    watchForUnsavedChanges();
});


function loadGuiView(){
    if(!codeEditor.isClean()){
        savePageObject();
    }

    codeEditor.markClean();

    // redirect to gui view
    window.location.replace("/p/"+project+"/page/"+pageObjectName+"/");
}


function savePageObject(){
    var content = codeEditor.getValue();

    $.ajax({
        url: "/save_page_object_code/",
        data: JSON.stringify({
                "project": project,
                "pageObjectName": pageObjectName,
                "content": content
            }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        success: function(data) {
            toastr.options = {
                "positionClass": "toast-top-center",
                "timeOut": "3000",
                "hideDuration": "100"}
            toastr.success("Page "+pageObjectName+" saved");

            codeEditor.markClean();
        },
        error: function() {
        }
    });
}


function watchForUnsavedChanges(){
    window.addEventListener("beforeunload", function (e) {
        if(!codeEditor.isClean()){
            var confirmationMessage = 'There are unsaved changes';
            (e || window.event).returnValue = confirmationMessage; //Gecko + IE
            return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
        }
    });
}