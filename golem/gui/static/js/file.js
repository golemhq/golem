

class File {

    constructor(type, project, name, fullName) {
        this.type = type;
        this.project = project;
        this.name = name;
        this.fullName = fullName
    }

    startInlineNameEdition() {
        $("#filenameInput input").val(this.fullName);
        $("#filenameInput").show();
        $("#fileName").hide();
        $("#filenameInput input").focus();
        $("#filenameInput input").unbind('blur');
        $("#filenameInput input").unbind('keyup');
        $("#filenameInput input").on('blur', (e) => this.saveInlineNameEdition());
        $("#filenameInput input").on('keyup', (e) => {if(e.keyCode == '13') e.target.blur()});
    };

    saveInlineNameEdition() {
        let newTestNameValue = $("#filenameInput input").val().trim();
        if(newTestNameValue == this.fullName){
            $("#filenameInput").hide();
            $("#fileName").show();
            return
        }
        let renameUrl = this.renameUrl(this.type);
        xhr.post(renameUrl, {
            project: this.project,
            fullFilename: this.fullName,
            newFullFilename: newTestNameValue,
        }, (result) => {
            if(result.errors.length == 0){
                document.title = document.title.replace(Test.fullName, newTestNameValue);
                this.fullName = newTestNameValue;
                $("#filenameInput input").val('');
                $("#filenameInput").hide();
                $("#fileName").html(newTestNameValue).show();
                let new_url = `/project/${Global.project}/test/${newTestNameValue}/`;
                window.history.pushState("object or string", "", new_url);
                Main.Utils.toast('success', 'File was renamed', 2000);
            }
            else{
                result.errors.forEach(function(error){
                    Main.Utils.toast('error', error, 3000);
                });
                $("#filenameInput").hide();
                $("#fileName").show();
            }
        })
    }

    renameUrl(fileType) {
        if(fileType == Main.FILE_TYPES.test)
            return '/api/test/rename'
        else if(fileType == Main.FILE_TYPES.suite)
            return '/api/suite/rename'
        else if(fileType == Main.FILE_TYPES.page)
            return '/api/page/rename'
    }
}