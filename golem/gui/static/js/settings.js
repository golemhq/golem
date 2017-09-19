var projectSettingsEditor;
var globalSettingsEditor;


$(document).ready(function() {      

   projectSettingsEditor = CodeMirror($("#settingsContainer")[0], {
      value: settingsCode,
      mode: "application/ld+json",
      lineNumbers: true,
      styleActiveLine: true,
      matchBrackets: true,
      autoCloseBrackets: true,
      lineWrapping: true
    });

   globalSettingsEditor = CodeMirror($("#globalSettingsContainer")[0], {
      value: globalSettingsCode,
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


function saveSettings(){
    var projectSettings = projectSettingsEditor.getValue();
    var globalSettings = globalSettingsEditor.getValue();

    $.ajax({
        url: "/save_settings/",
        data: JSON.stringify({
                "project": project,
                "projectSettings": projectSettings,
                "globalSettings": globalSettings
            }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        success: function(data) {
            console.log(data);
            if(data === 'ok'){
                toastr.options = {
                    "positionClass": "toast-top-center",
                    "timeOut": "2000",
                    "hideDuration": "100"}
                toastr.success("Settings saved");

                codeEditor.markClean();
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
        if(!(projectSettingsEditor.isClean() && globalSettingsEditor.isClean())){
            var confirmationMessage = 'There are unsaved changes';
            (e || window.event).returnValue = confirmationMessage; //Gecko + IE
            return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
        }
    });
}