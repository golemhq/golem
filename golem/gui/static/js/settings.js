let settingsEditor = null;


$(document).ready(function() {
    settingsEditor = CodeMirror($("#settingsContainer")[0], {
        value: settingsJson,
        mode: "application/ld+json",
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        lineWrapping: true
    })

    if(Global.user.projectWeight < Main.PermissionWeightsEnum.admin){
        settingsEditor.setOption('readOnly', 'nocursor')
    }

    // set unsaved changes watcher
    watchForUnsavedChanges();
});


function saveSettings(){
    let settings = settingsEditor.getValue();
    $.ajax({
        url: "/api/settings/project/save",
        data: JSON.stringify({
            "project": Global.project,
            "settings": settings
        }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'PUT',
        success: function(data) {
            Main.Utils.toast('success', "Settings saved", 2000);
            settingsEditor.markClean();
        },
    });
}

function saveGlobalSettings(){
    let globalSettings = settingsEditor.getValue();

    $.ajax({
        url: "/api/settings/global/save",
        data: JSON.stringify({
            "settings": globalSettings
        }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'PUT',
        success: function(data) {
            Main.Utils.toast('success', "Settings saved", 2000);
            settingsEditor.markClean();
        },
    });
}


function watchForUnsavedChanges(){
    window.addEventListener("beforeunload", function (e) {
        let settingsIsClean = settingsEditor.isClean();
        if(!settingsIsClean){
            let confirmationMessage = 'There are unsaved changes';
            (e || window.event).returnValue = confirmationMessage;
            return confirmationMessage
        }
    });
}