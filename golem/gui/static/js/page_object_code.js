var codeEditor;


$(document).ready(function() {

    if(codeError.length > 0){
        $(".error-container").show();
        $(".error-container pre").html(codeError);
    }      

    codeEditor = CodeMirror($("#codeEditorContainer")[0], {
        value: pageObjectCode,
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


function loadGuiView(){
    if(!codeEditor.isClean()){
        savePageObject();
    }

    codeEditor.markClean();

    // redirect to gui view
    //window.location.replace("/project/"+project+"/page/"+pageObjectName+"/");
    var pathname = window.location.pathname;
    window.location.replace(pathname.replace('/code/', '/'));
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
            codeEditor.markClean();
            utils.toast('success', "Page "+pageObjectName+" saved", 3000);
            if(data.error.length > 0){
                $(".error-container").show();
                $(".error-container pre").html(data.error);
            }
            else{
                $(".error-container").hide();
                $(".error-container pre").html('');
            }
        },
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