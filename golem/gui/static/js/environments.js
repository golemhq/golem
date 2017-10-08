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
        success: function(data) {
            if(data.result === 'ok'){
                toastr.options = {
                    "positionClass": "toast-top-center",
                    "timeOut": "2000",
                    "hideDuration": "100"}
                toastr.success("Settings saved");
                environmentsEditor.markClean();
            }
            else{
                toastr.options = {
                    "positionClass": "toast-top-center",
                    "timeOut": "3000",
                    "hideDuration": "100"}
                toastr.error(data);
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