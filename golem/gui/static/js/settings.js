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


function saveSettings() {
    let settings = settingsEditor.getValue();
    xhr.put('/api/settings/project/save', {
        'project': Global.project,
        settings
    }, data => {
        Main.Utils.toast('success', "Settings saved", 2000);
        settingsEditor.markClean();
    })
}

function saveGlobalSettings() {
    let settings = settingsEditor.getValue();
    xhr.put('/api/settings/global/save', {settings}, data => {
        Main.Utils.toast('success', "Settings saved", 2000);
        settingsEditor.markClean();
    })
}


function watchForUnsavedChanges() {
    window.addEventListener("beforeunload", function (e) {
        let settingsIsClean = settingsEditor.isClean();
        if(!settingsIsClean) {
            let confirmationMessage = 'There are unsaved changes';
            (e || window.event).returnValue = confirmationMessage;
            return confirmationMessage
        }
    });
}