
var pageObjects = [];
var globalActions = [];
var selectedPageObjectsElements = [];
var selectedPageObjectsFunctions = [];
var unsavedChanges = false;
var checkDelay = 2000;

$(document).ready(function() {      

    getGlobalActions();
    getPageObjects();
    getSelectedPageObjectElements();
    startAllElementInputAutocomplete();
    startAllValueInputAutocomplete();  

    $(".dato-variable").blur(function() {
        startAllValueInputAutocomplete();
    });

    $(".dato-variable").keyup(function(e) {
        if (e.which == 13) // Enter key
        startAllValueInputAutocomplete();
    });

    $(".page-objects-input").blur(function() {
        getSelectedPageObjectElements();
    });

    $(".page-objects-input").keyup(function(e) {
        if (e.which == 13) // Enter key
        getSelectedPageObjectElements();
    });

    // set unsaved changes watcher
    watchForUnsavedChanges();

    // start sortable steps
    startSortableSteps();

    // lock the file for current user
    //testManager.setFileLockInterval();
    //testManager.setUnlockFileOnUnload();
});


function addPOInput(){
    $("#pageObjects").append(
        "<div class='input-group'> \
            <input type='text' class='form-control custom-input \
                page-objects-input page-objects-autocomplete'> \
            <span class='input-group-btn input-middle-btn'> \
                <button class='btn btn-default' type='button' \
                    onclick='openPageObjectInNewWindow(this)'> \
                        <span class='glyphicon glyphicon-new-window' aria-hidden='true'> \
                        </span>\
                </button> \
            </span> \
            <span class='input-group-btn'> \
                <button class='btn btn-default' type='button' onclick='deletePageObject(this)'> \
                    <span class='glyphicon glyphicon-remove' aria-hidden='true'></span> \
                </button> \
            </span> \
        </div>");

    // give focus to the last input
    $(".page-objects-input").last().focus();

    startPageObjectsAutocomplete();
}


function addFirstStepInput(targetSection){

    if(targetSection == 'setup'){
        var section = $("#setupSteps .steps");
    }
    else if(targetSection == 'test'){
        var section = $("#testSteps .steps");
    }
    else if(targetSection == 'teardown'){
        var section = $("#teardownSteps .steps");
    }
    section.append(
        "<div class='step'> \
            <div class='step-numbering'></div> \
            <div class='col-sm-3 step-input-container step-first-input-container'> \
                <div class='input-group'> \
                    <input type='text' class='form-control step-first-input' \
                        placeholder='action'> \
                </div> \
            </div> \
            <div class='params col-sm-6'> \
            </div> \
            <div class='step-remove-icon'> \
                <a href='javascript:void(0)' onclick='deleteStep(this);'> \
                    <span class='glyphicon glyphicon-remove' aria-hidden='true'></span> \
                </a> \
            </div> \
        </div>");

    // give focus to the last step action input
    section.find(".step-first-input").last().focus();

    fillStepNumbering();
    startStepFirstInputAutocomplete();
}


function deletePageObject(elem){
    $(elem).parent().parent().remove();
    unsavedChanges = true;
}


function getPageObjects(){
    $.ajax({
        url: "/get_page_objects/",
        data: {
            "project": project,
        },
        dataType: 'json',
        type: 'POST',
        success: function(data) {
            for(po in data){
                var po = data[po];
                pageObjects.push({
                    'value': po,
                    'data': po,
                });
            }
            startPageObjectsAutocomplete();
        },
        error: function() {
        }
    });
}


function startPageObjectsAutocomplete(){
    autocomplete = $(".page-objects-autocomplete").autocomplete({
        lookup: getPageObjectsNotYetSelected(),
        minChars: 0,
        onSelect: function (suggestion) {
            getSelectedPageObjectElements();
            unsavedChanges = true;

            // shoud I add a new page input?
            var theresEmptyInput = false;
            $(".page-objects-input").each(function(){
                if($(this).val() == ''){
                    theresEmptyInput = true;
                }
            })
            if(!theresEmptyInput){
                addPOInput();
            }
        },
        onSearchStart: function () {
        },
        beforeRender: function (container) {},
        onSearchComplete: function (query, suggestions) {
        }
    });
}


