
$(document).ready(function() {
    getTests(project);
    $('#testCasesTree').treed();
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
            $("#testCasesTree").append(Project.newElementForm('.'));
            loadTreeElements($("#testCasesTree"), tests.sub_elements, 'test');
        },
    });
}


function loadTreeElements(rootElement, elements, elementType){
    elements.forEach(function(element){
        if(element.type == 'file'){
            var elementUrl = "/project/"+project+"/"+elementType+"/"+element.dot_path+"/";
            var uiElement = Project.generateNewElement({
                name: element.name,
                url: elementUrl,
                dotPath: element.dot_path, 
                type: elementType});
        }
        else if(element.type == 'directory'){
            var uiElement = Project.addBranchToTree(element.name, element.dot_path);
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

    // replace inner spaces with underscores
    elementName = elementName.replace(/ /g, '_');
    
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
                    var branch = Project.addBranchToTree(data.element.name, data.element.full_path);
                    parentUl.children().last().before(branch);
                }
                else{
                    var elementUrl = "/project/"+data.project_name+"/"+data.element.type+"/"+data.element.full_path+"/";
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
                utils.toast('success', "File "+fullPath+" was removed", 2000)
            }
            else{
                utils.toast('error', 'There was an error removing file', 2000)
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
                var elementUrl = "/project/"+project+"/"+elemType+"/"+newFileFullPath+"/";
                var uiElement = Project.generateNewElement({
                    name: name,
                    url: elementUrl,
                    dotPath: newFileFullPath, 
                    type: elemType});
                var ul = originalElement.closest('ul');
                ul.children().last().before(uiElement);
                utils.toast('success', 'File was copied', 2000)
            }
            else{
                utils.toat('error', 'There was an error duplicating the file', 2000);
            }
            $("#promptModal").modal("hide");
            $("#promptModal button.confirm").unbind('click');
        },
        error: function(){
            utils.toast('error', 'There was an error duplicating the file', 2000)
            $("#promptModal").modal('hide');
            $("#promptModal button.confirm").unbind('click');
        }
    });
}