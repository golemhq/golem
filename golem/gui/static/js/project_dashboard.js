
$(document).ready(function() {

    getTests(project);
    getPages(project);
    getSuites(project);

    $('#testCasesTree').treed();
    $('#pagesTree').treed();

    generateHealthChart(project);
});


function getTests(projectName){
    $.ajax({
        url: "/project/get_tests/",
        data: {
            "project": projectName
        },
        dataType: 'json',
        type: 'POST',
        success: function(tests) {
            $("#testCasesTree").append(Project.newElementForm());
            loadTreeElements($("#testCasesTree"), tests.sub_elements, 'test');
        },
    });
}


function getPages(projectName){
    $.ajax({
        url: "/project/get_pages/",
        data: {
            "project": projectName
        },
        dataType: 'json',
        type: 'POST',
        success: function(pages) {
            $("#pagesTree").append(Project.newElementForm());
            loadTreeElements($("#pagesTree"), pages.sub_elements, 'page');
        },
    });
}


function getSuites(projectName){
    $.ajax({
        url: "/project/get_suites/",
        data: {
            "project": projectName
        },
        dataType: 'json',
        type: 'POST',
        success: function(suites) {
            $("#suitesTree").append(Project.newElementForm());
            loadTreeElements($("#suitesTree"), suites.sub_elements, 'suite');
        },
    });
}


function loadTreeElements(rootElement, elements, elementType){
    elements.forEach(function(element){
        if(element.type == 'file'){
            var elementUrl = "/p/"+project+"/"+elementType+"/"+element.dot_path+"/";
            var uiElement = Project.generateNewElement({
                name: element.name,
                url: elementUrl,
                dotPath: element.dot_path, 
                type: elementType});
        }
        else if(element.type == 'directory'){
            var uiElement = Project.addBranchToTree(element.name, '');
            loadTreeElements(uiElement.find('ul'), element.sub_elements, elementType);
        }
        rootElement.children().last().before(uiElement);
    });
}

function displayNewElementForm(elem){
    var parent = $(elem).parent().parent();
    parent.find(".new-element-form").show().find("input").focus();
    parent.find(".display-new-element-link").hide();
}


function addElement(event){
    event.preventDefault();
    var input = $(event.target);
    var elementType = '';
    var urlPrefixForElementType = '';

    var closestTree = input.closest('.tree')
    if(closestTree.hasClass('test-tree')){
        elementType = 'test';
    }
    else if(closestTree.hasClass('page-tree')){
        elementType = 'page';
    }
    else if(closestTree.hasClass('suite-tree')){
        elementType = 'suite';
    }

    var elementName = input.val().trim();
    var fullPath = getElementFullPath(input, elementName);
    var isDir = false;
    if(elementName.indexOf('/') > -1){
        isDir = true;
        if(elementType == 'test') elementType = 'test_dir';
        else if(elementType == 'page') elementType = 'page_dir';
    }

    if(elementName.length == 0){
        input.val('');
        input.parent().hide();
        input.parent().parent().find(".display-new-element-link").show();
        return
    }

    // replace inner spaces with underscores
    elementName = elementName.replace(/ /g, '_');

    // validate length
    if(elementName.length > 60){
        displayErrorModal(['Maximum length is 60 characters']);
        return
    }
    // validate there is no more than 1 slash
    if(elementName.split('/').length -1 > 1){
        displayErrorModal(['Only one slash character is allowed']);
        return   
    }
    // validate there is no more than 1 slash
    if(elementType == 'suite' &&  elementName.split('/').length -1 == 1){
        displayErrorModal(['Suite names cannot contain slashes']);
        return   
    }
    // validate if there is a slash it is trailing
    if(isDir){
        if(elementName.indexOf('/') != elementName.length-1){
            displayErrorModal(['Directories should end with a trailing slash character']);
            return
        }
    }
    
    $.ajax({
        url: "/new_tree_element/",
        data: {
            "project": project,
            "elementType": elementType,
            "isDir": isDir,
            "fullPath": fullPath,
        },
        dataType: 'json',
        type: 'POST',
        success: function(data) {
            if(data.errors.length == 0){
                var parentUl = input.parent().parent().parent();
                if(data.element.is_directory){
                    var branch = Project.addBranchToTree(data.element.name);
                    parentUl.children().last().before(branch);
                }
                else{
                    var elementUrl = "/p/"+data.project_name+"/"+data.element.type+"/"+data.element.full_path+"/";
                    var uiElement = Project.generateNewElement({
                        name: data.element.name,
                        url: elementUrl,
                        dotPath: data.element.full_path, 
                        type: data.element.type});
                    parentUl.children().last().before(uiElement);
                }
                // reset the form, hide the form and display the add new link
                input.val("");
                input.parent().hide();
                input.parent().parent().find(".display-new-element-link").show();
            }
            else{
                displayErrorModal(data.errors);
            }
        },
        error: function() {}
    });
}


function getElementFullPath(elem, elementName){
    var dotted_branches = '';
    elem.parents('.branch').each(function(){
        if(dotted_branches.length == 0){
            dotted_branches = $(this).find('a').html();    
        }
        else {
            dotted_branches = $(this).find('a').html() + '.' + dotted_branches;
        }
    });
    if(dotted_branches.length == 0)
        return elementName
    else
        return dotted_branches + '.' + elementName
}


function removeTreeElement(elem){
    var parent = $(elem).parent().parent();
}


function generateHealthChart(projectName){
    $.ajax({
        url: "/report/get_project_health_data/",
        data: {
            "project": projectName,
        },
        dataType: 'json',
        type: 'POST',
        success: function( healthData ) { 
            if($.isEmptyObject(healthData)){
                $("#healthContainer").html("<div class='text-center' style='padding-top: 55px'>no data</div>");
            }
            else{
                loadHealthData(healthData);
            }
        }
    });
}