function startStepFirstInputAutocomplete(){

   var lookup = []

    for(ac in globalActions){
        lookup.push({
            'value': globalActions[ac].name,
            'data': globalActions[ac].name
        })        
    }

    for(f in selectedPageObjectsFunctions){
        lookup.push({
            'value': selectedPageObjectsFunctions[f].full_function_name,
            'data': 'data'
        })        
    }

    autocomplete = $(".step-first-input").autocomplete({
        lookup: lookup,
        minChars: 0,
        triggerSelectOnValidInput: false,
        onSelect: function (suggestion) {
            // not this is not always called, 
            // sometimes the onchange is called before
            stepFirstInputChange($(this));
            unsavedChanges = true;
        },
        onSelect: function (suggestion) {
            // not this is not always called, 
            // sometimes the onchange is called before
            stepFirstInputChange($(this));
            unsavedChanges = true;
        },
        onSearchStart: function () {
        },
        beforeRender: function (container) {},
        onSearchComplete: function (query, suggestions) {
        }
    });
}


function stepFirstInputChange(elem){
    var step = $(elem).parent().parent().parent();
    var hasParameter = step.find('.parameter-input').length > 0
    var placeholder = ''
    var elemValue = $(elem).val();
    
    if(hasParameter){     
        // the step already has parameters, remove them and update
        step.find('.parameter-container').remove();
    }

    var pageObjects = getSelectedPageObjects();

    if(isInGlobalActions(elemValue)){
        // this is a global action
        var actionParameters = getGlobalActionParameters(elemValue);
    }
    else{
        // this is a page object function
        var actionParameters = getPageObjectFunctionParameters(elemValue);
    }

    for(p in actionParameters){
        var parameter = actionParameters[p];    

        if(parameter.type == 'value'){
            var customClass = 'value-input';
            var input = "<input type='text' class='form-control \
                                    parameter-input "+customClass+"' \
                                    placeholder='"+parameter.name+"'>";
        }
        else if(parameter.type == 'multiline-value'){
            var customClass = 'multiline-value-input';
            var input = "<textarea type='text' class='form-control \
                            parameter-input "+customClass+"' \
                            placeholder='"+parameter.name+"' rows='2'></textarea>";
        }
        else if(parameter.type == 'element'){
            var customClass = 'element-input';
            var input = "<input type='text' class='form-control \
                                    parameter-input "+customClass+"' \
                                    placeholder='"+parameter.name+"'>";
        }
        
        var newInput = $("<div class='col-sm-6 step-input-container parameter-container'> \
                            <div class='input-group'> \
                            "+input+" \
                            </div> \
                        </div>");

        newInput.on('change', function(){
            unsavedChanges = true;
        });

        step.find('.params').append(newInput);

        // five focus to the first parameter input
        step.find(".parameter-input").first().focus();

        getSelectedPageObjectElements()

        startAllValueInputAutocomplete();

        unsavedChanges = true;      
    }

    return false
}



function startAllValueInputAutocomplete(){

    var lookup = []

    var allValues = getLoadedDatosWithValues();

    for(value in allValues){
        lookup.push({
            'value': 'data.' + allValues[value].name,
            'data': 'data.' + allValues[value].name
        })        
    }

    $(".value-input").each(function(){

        autocomplete = $(this).autocomplete({
            lookup: lookup,
            minChars: 0,
            onSelect: function (suggestion) {
                //stepFirstInputChange($(this));
                unsavedChanges = true;
            },
            onSearchStart: function () {},
            beforeRender: function (container) {},
            onSearchComplete: function (query, suggestions) {
            }
        });
    })
}


function startAllElementInputAutocomplete(){

    var lookup = []

    //getSelectedPageObjectElements();

    for(elem in selectedPageObjectsElements){
        lookup.push({
            'value': selectedPageObjectsElements[elem].element_full_name,
            'data': selectedPageObjectsElements[elem].element_full_name
        })        
    }

    $(".element-input").each(function(){

        autocomplete = $(this).autocomplete({
            lookup: lookup,
            minChars: 0,
            onSelect: function (suggestion) {
                //stepFirstInputChange($(this));
                unsavedChanges = true;
            },
            onSearchStart: function () {},
            beforeRender: function (container) {},
            onSearchComplete: function (query, suggestions) {
            }
        });
    })

}


function isInPageObjectArray(value){
    for(po in pageObjects){
        if(value == pageObjects[po].value){
            return true;
        }
    }
    return false
}

function isInGlobalActions(value){
    for(ac in globalActions){
        if(value == globalActions[ac].name){
            return true
        }
    }
    return false
}

