let codeEditor;

const SuiteCode = new function() {

    this.file;
    this.codeEditor;

    this.initialize = function(file, code, codeError) {
        this.file = file;
        if(codeError !== null) {
            $(".error-container").show();
            $(".error-container pre").html(codeError);
        }
        this.codeEditor = CodeMirror($("#codeEditorContainer")[0], {
            value: code,
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
        if(Global.user.projectWeight < Main.PermissionWeightsEnum.standard) {
            codeEditor.setOption('readOnly', 'nocursor')
        }
        // set unsaved changes watcher
        this.watchForUnsavedChanges();
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
        xhr.put('/api/suite/code/save', {
            project: this.file.project,
            suiteName: this.file.fullName,
            content: codeEditor.getValue()
        }, result => {
            codeEditor.markClean();
            Main.Utils.toast('success', `Suite ${this.file.fullName} saved`, 3000);
            if(result.error != null) {
                $(".error-container").show();
                $(".error-container pre").html(result.error);
                Main.Utils.toast('info', "There are errors in the code", 3000)
            } else {
                $(".error-container").hide();
                $(".error-container pre").html('');
            }
        })
    }

    // TODO, defined also in suite.js
    this.run = function() {
        let project = this.file.project;
        let fullName = this.file.fullName;

        function _runSuite() {
            xhr.post('/api/suite/run', {
                project: project,
                suite: fullName,
            }, timestamp => {
                let url = `/report/project/${project}/suite/${fullName}/${timestamp}/`;
                let msg = `Running suite ${fullName} - <a href="${url}"><strong>open</strong></a>`;
                Main.Utils.toast('info', msg, 15000)
            })
        }

        if(this.unsavedChanges)
            this.save(_runSuite())
        else
            _runSuite()
    }

    this.watchForUnsavedChanges = function() {
        window.addEventListener("beforeunload", e => {
            if(!this.codeEditor.isClean()){
                let confirmationMessage = 'There are unsaved changes';
                (e || window.event).returnValue = confirmationMessage; //Gecko + IE
                return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
            }
        });
    }
}