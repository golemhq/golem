

var Test = new function(){

    this.file;
    this.golemActions = [];
    this.allPages = [];
    this.importedPages = [];
    this.unsavedChanges = false;

    this.initialize = function(file, importedPages, testHooks, testFunctions){

        this.file = file;

        Test.getUniqueTags();
        importedPages.forEach(function(page){
            Test.getPageContents(page)
        });
        Test.getAllProjectPages();
        Test.getGolemActions();
        Test.addTestHooks(testHooks);
        Test.addTestFunctions(testFunctions);
        Test.refreshActionInputsAutocomplete();
        Test.refreshValueInputsAutocomplete();
        $('#pageModal').on('hidden.bs.modal', function() {
            Test.importedPages.forEach((page) => Test.getPageContents(page.name))
        });
        Test.Utils.watchForUnsavedChanges();
        Test.Utils.startSortableSteps();
    }

    this.getGolemActions = function(){
        xhr.get('/api/golem/actions', {
            project: this.file.project
        }, golemActions => {
            Test.golemActions = golemActions;
            Test.refreshActionInputsAutocomplete();
        })
    }

    this.addTestFunctions = function(testFunctions){
        for (const testFunction in testFunctions) {
            Test.addTestFunction(testFunction, testFunctions[testFunction]);
        }
    }

    this.addTestFunction = function(functionName, steps) {
        this.addXFunction(functionName, steps, $('#testFunctions'), true);
    }

    this.addTestHooks = function(testHooks) {
        let orderedTestHooks = Test.Hooks.orderTestHooks(testHooks);

        for (const testHook in orderedTestHooks) {
            Test.addTestHook(testHook, testHooks[testHook]);
        }
    }

    this.addTestHook = function(hookName, steps) {
        Test.Hooks.addHook(hookName, steps);
    }

    this.addXFunction = function(functionName, testSteps, container, isTestFunction) {
        // only test functions have on click to modify test function name
        // test hooks names cannot be modified
        if(isTestFunction) {
            functionNameOnClick = 'Test.Utils.startTestFunctionInlineNameEdition(this)';
            removeIconOnClick = 'Test.Utils.deleteTestFunction(this)';
        } else {
            functionNameOnClick = '';
            removeIconOnClick = 'Test.Hooks.deleteHook(this)';
        }

        let testFunctionTemplate = $(`
            <div class='test-function function'>
                <div class='testFunctionNameContainer'>
                    <h4 class="testFunctionNameContainer">
                        <span class="test-function-name" onclick="${functionNameOnClick}">${functionName}</span>
                        <span class="test-function-name-input" style="display: none">
                            <input type="text">
                        </span>
                    </h4>
                    <div class="inline-remove-icon">
                        <a href="javascript:void(0)" onclick="${removeIconOnClick}">
                            <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>
                        </a>
                    </div>
                </div>
                <div class='steps'></div>
                <button class='btn btn-default btn-sm add-step' style='margin-left: 21px;' onclick="Test.addStepInputToThis(this);">
                    <span class="glyphicon glyphicon-plus" aria-hidden="true"></span></button>
            </div>`);

        let stepContainer = testFunctionTemplate.find('.steps');
        if(testSteps.length) {
            Test.renderSectionSteps(stepContainer, testSteps);
        } else {
            Test.addStepInputToThis(stepContainer);
        }
        container.append(testFunctionTemplate);
        Test.refreshActionInputsAutocomplete();
        Test.refreshValueInputsAutocomplete();
    }

    this.renderSectionSteps = function(container, steps) {
        if(!steps) {
            Test.addStepInputToThis(container)
        } else {
            steps.forEach(function(step) {
                if(step.type == 'function-call') {
                    container.append(Test.functionCallStepTemplate(step.function_name, step.parameters))
                } else if(step.type == 'code-block') {
                    Test.addCodeBlockStep(container, step.code)
                }
            })
        }
        Test.Utils.fillStepNumbering();
    }

    this.addCodeBlockStep = function(container, code) {
        let step = Test.codeBlockStepTemplate();
        container.append(step);
        Test.initializeCodeBlock(step, code)
    }

    this.addEmptyCodeBlockStep = function(step) {
        let codeBlockStep = Test.codeBlockStepTemplate();
        step.replaceWith(codeBlockStep);
        let editor = Test.initializeCodeBlock(codeBlockStep, '');
        editor.focus()
    }

    this.initializeCodeBlock = function(step, code) {
        code = code || '';
        let editor = CodeMirror(step.find('.code-block')[0], {
            value: code,
            mode:  "python",
            lineNumbers: false,
            styleActiveLine: false,
            matchBrackets: true,
            indentUnit: 4,
            indentWithTabs: false,
            extraKeys: {
                Tab: TestCommon.Utils.convertTabToSpaces
            },
            viewportMargin: Infinity
        });
        setTimeout(() => editor.refresh(), 250);
        editor.on('change', editor => Test.unsavedChanges = true);
        return editor
    }

    this.addNewTestFunction = function() {
        let callback = (testName) => {
            Test.addTestFunction(testName, [])
        }
        let validationCallback = (testName) => {
            return Test.Utils.validateTestFunctionName(testName);
        }
        Main.Utils.displayPromptModal('Add Test', '', 'test', 'test name', callback, validationCallback)
    }

    this.getAllTestFunctionNames = function() {
        let testFunctionNames = []
        $('#testFunctions > .test-function span.test-function-name').each(function() {
            testFunctionNames.push($(this).html().trim())
        })
        return testFunctionNames
    }

    this.getAllProjectPages = function(){
        xhr.get('/api/project/pages', {
            project: this.file.project
        }, pages => {
            Test.allPages = pages;
            Test.refreshPagesAutocomplete();
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
                Test.importedPages = Test.importedPages.filter(page => page.name !== pageName)
                Test.importedPages.push({
                    name: pageName,
                    elements: result.components.elements,
                    functions: result.components.functions
                });
                Test.refreshPagesAutocomplete()
                Test.refreshElementInputsAutocomplete();
                Test.refreshActionInputsAutocomplete();
            }
        })
    }

    this.refreshActionInputsAutocomplete = function() {
        let lookup = []
        Test.golemActions.forEach(function(action) {
            lookup.push({value: action.name, data: action.description})
        })
        Test.importedPages.forEach(function(page) {
            page.functions.forEach(function(func) {
                lookup.push({value: func.partial_name, data: func.description})
            })
        });
        autocomplete = $(".step-first-input").autocomplete({
            lookup: lookup,
            minChars: 0,
            triggerSelectOnValidInput: false,
            formatResult: function(suggestion, currentValue) {
                let descriptionBox = '';
                if(suggestion.data){
                    descriptionBox = `<div class="action-description">${suggestion.data}</div>`
                }
                let suggestionHTML = `<div>${suggestion.value}</div>${descriptionBox}`;
                return suggestionHTML
            },
            onSelect: function (suggestion) { Test.onActionInputChange($(this)) }
        });
    }

    this.refreshValueInputsAutocomplete = function(){
        let dataTableHeaders = TestCommon.DataSource.DataTable.getHeaders();
        let lookup = []
        dataTableHeaders.forEach(function(header){
            lookup.push(`data.${header}`)
        });
        $(".value-input").each(function(){
            autocomplete = $(this).autocomplete({
                lookup: lookup,
                minChars: 0,
                onSelect: function (suggestion) { Test.unsavedChanges = true }
            });
        })
    }

    this.refreshElementInputsAutocomplete = function(){
        let lookup = [];
        Test.importedPages.forEach(function(page){
            page.elements.forEach(function(element){
                lookup.push(element.partial_name)
            })
        });
        $(".element-input").each(function(){
            autocomplete = $(this).autocomplete({
                lookup: lookup,
                minChars: 0,
                onSelect: function (suggestion) { Test.unsavedChanges = true; },
                onSearchStart: function () {},
                beforeRender: function (container) {},
                onSearchComplete: function (query, suggestions) {
                }
            });
        })
    }

    this.refreshPagesAutocomplete = function(){
        let pages = Test.Utils.getNotImportedPages();
        autocomplete = $(".page-objects-autocomplete").autocomplete({
            lookup: pages,
            minChars: 0,
            noCache: true,
            onSelect: function (suggestion) {
                Test.addPageToList(suggestion.value);
                $("input.page-objects-input.page-objects-autocomplete").val('');
            },
        });
    }

    this.onActionInputChange = function(elem){
        let step = $(elem).closest('.step');
        let elemValue = $(elem).val();
        let hasParameters = step.find('.parameter-input').length > 0;
        if(hasParameters){
            step.find('.parameter-container').remove();
        }

        if(elemValue == 'code_block'){
            Test.addEmptyCodeBlockStep(step)
            return
        }

        let actionParameters;
        if(Test.Utils.isGolemAction(elemValue)){
            actionParameters = Test.golemActions.filter(x => x.name == elemValue)[0].parameters;
        } else {
            // this is a page object function
            actionParameters = Test.Utils.getPageFunctionParameters(elemValue)
        }
        actionParameters.forEach(function(parameter){
            let customClass
            if(parameter.type == 'value'){ customClass = 'value-input' }
            else if(parameter.type == 'element'){ customClass = 'element-input' }
            else if(parameter.type == 'both'){ customClass = 'element-input value-input' }
            let input = `<input type="text" class="form-control parameter-input ${customClass}" placeholder="${parameter.name}">`;
            let paramContainer = $("<div class='step-input-container parameter-container'>"+input+"</div>");
            paramContainer.on('change', function(){ Test.unsavedChanges = true });
            step.find('.params').append(paramContainer);
            step.find(".parameter-input").first().focus();
            Test.refreshValueInputsAutocomplete();
            Test.refreshElementInputsAutocomplete();
            Test.unsavedChanges = true;
        })
        return false
    }

    this.runTest = function(){
        if(Test.unsavedChanges)
            Test.save({runAfter: true})
        else
            Main.TestRunner.runTest(this.file.project, Test.file.fullName);
    }

    this.save = function(config) {
        runAfter = config.runAfter || false;
        let description = $("#description").val();
        let pageObjects = Test.importedPages.map(x => x.name);
        let testData = TestCommon.DataSource.getData();
        let testSteps = Test.Utils.getSteps();
        let tags = [];
        if($("#tags").val().length > 0){
            $($("#tags").val().split(',')).each(function(){
                if(this.trim().length > 0){
                    tags.push(this.trim());
                }
            });
        }
        let skip = ($("#skipCheckbox").prop('checked'));
        if(skip){
            let reason = $("#skipReason").val().trim()
            if(reason.length){
                skip = reason
            }
        }

        let data = {
            'description': description,
            'pages': pageObjects,
            'testData': testData,
            'steps': testSteps,
            'project': this.file.project,
            'testName': Test.file.fullName,
            'tags': tags,
            'skip': skip
        }

        xhr.put('/api/test/save', data, (result) => {
            if(result.errors.length) {
                result.errors.forEach(error => Main.Utils.toast('error', error, 10000));
            } else {
                Test.unsavedChanges = false;
                Main.Utils.toast('success', `Test ${Test.file.fullName} saved`, 3000);
                if(runAfter){ Main.TestRunner.runTest(this.file.project, Test.file.fullName) }
            }
        })
    }

    this.generatePageInput = function(pageName){
        let pageInput = `
            <div class="input-group page">
                <input type="text" disabled class="form-control page-name" value="${pageName}">
                <div class="input-group-btn">
                    <button class="btn btn-default" type="button" onclick="Test.loadPageInModal(this)">
                        <span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button>
                    <button class="btn btn-default" type="button" onclick="Test.Utils.openPageInNewWindow(this)">
                        <span class="glyphicon glyphicon-new-window" aria-hidden="true"></span>
                    </button>
                    <button class="btn btn-default" type="button" onclick="Test.deletePageObject(this)">
                        <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>
                    </button>
                </div>
            </div>`;
        return pageInput
    }

    this.addStepInputToThis = function(elem) {
        let stepsContainer = $(elem).closest('.function').find('.steps');
        stepsContainer.append(Test.functionCallStepTemplate())
        // give focus to the last step action input
        stepsContainer.find(".step-first-input").last().focus();
        Test.Utils.fillStepNumbering();
        Test.refreshActionInputsAutocomplete()
    }

    this.deletePageObject = function(elem){
        let pageName = $(elem).closest('.page').find('input.page-name').val();
        Test.importedPages = Test.importedPages.filter(page => page.name !== pageName)
        $(elem).closest('.page' ).remove();
        Test.refreshPagesAutocomplete();
        Test.unsavedChanges = true;
    }

    this.displayNewPagePrompt = function(){
        let title = 'Add New Page';
        let message = '';
        let inputValue = '';
        let placeholderValue = 'new page name';
        let callback = function(newPageName){
            Test.addNewPage(newPageName);
        }
        Main.Utils.displayPromptModal(title, message, inputValue, placeholderValue, callback);
    }

    this.addNewPage = function(newPageName){
        let errors = Main.Utils.validateFilename(newPageName);
        if(errors.length > 0){
            Main.Utils.displayErrorModal(errors);
            return
        }

        xhr.post('/api/project/page', {
            project: this.file.project,
            fullPath: newPageName
        }, data => {
            if(data.errors.length == 0) {
                Test.allPages.push(newPageName);
                Test.addPageToList(newPageName)
            } else {
                Main.Utils.displayErrorModal(data.errors);
            }
        })
    }

    this.addPageToList = function(pageName){
        let newPageInput = Test.generatePageInput(pageName);
        $("#pageObjects").append(newPageInput);
        Test.getPageContents(pageName)
        Test.unsavedChanges = true;
    }

    this.loadPageInModal = function(elem){
        let inputVal = $(elem).closest('.page').find('input.page-name').val();
        $("#pageModalIframe").attr('src', `/project/${this.file.project}/page/${inputVal}/no_sidebar/`);
        $("#pageModal").modal('show');        
    }

    this.getUniqueTags = function(){
        xhr.get('/api/project/tags', {project: this.file.project}, tags => {
            Test.projectTags = tags;
            Test.refreshTagInputAutocomplete();
        })
    }

    this.refreshTagInputAutocomplete = function(){
        $('#tags').autocomplete({
            lookup: Test.projectTags,
            minChars: 0,
            delimiter: ', ',
            triggerSelectOnValidInput: false,
            onSelect: function (suggestion) {
                $('#tags').val($('#tags').val()+', ');
            }
        });
    }

    this.functionCallStepTemplate = function(functionName, parameters){
        functionName = functionName || '';
        parameters = parameters || [];
        let paramString = '';
        parameters.forEach(function(parameter){
            parameter = parameter.replace(/"/g,'&quot;');
            paramString = paramString.concat(`<div class="step-input-container parameter-container">
                <input type="text" class="form-control parameter-input element-input value-input" value="${parameter}">
            </div>`);
        });

        let step = `<div class="step" step-type="function-call">
            <div class="step-numbering"></div>
            <div class="col-sm-3 step-input-container step-first-input-container">
                <input type="text" class="form-control step-first-input" placeholder="action" value="${functionName}">
            </div>
            <div class="params">${paramString}</div>
            <div class="step-remove-icon">
                <a href="javascript:void(0)" onclick="Test.Utils.deleteStep(this)">
                    <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>
                </a>
            </div>
        </div>`;
        return step
    }

    this.codeBlockStepTemplate = function(){
        let template = $(`<div class="step" step-type="code-block">
            <div class="step-numbering"></div>
            <div class="code-block"></div>
            <div class="step-remove-icon">
                <a href="javascript:void(0)" onclick="Test.Utils.deleteStep(this)">
                    <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>
                </a>
            </div>
        </div>`);
        return template
    }

    this.Hooks = new function() {

        this.orderTestHooks = function(hooks) {
            ordered = {}
            orderList = ['before_test', 'setup', 'before_each', 'after_each', 'after_test', 'teardown']
            for (hookName of orderList) {
                if(hookName in hooks) {
                    ordered[hookName] = hooks[hookName]
                }
            }
            return ordered
        }

        this.addHook = function(name, steps) {
            steps = steps || [];
            Test.addXFunction(name, steps, $('#testHooks'), false);
            $(`#hookSelector a[hook-name='${name}']`).hide();
        }

        this.deleteHook = function(elem) {
            let hookName = $(elem).closest('.test-function').find('h4 span').html();
            Main.Utils.displayConfirmModal('Delete Test Hook?', '', () => {
                $(elem).closest('.test-function').remove();
                Test.unsavedChanges = true;
                $(`#hookSelector a[hook-name='${hookName}']`).show();
            });
        }
    }

    this.Utils = new function() {

        this.getNotImportedPages = function() {
            let notImported = [];
            let importedPagesNames = Test.importedPages.map(x => x.name);
            Test.allPages.forEach(function(page){
                if($.inArray(page, importedPagesNames) == -1){
                    notImported.push(page);
                }
            })
            return notImported
        }

        this.getPageFunctionParameters = function(functionName){
            for(var i = 0; i < Test.importedPages.length; i++) {
                let page = Test.importedPages[i];
                for(var j = 0; j < page.functions.length; j++) {
                    let func = page.functions[j];
                    if(func.full_name == functionName){
                        return func.arguments.map(x => ({'name': x, 'type': 'both'}))
                    }
                }
            }
            return false
        }

        this.isGolemAction = function(value){
            for(ac in Test.golemActions){
                if(Test.golemActions[ac].name == value){ return true }
            }
            return false
        }

        this.collapseTeardown = function(){
            $("#showTeardownLink").show();
            $("#teardownSteps").slideUp('fast');
        }

        this.collapseSetup = function(){
            $("#showSetupLink").show();
            $("#setupSteps").slideUp('fast');
        }

        this.showSetupSteps = function(){
            $("#showSetupLink").hide();
            $("#setupSteps").slideDown('fast');
        }

        this.showTeardownSteps = function(){
            $("#showTeardownLink").hide();
            $("#teardownSteps").slideDown('fast');
        }

        this.startSortableSteps = function(){
            let settings = {
                handle: '.step-numbering',
                draggable: '.step',
                onEnd: function (evt) {
                    Test.Utils.fillStepNumbering();
                }
            };
            $('.steps').each(function() {
                Sortable.create(this, settings);
            })
        }

        this.fillStepNumbering = function(){
            $(".steps").each(function(){
                let count = 1;
                $(this).find(".step").each(function(){
                    $(this).find('.step-numbering').html(count);
                    count++;
                })
            })
        }

        this.openPageInNewWindow = function(elem){
            let inputVal = $(elem).closest('.page').find('input.page-name').val();
            if(inputVal.length > 0){
                let url = `/project/${Test.file.project}/page/${inputVal}/`;
                window.open(url, '_blank');
            }
        }

        this.watchForUnsavedChanges = function() {
            let unsavedChangesTrue = () => Test.unsavedChanges = true;

            $("#tags").on("change keyup paste", unsavedChangesTrue);
            $(".page-objects-input").on("change keyup paste", unsavedChangesTrue);
            $(".step-first-input").on("change keyup paste", unsavedChangesTrue);
            $(".parameter-input").on("change keyup paste", unsavedChangesTrue);
            $("#description").on("change keyup paste", unsavedChangesTrue);
            $("#dataContainerContainer").on("change paste", "#dataTable input", unsavedChangesTrue);
            $("#dataContainerContainer").on("change paste", "#jsonEditorContainer", unsavedChangesTrue);
            $("#dataContainerContainer").on("change paste", "#internalEditorContainer", unsavedChangesTrue);

            window.addEventListener("beforeunload", function (e) {
                if(Test.unsavedChanges){
                    let confirmationMessage = 'There are unsaved changes';
                    (e || window.event).returnValue = confirmationMessage;
                    return confirmationMessage;
                }
            });
        }

        this.deleteStep = function(elem) {
            $(elem).closest('.step').remove();
            Test.unsavedChanges = true;
        }

        this.getSteps = function() {
            let steps = {
                hooks: {},
                tests: {},
            }
            $('#testHooks > .test-function').each(function() {
                let hookName = $(this).find('span.test-function-name').html().trim();
                steps.hooks[hookName] = Test.Utils.parseSteps($(this).find('.step'))
            })
            $('#testFunctions > .test-function').each(function() {
                let testName = $(this).find('span.test-function-name').html().trim();
                steps.tests[testName] = Test.Utils.parseSteps($(this).find('.step'))
            })
            return steps
        }

        this.parseSteps = function(steps) {
            let parsedSteps = [];
            steps.each(function() {
                if(this.getAttribute('step-type') == 'function-call') {
                    let thisStep = Test.Utils.getFunctionCallStepValues(this);
                    if(thisStep.action.length > 0)
                        parsedSteps.push(thisStep);
                } else {
                    let thisStep = Test.Utils.getCodeBlockStepValues(this);
                    if(thisStep.code.trim())
                        parsedSteps.push(thisStep);
                }
            })
            return parsedSteps
        }

        this.getFunctionCallStepValues = function(elem) {
            let thisStep = {
                type: 'function-call',
                action: '',
                parameters: []
            }
            if($(elem).find('.step-first-input').val().length > 0) {
                thisStep.action = $(elem).find('.step-first-input').val();
                $(elem).find('.parameter-input').each(function() {
                    if($(this).val().length > 0)
                        thisStep.parameters.push($(this).val());
                });
            }
            return thisStep
        }

        this.getCodeBlockStepValues = function(elem) {
            let editor = $(elem).find('.CodeMirror').get(0).CodeMirror;
            return {
                type: 'code-block',
                code: editor.getValue()
            }
        }

        this.stepSection = function(section) {
            if(section == 'setup') return $("#setupSteps .steps")
            if(section == 'test') return $("#testSteps .steps")
            if(section == 'teardown') return $("#teardownSteps .steps")
        }

        this.onSkipCheckboxChange = function() {
            if($("#skipCheckbox").prop('checked')) {
                $("#skipReason").show();
            } else {
                $("#skipReason").hide();
            }
        }

        this.deleteTestFunction = function(elem) {
            Main.Utils.displayConfirmModal('Delete Test?', '', () => {
                $(elem).closest('.test-function').remove();
                Test.unsavedChanges = true;
            });
        }

        this.startTestFunctionInlineNameEdition = function(elem) {
            let nameContainer = $(elem).closest('.testFunctionNameContainer');
            let valueSpan = nameContainer.find('.test-function-name');
            let inputSpan = nameContainer.find('.test-function-name-input');
            let input = inputSpan.find('input');
            let callback = function() {
                Test.Utils.updateTestFunctionName(valueSpan, inputSpan, input);
            }
            Main.Utils.startGenericInlineName(
                inputSpan, valueSpan, valueSpan.html().trim(), callback)
        }

        this.updateTestFunctionName = function(valueSpan, inputSpan, input) {
            let currentName = valueSpan.html();
            let newNameValue = input.val().trim();
            if(currentName == newNameValue) {
                inputSpan.hide();
                valueSpan.show();
                return
            }
            let error = Test.Utils.validateTestFunctionName(newNameValue);
            if(error.length) {
                inputSpan.hide();
                valueSpan.show();
                Main.Utils.toast('error', error, 2000);
                return
            } else {
                input.val('');
                inputSpan.hide();
                valueSpan.html(newNameValue).show();
                Test.unsavedChanges = true;
            }
        }

        this.validateTestFunctionName = function(testName) {
            if(testName.length == 0) {
                return 'test name cannot be blank'
            } else if(!testName.startsWith('test')) {
                return 'test name should start with "test"'
            } else if(Test.getAllTestFunctionNames().includes(testName)) {
                return `a test with name "${testName}" already exists`
            } else {
                return ''
            }
        }
    }
}
