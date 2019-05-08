var projectSettingsEditor = null;
var globalSettingsEditor = null;


$(document).ready(function() {    
    if(settingsCode != null){
        $("#projectSettingsContainer").show();
        projectSettingsEditor = CodeMirror($("#projectSettingsContainer>.codeEditorContainer")[0], {
          value: settingsCode,
          mode: "application/ld+json",
          lineNumbers: true,
          styleActiveLine: true,
          matchBrackets: true,
          autoCloseBrackets: true,
          lineWrapping: true
      })
    }

    globalSettingsEditor = CodeMirror($("#globalSettingsContainer>.codeEditorContainer")[0], {
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

    var projectSettings = null;
    if(projectSettingsEditor != null){
        projectSettings = projectSettingsEditor.getValue();
    }
    var globalSettings = globalSettingsEditor.getValue();

    $.ajax({
        url: "/api/settings/save",
        data: JSON.stringify({
            "project": project,
            "projectSettings": projectSettings,
            "globalSettings": globalSettings
        }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'PUT',
        success: function(data) {
            Main.Utils.toast('success', "Settings saved", 2000);
            if(projectSettingsEditor != null){ projectSettingsEditor.markClean() }
            globalSettingsEditor.markClean();
        },
    });
}


function watchForUnsavedChanges(){
    window.addEventListener("beforeunload", function (e) {
        if(projectSettingsEditor != null)
            var projectSettingsIsClean = projectSettingsEditor.isClean();
        else
            var projectSettingsIsClean = true;
        var globalSettingsIsClean = globalSettingsEditor.isClean();
        if(!globalSettingsIsClean || !projectSettingsIsClean){
            var confirmationMessage = 'There are unsaved changes';
            (e || window.event).returnValue = confirmationMessage; //Gecko + IE
            return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
        }
    });
}