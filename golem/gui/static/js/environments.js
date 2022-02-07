let environmentsEditor = null;


$(document).ready(function() {
    environmentsEditor = CodeMirror($("#environmentsContainer")[0], {
        value: environmentData,
        mode: "application/ld+json",
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        lineWrapping: true
    });

    if(Global.user.projectWeight < Main.PermissionWeightsEnum.admin){
        environmentsEditor.setOption('readOnly', 'nocursor')
    }

    // set unsaved changes watcher
    watchForUnsavedChanges();
});


function saveEnvironments() {
    let environments = environmentsEditor.getValue();
    xhr.put('/api/project/environments/save', {
        'project': Global.project,
        'environmentData': environments
    }, result => {
        if(result.error.length) {
            Main.Utils.toast('error', result.error, 2000);
        } else {
            Main.Utils.toast('success', "Environments saved", 2000);
            environmentsEditor.markClean();
        }
    })
}


function watchForUnsavedChanges(){
    window.addEventListener("beforeunload", function (e) {
        if(!environmentsEditor.isClean()){
            var confirmationMessage = 'There are unsaved changes';
            (e || window.event).returnValue = confirmationMessage; //Gecko + IE
            return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
        }
    });
}