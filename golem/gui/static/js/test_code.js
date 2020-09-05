
let codeEditor;


const TestCode = new function() {

    this.codeEditor = undefined;
    this.unsavedChanges = false;

    this.initialize = function(file, testCode, codeError) {
        this.file = file;
        if(codeError != null){
            $(".error-container").show();
            $(".error-container pre").html(codeError);
        }
        this.codeEditor = CodeMirror($("#codeEditorContainer")[0], {
            value: testCode,
            mode:  "python",
            //theme: "default",
            lineNumbers: true,
            styleActiveLine: true,
            matchBrackets: true,
            indentUnit: 4,
            indentWithTabs: false,
            extraKeys: {
                Tab: TestCommon.Utils.convertTabToSpaces
            }
        });

        codeEditor = this.codeEditor;

        if(Global.user.projectWeight < Main.PermissionWeightsEnum.standard){
            this.codeEditor.setOption('readOnly', 'nocursor')
        }
        // set unsaved changes watcher
        this.watchForUnsavedChanges();
    }

    this.save = function(callback){
        let content = this.codeEditor.getValue();
        // get data from table
        let testData = TestCommon.DataTable.getData();
        let payload = {
            'content': content,
            'testData': testData,
            'project': this.file.project,
            'testName': this.file.fullName
        }
        xhr.put('/api/test/code/save', payload, result => {
            this.unsavedChanges = false;
            this.codeEditor.markClean();
            Main.Utils.toast('success', `Test ${this.file.fullName} saved`, 3000);
            if(result.error != null) {
                $(".error-container").show();
                $(".error-container pre").html(result.error);
                Main.Utils.toast('info', "There are errors in the code", 3000)
            } else {
                $(".error-container").hide();
                $(".error-container pre").html('');
                if(callback != undefined)
                    callback()
            }
        })
    }

    this.watchForUnsavedChanges = function(){
        $("#dataTable").on("change keyup paste", () => this.unsavedChanges = true);

        window.addEventListener("beforeunload", e => {
            if(this.hasUnsavedChanges()){
                var confirmationMessage = 'There are unsaved changes';
                (e || window.event).returnValue = confirmationMessage; //Gecko + IE
                return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
            }
        });
    }

    this.runTest = function(){
        let run = () => Main.TestRunner.runTest(this.file.project, this.file.fullName);
        if(this.hasUnsavedChanges())
            this.save(run)
        else
            run()
    }

    this.hasUnsavedChanges = function(){
        return !this.codeEditor.isClean() || this.unsavedChanges
    }
}