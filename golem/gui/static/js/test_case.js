
$(document).ready(function() {
    Test.initialize(Global.project, testCaseName, fullTestCaseName, importedPages, steps);
});


var Test = new function(){

    this.project = '';
    this.name = '';
    this.fullName = '';
    this.golemActions = [];
    this.allPages = [];
    this.importedPages = [];
    this.unsavedChanges = false;

    this.initialize = function(project, testCaseName, fullTestCaseName, importedPages, steps){
        Test.getUniqueTags(project);
        Test.project = project;
        Test.fullName = fullTestCaseName;
        importedPages.forEach(function(page){
            Test.getPageContents(page)
        });
        Test.getAllProjectPages();
        Test.getGolemActions();
        Test.renderSteps(steps);
        Test.refreshActionInputsAutocomplete();
        Test.refreshValueInputsAutocomplete();
        $('#pageModal').on('hidden.bs.modal', function(){
            Test.importedPages.forEach(function(page){
                Test.getPageContents(page.name)
            })
        });
        Test.Utils.watchForUnsavedChanges();
        Test.Utils.startSortableSteps();
    }

    this.getGolemActions = function(){
        $.ajax({
            url: "/api/golem/actions",
            data: {
                "project": Test.project,
            },
            dataType: 'json',
            type: 'GET',
            success: function(golemActions) {
                Test.golemActions = golemActions;
                Test.refreshActionInputsAutocomplete();
            }
        });
    }

    this.renderSteps = function(steps){
        Test.renderSectionSteps(steps.setup, 'setup');
        Test.renderSectionSteps(steps.test, 'test');
        Test.renderSectionSteps(steps.teardown, 'teardown');
    }

    this.renderSectionSteps = function(steps, sectionName){
        if(steps.length == 0){
            Test.addFirstStepInput(sectionName)
        }
        else{
            steps.forEach(function(step){
                let section = Test.Utils.stepSection(sectionName);
                if(step.type == 'function-call'){
                    section.append(Test.functionCallStepTemplate(step.function_name, step.parameters))
                }
                else if(step.type == 'code-block'){
                    Test.addCodeBlockStep(section, step.code)
                }
            })
        }
    }

    this.addCodeBlockStep = function(section, code){
        let step = Test.codeBlockStepTemplate();
        section.append(step);
        Test.initializeCodeBlock(step, code)
    }

    this.addEmptyCodeBlockStep = function(step){
        let codeBlockStep = Test.codeBlockStepTemplate();
        step.replaceWith(codeBlockStep);
        let editor = Test.initializeCodeBlock(codeBlockStep, '');
        editor.focus()
    }

    this.initializeCodeBlock = function(step, code){
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
            }
        });
        editor.on('change', editor => Test.unsavedChanges = true);
        return editor
    }

    this.getAllProjectPages = function(){
        $.ajax({
            url: "/api/project/pages",
            data: {
                "project": Test.project,
            },
            dataType: 'json',
            type: 'GET',
            success: function(pages) {
                Test.allPages = pages;
                Test.refreshPagesAutocomplete();
            }
        });
    }

    this.getPageContents = function(pageName){
        $.ajax({
            url: "/api/page/components",
            data: {
                 "project": Test.project,
                 "page": pageName,
            },
            dataType: 'json',
            type: 'GET',
            success: function(result) {
                if(result.error == 'page does not exist'){
                    // mark page as not existent
                    $(`input[value='${pageName}']`).addClass('not-exist');
                }
                else{
                    Test.importedPages = Test.importedPages.filter(page => page.name !== pageName)
                    Test.importedPages.push({
                        'name': pageName,
                        'elements': result.components.elements,
                        'functions': result.components.functions
                    });
                    Test.refreshPagesAutocomplete()
                    Test.refreshElementInputsAutocomplete();
                    Test.refreshActionInputsAutocomplete();
                }
            }
        });
    }

    this.refreshActionInputsAutocomplete = function(){
        let lookup = []
        Test.golemActions.forEach(function(action){
            lookup.push({value: action.name, data: action.description})
        })
        Test.importedPages.forEach(function(page){
            page.functions.forEach(function(func){
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
        let dataTableHeaders = TestCommon.DataTable.getHeaders();
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
        }
        else{
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
            Main.TestRunner.runTest(Test.project, Test.fullName);
    }

    this.save = function(config){
        runAfter = config.runAfter || false;
        let description = $("#description").val();
        let pageObjects = Test.importedPages.map(x => x.name);
        let testData = TestCommon.DataTable.getData();
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
            'project': Test.project,
            'testName': Test.fullName,
            'tags': tags,
            'skip': skip
        }

        $.ajax({
            url: "/api/test/save",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            type: 'PUT',
            success: function(data) {
                Test.unsavedChanges = false;
                Main.Utils.toast('success', `Test ${Test.fullName} saved`, 3000);
                if(runAfter){ Main.TestRunner.runTest(Test.project, Test.fullName) }
            }
        });
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

    this.addFirstStepInput = function(targetSection){
        let section = Test.Utils.stepSection(targetSection);
        section.append(Test.functionCallStepTemplate())
        // give focus to the last step action input
        section.find(".step-first-input").last().focus();
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
        $.ajax({
            url: "/api/project/page",
            data: JSON.stringify({
                "project": Test.project,
                "fullPath": newPageName
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                if(data.errors.length == 0){
                    Test.allPages.push(newPageName);
                    Test.addPageToList(newPageName)
                }
                else{
                    Main.Utils.displayErrorModal(data.errors);
                }
            }
        });
    }

    this.addPageToList = function(pageName){
        let newPageInput = Test.generatePageInput(pageName);
        $("#pageObjects").append(newPageInput);
        Test.getPageContents(pageName)
        Test.unsavedChanges = true;
    }

    this.loadPageInModal = function(elem){
        let inputVal = $(elem).closest('.page').find('input.page-name').val();
        $("#pageModalIframe").attr('src', `/project/${Test.project}/page/${inputVal}/no_sidebar/`);
        $("#pageModal").modal('show');        
    }

    this.getUniqueTags = function(project){
        $.ajax({
            url: "/api/project/tags",
            data: {
                "project": project
            },
            dataType: 'json',
            type: 'GET',
            success: function(tags) {
                Test.projectTags = tags;
                Test.refreshTagInputAutocomplete();
            },
        });
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


    this.Utils = new function(){

        this.getNotImportedPages = function(){
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
            let setupSteps = document.querySelector("[id='setupSteps']>.steps");
            let testSteps = document.querySelector("[id='testSteps']>.steps");
            let teardownSteps = document.querySelector("[id='teardownSteps']>.steps");
            let settings = {
                handle: '.step-numbering',
                draggable: '.step',
                onEnd: function (/**Event*/evt) {
                    Test.Utils.fillStepNumbering();
                }
            };
            Sortable.create(setupSteps, settings);
            Sortable.create(testSteps, settings);
            Sortable.create(teardownSteps, settings);
        }

        this.fillStepNumbering = function(){
            let count = 1;
            $("#setupSteps .step").each(function(){
                $(this).find('.step-numbering').html(count);
                count++;
            });
            count = 1;
            $("#testSteps .step").each(function(){
                $(this).find('.step-numbering').html(count);
                count++;
            });
            count = 1;
            $("#teardownSteps .step").each(function(){
                $(this).find('.step-numbering').html(count);
                count++;
            });
        }

        this.openPageInNewWindow = function(elem){
            let inputVal = $(elem).closest('.page').find('input.page-name').val();
            if(inputVal.length > 0){
                let url = `/project/${Test.project}/page/${inputVal}/`;
                window.open(url, '_blank');
            }
        }

        this.watchForUnsavedChanges = function(){
            $("#tags").on("change keyup paste", function(){
                Test.unsavedChanges = true;
            });
            $(".page-objects-input").on("change keyup paste", function(){
                Test.unsavedChanges = true;
            });
            $(".step-first-input").on("change keyup paste", function(){
                Test.unsavedChanges = true;
            });
            $(".parameter-input").on("change keyup paste", function(){
                Test.unsavedChanges = true;
            });
            $("#description").on("change keyup paste", function(){
                Test.unsavedChanges = true;
            });
            $("#dataTable").on("change keyup paste", function(){
                Test.unsavedChanges = true;
            });

            window.addEventListener("beforeunload", function (e) {
                if(Test.unsavedChanges){
                    let confirmationMessage = 'There are unsaved changes';
                    (e || window.event).returnValue = confirmationMessage;
                    return confirmationMessage;
                }
            });
        }

        this.deleteStep = function(elem){
            $(elem).closest('.step').remove();
            Test.unsavedChanges = true;
        }

        this.getSteps = function(){
            return {
                'setup': Test.Utils.parseSteps($("#setupSteps .step")),
                'test': Test.Utils.parseSteps($("#testSteps .step")),
                'teardown': Test.Utils.parseSteps($("#teardownSteps .step"))
            }
        }

        this.parseSteps = function(steps){
            let parsedSteps = [];
            steps.each(function(){
                if(this.getAttribute('step-type') == 'function-call'){
                    let thisStep = Test.Utils.getFunctionCallStepValues(this);
                    if(thisStep.action.length > 0){
                        parsedSteps.push(thisStep);
                    }
                }
                else{
                    let thisStep = Test.Utils.getCodeBlockStepValues(this);
                    if(thisStep.code.trim()){
                        parsedSteps.push(thisStep)
                    }
                }
            })
            return parsedSteps
        }

        this.getFunctionCallStepValues = function(elem){
            let thisStep = {
                'type': 'function-call',
                'action': '',
                'parameters': []
            }
            if($(elem).find('.step-first-input').val().length > 0){
                thisStep.action = $(elem).find('.step-first-input').val();
                $(elem).find('.parameter-input').each(function(){
                    if($(this).val().length > 0){
                        thisStep.parameters.push($(this).val());
                    }
                });
            }
            return thisStep
        }

        this.getCodeBlockStepValues = function(elem){
            let editor = $(elem).find('.CodeMirror').get(0).CodeMirror;
            return {
                'type': 'code-block',
                'code': editor.getValue()
            }
        }

        this.stepSection = function(section){
            if(section == 'setup') return $("#setupSteps .steps")
            if(section == 'test') return $("#testSteps .steps")
            if(section == 'teardown') return $("#teardownSteps .steps")
        }

        this.onSkipCheckboxChange = function(){
            if($("#skipCheckbox").prop('checked')) {
                $("#skipReason").show();
            } else {
                $("#skipReason").hide();
            }
        }
    }
}
