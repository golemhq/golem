
let codeEditor;

const PageCode = new function() {

    this.file;
    this.codeEditor;

    this.initialize = function(file, pageCode, codeError) {
        this.file = file;

        if(codeError !== null) {
            $(".error-container").show();
            $(".error-container pre").html(codeError);
        }
        this.codeEditor = CodeMirror($("#codeEditorContainer")[0], {
            value: pageCode,
            mode:  "python",
            lineNumbers: true,
            styleActiveLine: true,
            matchBrackets: true,
            indentUnit: 4,
            indentWithTabs: false,
            extraKeys: {
                Tab: this.convertTabToSpaces
            }
        });
        codeEditor = this.codeEditor;

        if(Global.user.projectWeight < Main.PermissionWeightsEnum.standard)
            this.codeEditor.setOption('readOnly', 'nocursor')

        // set unsaved changes watcher
        this.watchForUnsavedChanges()
    }

    this.convertTabToSpaces = function(cm) {
      if (cm.somethingSelected()) {
        cm.indentSelection("add");
      } else {
        cm.replaceSelection(cm.getOption("indentWithTabs")? "\t":
          Array(cm.getOption("indentUnit") + 1).join(" "), "end", "+input");
      }
    }

    this.loadGuiView = function() {
        if(!this.codeEditor.isClean())
            this.save()
        this.codeEditor.markClean();
        // redirect to gui view
        let pathname = window.location.pathname;
        window.location.replace(pathname.replace('/code/', '/'));
    }

    this.save = function() {
        let content = this.codeEditor.getValue();
        xhr.put('/api/page/code/save', {
            project: this.file.project,
            pageName: this.file.fullName,
            content: content
        }, result => {
            this.codeEditor.markClean();
            Main.Utils.toast('success', `Page ${this.file.name} saved`, 3000);
            if(result.error != null) {
                $(".error-container").show();
                $(".error-container pre").html(result.error);
                Main.Utils.toast('info', 'There are errors in the code', 3000)
            } else {
                $(".error-container").hide();
                $(".error-container pre").html('');
            }
        })
    }

    this.watchForUnsavedChanges = function() {
        window.addEventListener("beforeunload", e => {
            if(this.hasUnsavedChanges()) {
                var confirmationMessage = 'There are unsaved changes';
                (e || window.event).returnValue = confirmationMessage; //Gecko + IE
                return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
            }
        })
    }

    this.hasUnsavedChanges = function(){
        return !this.codeEditor.isClean()
    }
}