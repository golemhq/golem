
$(document).ready(function() {
    Test.initialize(project, testCaseName, fullTestCaseName, importedPages);
});


var Test = new function(){

    this.project = '';
    this.name = '';
    this.fullName = '';
    this.golemActions = [];
    this.allPages = [];
    this.importedPages = [];
    this.unsavedChanges = false;

    this.initialize = function(project, testCaseName, fullTestCaseName, importedPages){
        Test.getUniqueTags(project);
        Test.project = project;
        Test.fullName = fullTestCaseName;
        importedPages.forEach(function(page){
            Test.getPageContents(page)
        });
        Test.getAllProjectPages();
        Test.getGolemActions();
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
            url: "/get_golem_actions/",
            dataType: 'json',
            type: 'GET',
            success: function(golemActions) {
                Test.golemActions = golemActions;
                Test.refreshActionInputsAutocomplete();
            }
        });
    }

    this.getAllProjectPages = function(){
        $.ajax({
            url: "/get_page_objects/",
            data: {
                "project": Test.project,
            },
            dataType: 'json',
            type: 'POST',
            success: function(pages) {
                Test.allPages = pages;
                Test.refreshPagesAutocomplete();
            }
        });
    }

    this.getPageContents = function(page){
        $.ajax({
            url: "/get_page_contents/",
            data: {
                 "project": Test.project,
                 "page": page,
            },
            dataType: 'json',
            type: 'GET',
            success: function(result) {
                if(result.error == 'page does not exist'){
                    // mark page as not existent
                    $("input[value='"+thisPageName+"']").addClass('not-exist');
                }
                else{
                    Test.importedPages.push({
                        'name': page,
                        'elements': result.content.elements,
                        'functions': result.content.functions
                    })
                    Test.refreshElementInputsAutocomplete();
                    Test.refreshActionInputsAutocomplete();
                }
            }
        });
    }

    this.refreshActionInputsAutocomplete = function(){
        let lookup = []
        Test.golemActions.forEach(function(action){
            lookup.push(action.name)
        })
        Test.importedPages.forEach(function(page){
            page.functions.forEach(function(func){
                lookup.push(func.full_function_name)
            })
        });
        autocomplete = $(".step-first-input").autocomplete({
            lookup: lookup,
            minChars: 0,
            triggerSelectOnValidInput: false,
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
                lookup.push(element.element_name)
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
                Test.addPageToList(suggestion.value)
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

    this.loadCodeView = function(){
        if(Test.unsavedChanges){
            Test.save({runAfter: false});
        }
        Test.unsavedChanges = false;
        window.location.replace(`/project/${Test.project}/test/${Test.fullName}/code/`);
    }

    this.save = function(config){
        runAfter = config.runAfter || false;
        let description = $("#description").val();
        let pageObjects = Test.importedPages.map(x => x.name);
        let testData = TestCommon.DataTable.getData();
        let testSteps = {
            'setup': [],
            'test': [],
            'teardown': []
        };
        $("#setupSteps .step").each(function(){
            let thisStep = Test.Utils.getStepValues(this);
            if(thisStep.action.length > 0){
                testSteps.setup.push(thisStep);
            }
        });
        $("#testSteps .step").each(function(){
            let thisStep = Test.Utils.getStepValues(this);
            if(thisStep.action.length > 0){
                testSteps.test.push(thisStep);
            }
        });
        $("#teardownSteps .step").each(function(){
            let thisStep = Test.Utils.getStepValues(this);
            if(thisStep.action.length > 0){
                testSteps.teardown.push(thisStep);
            }
        });
        let tags = [];
        if($("#tags").val().length > 0){
            $($("#tags").val().split(',')).each(function(){
                if(this.trim().length > 0){
                    tags.push(this.trim());
                }
            });
        }
        let data = {
            'description': description,
            'pageObjects': pageObjects,
            'testData': testData,
            'testSteps': testSteps,
            'project': Test.project,
            'testCaseName': Test.fullName,
            'tags': tags,
        }
        $.ajax({
            url: "/save_test_case/",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            type: 'POST',
            success: function(data) {
                Test.unsavedChanges = false;
                Main.Utils.toast('success', "Test "+Test.fullName+" saved", 3000);
                if(runAfter){
                    Main.TestRunner.runTest(Test.project, Test.fullName);
                }
            }
        });
    }

    this.generatePageInput = function(pageName){
        let pageInput = "\
            <div class='input-group page'> \
                <input type='text' disabled class='form-control page-name' value='"+pageName+"'> \
                <div class='input-group-btn'> \
                    <button class='btn btn-default' type='button' onclick='Test.loadPageInModal(this)'>\
                        <span class='glyphicon glyphicon-edit' aria-hidden='true'></span></button>\
                    <button class='btn btn-default' type='button' onclick='Test.Utils.openPageInNewWindow(this)'> \
                        <span class='glyphicon glyphicon-new-window' aria-hidden='true'></span>\
                    </button> \
                    <button class='btn btn-default' type='button' onclick='Test.deletePageObject(this)'> \
                        <span class='glyphicon glyphicon-remove' aria-hidden='true'></span> \
                    </button> \
                </div> \
            </div>";
        return pageInput
    }

    this.addFirstStepInput = function(targetSection){
        let section;
        if(targetSection == 'setup'){ section = $("#setupSteps .steps") }
        else if(targetSection == 'test'){ section = $("#testSteps .steps") }
        else if(targetSection == 'teardown'){ section = $("#teardownSteps .steps") }
        section.append(
            "<div class='step'> \
                <div class='step-numbering'></div> \
                <div class='col-sm-3 step-input-container step-first-input-container'> \
                        <input type='text' class='form-control step-first-input' placeholder='action'> \
                </div> \
                <div class='params'> \
                </div> \
                <div class='step-remove-icon'> \
                    <a href='javascript:void(0)' onclick='Test.Utils.deleteStep(this);'> \
                        <span class='glyphicon glyphicon-remove' aria-hidden='true'></span> \
                    </a> \
                </div> \
            </div>");
        // give focus to the last step action input
        section.find(".step-first-input").last().focus();
        Test.Utils.fillStepNumbering();
        Test.refreshActionInputsAutocomplete()
    }

    this.deletePageObject = function(elem){
        let pageName = $(elem).closest('.page').find('input.page-name').val();
        Test.importedPages = Test.importedPages.filter(page => page.name !== pageName)
        $(elem).closest('.page' ).remove();
        Test.unsavedChanges = true;
    }

    this.displayNewPagePrompt = function(){
        let title = 'Add New Page';
        let message = '';
        let inputValue = '';
        let placeholderValue = 'page name';
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
            url: "/new_tree_element/",
            data: {
                "project": Test.project,
                "elementType": 'page',
                "isDir": false,
                "fullPath": newPageName
            },
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                if(data.errors.length == 0){
                    Test.allPages.push(data.element.full_path);
                    Test.addPageToList(data.element.full_path)
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
        $("#pageModalIframe").attr('src', '/project/'+Test.project+'/page/'+inputVal+'/no_sidebar/');
        $("#pageModal").modal('show');        
    }

    this.getUniqueTags = function(project){
        $.ajax({
            url: "/project/tags/",
            data: {
                "project": project
            },
            dataType: 'json',
            type: 'POST',
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
                    if(func.full_function_name == functionName){
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

        this.getStepValues = function(elem){
            let thisStep = {
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
    }
}