function getPageObjectDataFromPageObjects(poName){
    for(po in pageObjects){
        if(poName == pageObjects[po].value){
            return pageObjects[po]
        }
    }
}


function getLoadedDatos(){
    var datos = [];
    $(".dato").each(function(){
        datos.push(
            $(this).find(".dato-variable").val());
    });
    return datos;
}

function getLoadedDatosWithValues(){
    var datos = [];
    // $(".dato").each(function(){
    //     datos.push({
    //         'name': $(this).find(".dato-variable").val(),
    //         'value': $(this).find(".dato-value").val()
    //     });
    // });
    $("#dataTable thead input").each(function(){
        if($(this).val() != ''){
            datos.push({
                'name': $(this).val(),
                'value': $(this).val()
            });
        }
    });
    return datos;
}


function getGlobalActions(){
    $.ajax({
        url: "/get_global_actions/",
        data: {
        },
        dataType: 'json',
        type: 'POST',
        success: function(data) {
            globalActions = data;
            startStepFirstInputAutocomplete();
        },
        error: function() {}
    });   
}


function getGlobalActionParameters(actionName){
    for(a in globalActions){
        if(globalActions[a].name == actionName){
            return globalActions[a].parameters
        }
    }
    return false
}

function getPageObjectFunctionParameters(functionName){
    for(a in selectedPageObjectsFunctions){
        if(selectedPageObjectsFunctions[a].full_function_name == functionName){
            var parameters = [];
            for(p in selectedPageObjectsFunctions[a].arguments){
                var thisArgument = selectedPageObjectsFunctions[a].arguments[p];
                parameters.push({
                    name: thisArgument,
                    type: 'value'
                })
            }
            return parameters
        }
    }
    return false
}


function getSelectedPageObjectElements(){
    var selectedPageObjects = getSelectedPageObjects();

    selectedPageObjectsElements = [];

    for(po in selectedPageObjects){
        $.ajax({
            url: "/get_selected_page_object_elements/",
            data: {
                 "project": project,
                 "pageObject": selectedPageObjects[po],
             },
             dataType: 'json',
             type: 'POST',
             success: function(data) {
                // TODO, add elements and functions one by one

                // check if element does no already exist in selected ...
                if(data.element_list.length > 0){
                    if(! checkIfElementIsInSelectedPageObjectElements(
                                selectedPageObjectsElements,
                                data.element_list[0].element_full_name)){
                        selectedPageObjectsElements = selectedPageObjectsElements.concat(data.element_list);
                        startAllElementInputAutocomplete(); 
                    }
                }
                if(data.function_list.length > 0){
                    if(! checkIfFunctionIsInSelectedPageObjectFunctions(
                                                    selectedPageObjectsFunctions,
                                                    data.function_list[0].function_name)){
                        selectedPageObjectsFunctions = selectedPageObjectsFunctions.concat(data.function_list);
                        startStepFirstInputAutocomplete();
                    }
                }
             },
             error: function() {
             }
         });
    }
}


function saveTestCase(runAfter){
    runAfter = runAfter || false;
    if(!unsavedChanges){
        return
    }
    var description = $("#description").val();
    var pageObjects = getSelectedPageObjects();
    
    // get data from table
    var testData = dataTable.getData();

    var testSteps = {
        'setup': [],
        'test': [],
        'teardown': []
    };
    $("#setupSteps .step").each(function(){
        var thisStep = getThisStep(this);
        if(thisStep.action.length > 0){
            testSteps.setup.push(thisStep);    
        }
    });
    $("#testSteps .step").each(function(){
        var thisStep = getThisStep(this);
        if(thisStep.action.length > 0){
            testSteps.test.push(thisStep);    
        }
    });
    $("#teardownSteps .step").each(function(){
        var thisStep = getThisStep(this);
        if(thisStep.action.length > 0){
            testSteps.teardown.push(thisStep);    
        }
    });

    var data = {
        'description': description,
        'pageObjects': pageObjects,
        'testData': testData,
        'testSteps': testSteps,
        'project': project,
        'testCaseName': fullTestCaseName
    }

    $.ajax({
        url: "/save_test_case/",
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        success: function(data) {
            unsavedChanges = false;
            toastr.options = {
                "positionClass": "toast-top-center",
                "timeOut": "3000",
                "hideDuration": "100"}
            toastr.success("Test "+testCaseName+" saved")
            if(runAfter){
                testRunner.runTestCase();
            }
        },
        error: function() {
        }
    });
}


