let codeEditor;


$(document).ready(function() {

    if(codeError !== null){
        $(".error-container").show();
        $(".error-container pre").html(codeError);
    }
    codeEditor = CodeMirror($("#codeEditorContainer")[0], {
        value: suiteCode,
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

    if(Global.user.projectWeight < Main.PermissionWeightsEnum.standard){
        codeEditor.setOption('readOnly', 'nocursor')
    }

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
        saveSuite();
    }
    codeEditor.markClean();
    // redirect to gui view
    let pathname = window.location.pathname;
    window.location.replace(pathname.replace('/code/', '/'));
}


function saveSuite(){
    let content = codeEditor.getValue();
    xhr.put('/api/suite/code/save', {
        project: Global.project,
        suiteName: suiteName,
        content: content
    }, data => {
        codeEditor.markClean();
        Main.Utils.toast('success', `Suite ${suiteName} saved`, 3000);
        if(data.error != null) {
            $(".error-container").show();
            $(".error-container pre").html(data.error);
            Main.Utils.toast('info', "There are errors in the code", 3000)
        } else {
            $(".error-container").hide();
            $(".error-container pre").html('');
        }
    })
}


function watchForUnsavedChanges(){
    window.addEventListener("beforeunload", function (e) {
        if(!codeEditor.isClean()){
            let confirmationMessage = 'There are unsaved changes';
            (e || window.event).returnValue = confirmationMessage; //Gecko + IE
            return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
        }
    });
}