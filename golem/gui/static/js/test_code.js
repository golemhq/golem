
let codeEditor;


const TestCode = new function() {

    this.codeEditor = undefined;
    this.unsavedChanges = false;
    this.golemActions = [];
    this.importedPages = [];
	this.test_data =[];
	
    this.initialize = function(file, testCode, codeError) {
        this.file = file;
		TestCode.getGolemActions();
		TestCode.getAllProjectPages();
		TestCode.getAllData();
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
        });
        codeEditor = this.codeEditor;
		CodeMirror.commands.autocomplete = function(cm) {
			                        
										 CodeMirror.simpleHint(cm, CodeMirror.pythonHint);
										 }
	 codeEditor.on("keyup", function (cm, event) {
if (!cm.state.completionActive &&   /*Enables keyboard navigation in autocomplete list*/
     (event.keyCode > 64 && event.keyCode < 220) || (event.keyCode==190)){// only when a letter key is pressed
	 codeEditor.execCommand("autocomplete")
    }
});

        if(Global.user.projectWeight < Main.PermissionWeightsEnum.standard){
            this.codeEditor.setOption('readOnly', 'nocursor')
        }
        // set unsaved changes watcher
        this.watchForUnsavedChanges();
    }
    this.getGolemActions = function(){
        xhr.get('/api/golem/actions', {
            project: this.file.project
        }, golemAction => {
			golemAction.forEach(function(action) {
            TestCode.golemActions.push(action.name)
        })
        })
		
    }
	this.getAllProjectPages = function(){
        xhr.get('/api/project/pages', {
            project: this.file.project
        }, pages => {
			pages.forEach(function(page){
            TestCode.getPageContents(page)
        });
        })
    }
	this.getPageContents = function(pageName){
        xhr.get('/api/page/components', {
            project: this.file.project,
            page: pageName
        }, result => {
            if(result.error == 'page does not exist'){
                // mark page as not existent
                $(`input[value='${pageName}']`).addClass('not-exist');
            }
            else{
				let elemets  = result.components.elements
				elemets.forEach(function(pagefull){
					TestCode.importedPages.push(pagefull.full_name)	
					})
            }
        })
    }
	this.getAllData = function()
	{
		let dataTableHeaders = TestCommon.DataTable.getHeaders();
        dataTableHeaders.forEach(function(header){
            TestCode.test_data.push(`data.${header}`)
        });
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