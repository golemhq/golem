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


function saveEnvironments(){
    var environments = environmentsEditor.getValue();

    $.ajax({
        url: "/api/project/environments/save",
        data: JSON.stringify({
                "project": Global.project,
                "environmentData": environments
            }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'PUT',
        success: function(result) {
            if(result.error.length == 0){
                Main.Utils.toast('success', "Environments saved", 2000);
                environmentsEditor.markClean();
            }
            else{
                Main.Utils.toast('error', result.error, 2000);
            }
        }
    });
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