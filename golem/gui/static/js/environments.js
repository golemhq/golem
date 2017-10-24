var environmentsEditor = null;


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

    // set unsaved changes watcher
    watchForUnsavedChanges();
});


function saveEnvironments(){
    var environments = environmentsEditor.getValue();

    $.ajax({
        url: "/save_environments/",
        data: JSON.stringify({
                "project": project,
                "environmentData": environments
            }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        success: function(error) {
            if(error.length == 0){
                utils.toast('success', "Settings saved", 2000);
                environmentsEditor.markClean();
            }
            else{
                utils.toast('error', error, 2000);
            }
        },
        error: function() {
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