function dataTableHeaderInputChange(){
    startAllValueInputAutocomplete();
}


// U T I L S

function getSelectedPageObjects(){
    var selectedPageObjects = [];
    $(".page-objects-input").each(function(){
        if($(this).val().length > 0){
            selectedPageObjects.push($(this).val());
        }
    })
    return selectedPageObjects
}

function checkIfElementIsInSelectedPageObjectElements(selectedElements, elementName){
    for(elem in selectedPageObjectsElements){
        if(selectedPageObjectsElements[elem].element_full_name == elementName){
            return true
        }
    }
    return false
}

function checkIfFunctionIsInSelectedPageObjectFunctions(selectedFunctions, functionName){
    for(func in selectedPageObjectsFunctions){
        if(selectedPageObjectsFunctions[func].function_name == functionName){
            return true
        }
    }
    return false
}


function openPageObjectInNewWindow(elem){
    var inputVal = $(elem).parent().parent().find('input').val();
    if(inputVal.length > 0){
        var url = "/p/"+project+"/page/"+inputVal+"/";
        window.open(url, '_blank');
    }
}


function watchForUnsavedChanges(){
    $(".page-objects-input").on("change keyup paste", function(){
        unsavedChanges = true;
    });

    $(".step-first-input").on("change keyup paste", function(){
        unsavedChanges = true;
    });

    $(".parameter-input").on("change keyup paste", function(){
        unsavedChanges = true;
    });

    $("#description").on("change keyup paste", function(){
        unsavedChanges = true;
    });
    
    $("#dataTable").on("change keyup paste", function(){
        unsavedChanges = true;
    });

    window.addEventListener("beforeunload", function (e) {
        if(unsavedChanges){
            var confirmationMessage = 'There are unsaved changes';
            (e || window.event).returnValue = confirmationMessage; //Gecko + IE
            return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
        }
    });
}


function fillStepNumbering(){
    var count = 1;
    $("#setupSteps .step").each(function(){
        $(this).find('.step-numbering').html(count);
        count++;
    });
    var count = 1;
    $("#testSteps .step").each(function(){
        $(this).find('.step-numbering').html(count);
        count++;
    });
    var count = 1;
    $("#teardownSteps .step").each(function(){
        $(this).find('.step-numbering').html(count);
        count++;
    });
}


function deleteStep(elem){
    $(elem).parent().parent().remove();
    unsavedChanges = true;
}


function loadCodeView(){
    if(unsavedChanges){
        saveTestCase();
    }
    unsavedChanges = false;
    // redirect to gui view
    window.location.replace("/p/"+project+"/test/"+fullTestCaseName+"/code/");
}


function showSetupSteps(){
    $("#showSetupLink").hide();
    $("#setupSteps").slideDown('fast');
}


function showTeardownSteps(){
    $("#showTeardownLink").hide();
    $("#teardownSteps").slideDown('fast');
}


function startSortableSteps(){
    var setupSteps = $("#setupSteps .steps").get(0);
    var testSteps = $("#testSteps .steps").get(0);
    var teardownSteps = $("#teardownSteps .steps").get(0);
    var settings = {
        handle: '.step-numbering',        
        // Element dragging ended
        onEnd: function (/**Event*/evt) {
            fillStepNumbering();
        }
    };
    var sortable = Sortable.create(setupSteps, settings);
    var sortable = Sortable.create(testSteps, settings);
    var sortable = Sortable.create(teardownSteps, settings);
}


function getThisStep(elem){
    var thisStep = {
        'action': '',
        'parameters': []
    }
    if($(elem).find('.step-first-input').val().length > 0){
        thisStep.action = $(elem).find('.step-first-input').val();
        $(elem).find('.parameter-input').each(function(){
            thisStep.parameters.push($(this).val());
        });
    }
    return thisStep
}


function getPageObjectsNotYetSelected(){
    var selectedPageObjects = getSelectedPageObjects();
    var pageObjectsNotYetSelected = [];
    for(p in pageObjects){
        if($.inArray(pageObjects[p].data, selectedPageObjects) == -1){
            pageObjectsNotYetSelected.push(pageObjects[p]);
        }
    }
    return pageObjectsNotYetSelected
}

