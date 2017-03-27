
var pageObjects = [];
var globalActions = [];
var selectedPageObjectsElements = [];
var selectedPageObjectsFunctions = [];

var unsavedChanges = false;

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
            //alert('keyup')
        startAllValueInputAutocomplete();
    });

    $(".page-objects-input").blur(function() {
        //alert('blur')
        getSelectedPageObjectElements();
    });

    $(".page-objects-input").keyup(function(e) {
        if (e.which == 13) // Enter key
            //alert('keyup')
        getSelectedPageObjectElements();
    });

    // set unsaved changes watcher
    watchForUnsavedChanges();

    // start sortable steps
    var el = document.getElementById('steps');
    var sortable = Sortable.create(el, {
        handle: '.step-numbering',        
        // Element dragging ended
        onEnd: function (/**Event*/evt) {
            fillStepNumbering();
        },
    });
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


function addFirstStepInput(){
    
    // var nextStepNumber = $(".step-first-input").length + 1;

    $("#steps").append(
        "<div class='step'> \
            <div class='step-numbering'></div> \
            <div class='col-sm-3 step-input-container'> \
                <div class='input-group'> \
                    <input type='text' class='form-control step-first-input' \
                        placeholder='action' onchange=''> \
                </div> \
            </div> \
            <div class='step-remove-icon'> \
                <a href='javascript:void(0)' onclick='deleteStep(this);'> \
                    <span class='glyphicon glyphicon-remove' aria-hidden='true'></span> \
                </a> \
            </div> \
        </div>");

    // was failing with onchange, calling the function twice
    // stepFirstInputChange(this); return false

    // give focus to the last step action input
    $(".step-first-input").last().focus();

    fillStepNumbering();

    //onchange='stepFirstInputChange(this);'> \
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
        lookup: pageObjects,
        minChars: 0,
        onSelect: function (suggestion) {
            getSelectedPageObjectElements();
            unsavedChanges = true;
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
    console.log('called');
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
        }
        else if(parameter.type == 'element'){
            var customClass = 'element-input';
        }
        
        var newInput = $("<div class='col-sm-3 step-input-container parameter-container'> \
                            <div class='input-group'> \
                                <input type='text' class='form-control \
                                    parameter-input "+customClass+"' \
                                    placeholder='"+parameter.name+"' onchange=''> \
                            </div> \
                        </div>");

        newInput.on('change', function(){
            unsavedChanges = true;
        });

        step.append(newInput);

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
            'value': allValues[value].name,
            'data': allValues[value].name
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
        console.log(selectedPageObjects[po]);
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


function saveTestCase(){

    var description = $("#description").val();

    var pageObjects = [];
    $(".page-objects-input").each(function(){
        if($(this).val().length > 0){
            pageObjects.push($(this).val());
        }
    });

    var testData = [];
    
    var headerInputs = $("#dataTable thead input")    
    var tableRows = $("#dataTable tbody tr");
    
    tableRows.each(function(){
        var currentRow = $(this);
        var rowCells = currentRow.find("td input");
        var rowDict = {}
        rowCells.each(function(i){
            //console.log($(headerInputs[i]).val());
            if($(headerInputs[i]).val().length > 0){
                rowDict[$(headerInputs[i]).val()] = $(this).val();
            }
        });
        if(!jQuery.isEmptyObject(rowDict)){
            testData.push(rowDict)
        }
    });
    // empty values are allowed but only for one row of data
    var tempTestData = [testData[0]];
    for(var i = 1; i <= testData.length - 1; i++){
        var allEmpty = true;
        for(key in testData[i]){
            if(testData[i][key].length > 0){
                allEmpty = false
            }
        }
        if(!allEmpty){
            tempTestData.push(testData[i])
        }
    }
    testData = tempTestData;

    var testSteps = [];
    $(".step").each(function(){
        var thisStep = {
            'action': '',
            'parameters': []
        }
        if($(this).find('.step-first-input').val().length > 0){
            thisStep.action = $(this).find('.step-first-input').val();

            $(this).find('.parameter-input').each(function(){
                thisStep.parameters.push($(this).val());
            });

            testSteps.push(thisStep);
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
            toastr.success("Test case "+testCaseName+" saved")
        },
        error: function() {
        }
    });
}


function runTestCase(){
    toastr.options = {
        "positionClass": "toast-top-center",
        "timeOut": "3000",
        "hideDuration": "100"}
    toastr.info('Running test case ' + testCaseName);
    $.ajax({
        url: "/run_test_case/",
        data: {
             "project": project,
             "testCaseName": fullTestCaseName,
         },
         dataType: 'json',
         type: 'POST',
         success: function(data) {
            var timestamp = data;
            checkTestCaseResult(project, fullTestCaseName, timestamp);
         },
         error: function() {}
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

function addColumnToDataTable(){
    $("#dataTable thead tr").append(
        "<th> \
            <div class='input-group'> \
                <input class='form-control' type='text'> \
            </div> \
        </th>"
    );

    $("#dataTable tbody tr").each(function(){
        $(this).append(
            "<td> \
                <div class='input-group'> \
                    <input class='form-control' type='text'> \
                </div> \
            </td>"
        );
    });
}

function addRowToDataTable(){
    var amountOfColumns = $("#dataTable thead tr th").length -1;
    var amountOfRows = $("#dataTable tbody tr").length;
    var newCells = "";
    for(var i = 0; i < amountOfColumns; i++){
        newCells += "<td> \
                        <div class='input-group'> \
                            <input class='form-control' type='text'> \
                        </div> \
                    </td>";
    }
    
    $("#dataTable tbody").append(
        "<tr> \
            <th scope='row' class='index'>"+(amountOfRows+1)+"</th> \
            " + newCells + " \
        </tr>");
}


function openPageObjectInNewWindow(elem){
    var inputVal = $(elem).parent().parent().find('input').val();
    var url = "/p/"+project+"/page/"+inputVal+"/";
    window.open(url, '_blank');
}


function watchForUnsavedChanges(){
    $("input").on("change keyup paste", function(){
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
    $(".step").each(function(){
        $(this).find('.step-numbering').html(count);
        count++;
    });
}


function deleteStep(elem){
    $(elem).parent().parent().remove();
    unsavedChanges = true;
}


function checkTestCaseResult(project, fullTestCaseName, timestamp){

    $("#testRunModal").modal("show");

    $("#testRunModal .modal-title").html('Running Test Case');

    $("#loaderContainer").show();

    $("#testResultContainer").html('');

    checkAndRecheckStatus(project, fullTestCaseName, timestamp);
}

function checkAndRecheckStatus(project, fullTestCaseName, timestamp){

    $.ajax({
        url: "/check_test_case_run_result/",
        data: {
             "project": project,
             "testCaseName": fullTestCaseName,
             "timestamp": timestamp
         },
         dataType: 'json',
         type: 'POST',
         success: function(data) {
            if(data.status == 'not_complete'){
                setTimeout(function(){
                    checkAndRecheckStatus(project, fullTestCaseName, timestamp);
                }, 500, project, fullTestCaseName, timestamp);
            }
            else{
                $("#loaderContainer").hide();

                $("#testRunModal .modal-title").html('Result');

                $("#testResultContainer").html('');

                $("#testResultContainer").append('<span><strong>Result:</strong> ' + data.report_data.result + '</span><br>');
                $("#testResultContainer").append('<span><strong>Error:</strong> ' + data.report_data.short_error + '</span><br>');
                $("#testResultContainer").append('<span><strong>Elapsed Time:</strong> ' + data.report_data.test_elapsed_time + '</span><br>');
                $("#testResultContainer").append('<span><strong>Browser:<strong> ' + data.report_data.browser + '</span><br>');
                $("#testResultContainer").append('<span><strong>Steps:</strong></span>');
                $("#testResultContainer").append("<ol style='margin-left: 20px'></ol>");
                for(s in data.report_data.steps){
                    $("#testResultContainer ol").append('<li>' + data.report_data.steps[s] + '</li>')
                }
                $("#testResultContainer").append('</ol>')
            }
         },
         error: function() {}
     });
}