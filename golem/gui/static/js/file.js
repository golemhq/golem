

class File {

    constructor(type, project, name, fullName, isCodeView) {
        this.type = type;
        this.project = project;
        this.name = name;
        this.fullName = fullName;
        this.isCodeView = isCodeView || false;
    }

    startInlineNameEdition() {
        Main.Utils.startGenericInlineName($("#filenameInput"), $("#fileName"), this.fullName, () => this.saveInlineNameEdition())
    };

    saveInlineNameEdition() {
        let newNameValue = $("#filenameInput input").val().trim();
        if(newNameValue == this.fullName){
            $("#filenameInput").hide();
            $("#fileName").show();
            return
        }
        let renameUrl = this.renameUrl(this.type);
        xhr.post(renameUrl, {
            project: this.project,
            fullFilename: this.fullName,
            newFullFilename: newNameValue,
        }, (result) => {
            if(result.errors.length == 0){
                document.title = document.title.replace(this.fullName, newNameValue);
                this.fullName = newNameValue;
                $("#filenameInput input").val('');
                $("#filenameInput").hide();
                $("#fileName").html(newNameValue).show();
                window.history.pushState("object or string", "", this.fileUrl());
                Main.Utils.toast('success', 'File was renamed', 2000);
            } else {
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

    fileUrl(fileType, project, fullName) {
        let url = '';
        if(this.type == Main.FILE_TYPES.test)
            url = `/project/${this.project}/test/${this.fullName}/`
        else if(this.type == Main.FILE_TYPES.page)
            url = `/project/${this.project}/page/${this.fullName}/`
        else if(this.type == Main.FILE_TYPES.suite)
            url = `/project/${this.project}/suite/${this.fullName}/`
        if(this.isCodeView)
            url += 'code/'
        return url
    }
}