function loadHealthData(healthData){

    var totalOk = 0;
    var totalFail = 0;

    var table = "\
        <table id='healthTable' class='table no-margin-bottom last-execution-table'>\
            <thead>\
                <tr>\
                    <th>Suite</th>\
                    <th>Date &amp; Time</th>\
                    <th>Result</th>\
                </tr>\
            </thead>\
            <tbody>\
            </tbody>\
        </table>";
    $("#healthTableContainer").append(table);

    $.each(healthData, function(suite){
        var okPercentage = healthData[suite].total_ok * 100 / healthData[suite].total;
        var failPercentage = healthData[suite].total_fail * 100 / healthData[suite].total + okPercentage;
        totalOk += healthData[suite].total_ok;
        totalFail += healthData[suite].total_fail;

        var newRow = "\
            <tr class='cursor-pointer' onclick=''>\
                <td class=''>"+suite+"</td>\
                <td class=''>"+utils.getDateTimeFromTimestamp(healthData[suite].execution)+"</td>\
                <td class=''>\
                    "+reportUtils.generateProgressBars()+"\
                </td>\
            </tr>";
        newRow = $(newRow);

        newRow.attr('onclick', "document.location.href='/report/project/"+project+"/"+suite+"/"+healthData[suite].execution+"/'");

        $("#healthTable tbody").append(newRow);

        var okBar = newRow.find('.ok-bar');
        var failBar = newRow.find('.fail-bar');
        utils.animateProgressBar(okBar, okPercentage)
        utils.animateProgressBar(failBar, failPercentage)
    });

    var ctx = document.getElementById('healthChartCanvas').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Passed', 'Failed'],
            datasets: [
                {
                    data: [totalOk, totalFail],
                    backgroundColor: [
                        "rgb(66, 139, 202)",
                        "rgb(217, 83, 79)",
                    ],
                    hoverBackgroundColor: [
                        "rgb(66, 139, 202)",
                        "rgb(217, 83, 79)"
                    ]
                }
            ]
        },
        options: {
            animation: {
                animateScale: true,
                animateRotate: true
            },
            responsive: true,
            maintainAspectRatio : true,
        }
    });
}


function deleteElementConfirm(elementDeleteButton){
    var element =  $(elementDeleteButton).parent().parent();
    var elemFullPath = element.attr('fullpath');
    var elemType = element.attr('type');
    var message = 'Are you sure you want to delete <strong>' + elemFullPath + '</strong>?';
    var callback = function(){
        deleteElement(element, elemFullPath, elemType);
    }
    displayConfirmModal('Delete', message, callback);

}

function deleteElement(element, fullPath, elemType){
    $.ajax({
        url: "/delete_element/",
        data: {
            "project": project,
            "elemType": elemType,
            "fullPath": fullPath
        },
        dataType: 'json',
        type: 'POST',
        success: function(errors) {
            if(errors.length == 0){
                element.remove();
                toastr.options = {
                "positionClass": "toast-top-center",
                "timeOut": "2000",
                "hideDuration": "100"}
                toastr.success("File "+fullPath+" was removed")
            }
            else{
                toastr.options = {
                    "positionClass": "toast-top-center",
                    "timeOut": "2000",
                    "hideDuration": "100"}
                toastr.error('There was an error removing file');
            }
        },
    });
}


function duplicateElementPrompt(elementDuplicateButton){
    var element =  $(elementDuplicateButton).parent().parent();
    var elemFullPath = element.attr('fullpath');
    var elemType = element.attr('type');
    var title = 'Duplicate file';
    var message = 'Create a duplicate of <i>'+elemFullPath+'</i>. Enter a name for the new file..';
    var inputValue = elemFullPath;
    var callback = function(){
        duplicateFile(elemFullPath, elemType, element);
    }
    displayPromptModal(title, message, inputValue, callback)
}


function duplicateFile(elemFullPath, elemType, originalElement){
    var newFileFullPath = $("#promptModalInput").val();
    if(newFileFullPath === elemFullPath){
        // new file name is the same as original
        // don't show error message, do nothing
        return
    }

    $.ajax({
        url: "/duplicate_element/",
        data: {
            "project": project,
            "elemType": elemType,
            "fullPath": elemFullPath,
            "newFileFullPath": newFileFullPath
        },
        dataType: 'json',
        type: 'POST',
        success: function(errors) {
            if(errors.length == 0){
                var nameSplit = newFileFullPath.split('.');
                var name = nameSplit[nameSplit.length-1];
                var elementUrl = "/p/"+project+"/"+elemType+"/"+newFileFullPath+"/";
                var uiElement = Project.generateNewElement({
                    name: name,
                    url: elementUrl,
                    dotPath: newFileFullPath, 
                    type: elemType});
                var ul = originalElement.closest('ul');
                ul.children().last().before(uiElement);
                toastr.options = {
                "positionClass": "toast-top-center",
                "timeOut": "2000",
                "hideDuration": "100"}
                toastr.success("File was copied")
            }
            else{
                toastr.options = {
                    "positionClass": "toast-top-center",
                    "timeOut": "2000",
                    "hideDuration": "100"}
                toastr.error('There was an error duplicating the file');
            }
            $("#promptModal").modal("hide");
            $("#promptModal button.confirm").unbind('click');
        },
        error: function(){
            toastr.options = {
                "positionClass": "toast-top-center",
                "timeOut": "2000",
                "hideDuration": "100"}
            toastr.error('There was an error duplicating the file');
            $("#promptModal").modal('hide');
            $("#promptModal button.confirm").unbind('click');
        }
    });
}