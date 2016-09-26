
var pageObjects = [];

// var actions = [
//         {
//             'value': 'click',
//             'data': 'click'
//         },
//     ];

var globalActions = [];

var selectedPageObjectsElements = [];



$(document).ready(function() {      

    getGlobalActions();

    getPageObjects();

    //getDatosValues();

    getSelectedPageObjectElements();

    startAllElementInputAutocomplete();
            
    startAllValueInputAutocomplete();  


    $(".dato-variable").blur(function() {
        //alert('blur')
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

});


function addPOInput(){
    $("#pageObjects").append(
        "<div class='input-group'> \
            <input type='text' class='form-control custom-input page-objects-input page-objects-autocomplete'> \
            <span class='input-group-btn'> \
                <button class='btn btn-default' type='button' onclick='deleteInput(this)'> \
                    <span class='glyphicon glyphicon-remove' aria-hidden='true'></span> \
                </button> \
            </span> \
        </div>");

    startPageObjectsAutocomplete();
}


function addDatoInput(){
    $("#datos").append(
        "<div class='dato'> \
            <div class='col-sm-5'> \
                <div class='input-group'> \
                    <input type='text' class='form-control dato-variable' \
                        onchange='startAllValueInputAutocomplete();' value='' placeholder='nombre'> \
                </div> \
            </div> \
            <div class='col-sm-1'> \
                <label>=</label> \
            </div> \
            <div class='col-sm-6'> \
                <div class='input-group'> \
                    <input type='text' class='form-control dato-value' value='' placeholder='valor'> \
                    <span class='input-group-btn'> \
                        <button class='btn btn-default' type='button' onclick='deleteInputDato(this)'><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button> \
                    </span> \
                </div> \
            </div> \
        </div>");
}

function addFirstStepInput(){
    
    $("#steps").append(
        "<div class='step'> \
            <div class='col-sm-3'> \
                <div class='input-group'> \
                    <input type='text' class='form-control step-first-input' \
                        placeholder='action' onchange='stepFirstInputChange(this);'> \
                </div> \
            </div> \
        </div>");

    //onchange='stepFirstInputChange(this);'> \
    startStepFirstInputAutocomplete();
}


function deleteInput(elem){
    $(elem).parent().parent().remove();
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
                console.log(data)
                var po = data[po];
                pageObjects.push({
                    // 'value': po.name.split('.')[0],
                    // 'data': po,
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

    console.log("get page object actions");

    autocomplete = $(".step-first-input").autocomplete({
        lookup: lookup,
        minChars: 0,
        //triggerSelectOnValidInput: false,
        onSelect: function (suggestion) {
            stepFirstInputChange($(this));
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
    //var hasValueInput = step.find(".value-input").length > 0;
    //var hasElementInput= step.find(".element-input").length > 0;
    var hasParameter = step.find('.parameter-input').length > 0
    var placeholder = ''
    var elemValue = $(elem).val();
    //var isPageObject = isInPageObjectArray(elemValue);
    
    if(!hasParameter){     

        var pageObjects = getSelectedPageObjects();

        var actionParameters = getGlobalActionParameters(elemValue);

        if(!actionParameters){
            //is not a global action
            console.log("search in page object actions");
        }

        for(p in actionParameters){
            var parameter = actionParameters[p];    

            if(parameter.type == 'value'){
                var customClass = 'value-input';
            }
            else if(parameter.type == 'element'){
                var customClass = 'element-input';
            }
            
            var newInput = $("<div class='col-sm-3 parameter-container'> \
                                <div class='input-group'> \
                                    <input type='text' class='form-control \
                                        parameter-input "+customClass+"' \
                                        placeholder='"+parameter.name+"' onchange=''> \
                                </div> \
                            </div>");

            step.append(newInput);

            //startAllElementInputAutocomplete();
            // start all elements input through getselectedpageobjectelements function()
            getSelectedPageObjectElements()

            startAllValueInputAutocomplete();    
        }
    }
    else{
        step.find('.parameter-container').remove();
    }
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
            },
            onSearchStart: function () {},
            beforeRender: function (container) {},
            onSearchComplete: function (query, suggestions) {
            }
        });
    })

}


// function getPageObjectElements(pageObjectName, input){
//     var pageObjectData = getPageObjectDataFromPageObjects(pageObjectName);

//     $.ajax({
//         url: "/get_page_object_elements/",
//         data: {
//             "project": project,
//             "canal": canal,
//             "pageObjectPath": pageObjectData.data['path'],
//             "pageObjectName": pageObjectData.data['name'],
//         },
//         dataType: 'json',
//         type: 'POST',
//         success: function(data) {
//             startWebElementAutocomplete(data, input);
//         },
//         error: function() {
            
//         }
//     });
// }


function startWebElementAutocomplete(data, input){
    var lookup = []
    for(we in data.web_elements){
        lookup.push({
            'value': data.web_elements[we],
            'data': data.web_elements[we]
        })
    }

    autocomplete = input.autocomplete({
        lookup: lookup,
        minChars: 0,
        onSelect: function (suggestion) {
            addThirdStepTextBox($(this));
        },
        onSearchStart: function () {
        },
        beforeRender: function (container) {},
        onSearchComplete: function (query, suggestions) {
        }
    });
}


function addThirdStepTextBox(elem){
    var step = $(elem).parent().parent().parent();
    var alreadyHasSecondStep = step.find(".third-second-input").length > 0;

    if(!alreadyHasSecondStep){

        var placeholder = 'acción';

        step.append(
            "<div class='col-sm-3'> \
                <div class='input-group'> \
                    <input type='text' class='form-control third-second-input' \
                        placeholder='"+placeholder+"' onchange='stepThirdInputChange(this);'> \
                </div> \
            </div>");

        startActionAutocomplete(step.find(".third-second-input"));
    }
}


// function startActionAutocomplete(elem){
//     autocomplete = elem.autocomplete({
//         lookup: actions,
//         minChars: 0,
//         onSelect: function (suggestion) {
//             if(suggestion.value != 'click'){
//                 addFourthStepTextBox($(this));
//             }
//         },
//         onSearchStart: function () {
//         },
//         beforeRender: function (container) {},
//         onSearchComplete: function (query, suggestions) {
//         }
//     });
// }

function addFourthStepTextBox(elem){
    var step = $(elem).parent().parent().parent();
    var alreadyHasFourthStep = step.find(".fourth-second-input").length > 0;

    if(!alreadyHasFourthStep){

        var placeholder = 'valor a utilizar';

        step.append(
            "<div class='col-sm-3'> \
                <div class='input-group'> \
                    <input type='text' class='form-control fourth-second-input' \
                        placeholder='"+placeholder+"' onchange='stepFourthInputChange(this);'> \
                </div> \
            </div>");

        startFourthStepAutocomplete(step.find(".fourth-second-input"));
    }
}


function getDatosValues(){
    $.ajax({
        url: "/get_datos_values/",
        data: {
            "project": project,
            "canal": canal,
            "testCaseName": testCaseName,
        },
        dataType: 'json',
        type: 'POST',
        success: function(data) {
            console.log(data);
            for(dt in data){
                $(".dato").each(function(){
                    if($(this).find(".dato-variable").val() == data[dt].name){
                        $(this).find(".dato-value").val(data[dt].value);
                    }
                })
            }
        },
        error: function() {
            
        }
    });
}


function startFourthStepAutocomplete(elem){
    var datos = getLoadedDatos();
    var lookup = [];
    for(d in datos){
        lookup.push({
            'value': datos[d],
            'data': datos[d],
        })
    }
    autocomplete = elem.autocomplete({
        lookup: lookup,
        minChars: 0,
        onSelect: function (suggestion) {
        },
        onSearchStart: function () {
        },
        beforeRender: function (container) {},
        onSearchComplete: function (query, suggestions) {
        }
    });
}











// function saveTestCase(){
//     var testCaseName = $("#testCaseName").html();
//     var pageObjects = getSelectedPageObjects();
//     var datos = getLoadedDatosWihValues();
//     var steps;
// }
















function isInPageObjectArray(value){
    for(po in pageObjects){
        if(value == pageObjects[po].value){
            return true;
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
                // check if element does no already exist in selected ...
                if(! checkIfElementIsInSelectedPageObjectElements(
                            selectedPageObjectsElements,
                            data[0].element_full_name)){
                    selectedPageObjectsElements = selectedPageObjectsElements.concat(data);
                    startAllElementInputAutocomplete();
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
        pageObjects.push($(this).val());
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

        thisStep.action = $(this).find('.step-first-input').val();

        $(this).find('.parameter-input').each(function(){
            thisStep.parameters.push($(this).val());
        });

        testSteps.push(thisStep);
    });

    var data = {
        'description': description,
        'pageObjects': pageObjects,
        'testData': testData,
        'testSteps': testSteps,
        'project': project,
        'testCaseName': testCaseName
    }

    $.ajax({
        url: "/save_test_case/",
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        success: function(data) {
        },
        error: function() {
        }
    });
}




function runTestCase(){
    $.ajax({
        url: "/run_test_case/",
        data: {
             "project": project,
             "testCaseName": testCaseName,
         },
         dataType: 'json',
         type: 'POST',
         success: function(data) {
            
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