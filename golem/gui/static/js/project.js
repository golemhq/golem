
var Project = new function(){

    this.generateNewElement = function(element){
        var li = "\
            <li class='tree-element' fullpath='"+element.dotPath+"' name='"+element.name+"' type='"+element.type+"'>\
                <a href='"+element.url+"'>"+element.name+"</a> \
                <span class='pull-right tree-element-buttons'> \
                    <button onclick='Project.duplicateElementPrompt(this)'><i class='glyphicon glyphicon-copy'></i></button> \
                    <button onclick='Project.deleteElementConfirm(this)'><i class='glyphicon glyphicon-remove'></i></button> \
                </span>\
            </li>";
            //<button onclick=''><i class='glyphicon glyphicon-edit'></i></button> \
        return $(li)
    }

    this.addBranchToTree = function(branchName, dot_path){
        var openedClass = 'glyphicon-folder-open';
        var closedClass = 'glyphicon-folder-close';
        var li = "\
            <li class='tree-element branch' name='"+branchName+"' fullpath='"+dot_path+"'>\
                <a href='#'>"+branchName+"</a> \
                <span class='pull-right tree-element-buttons'> \
                </span> \
                <ul>\
                    "+this.newElementForm(dot_path)+"\
                </ul>\
            </li>";
            //<button><i class='glyphicon glyphicon-edit'></i></button> \
            //<button><i class='glyphicon glyphicon-copy'></i></button> \
            //<button><i class='glyphicon glyphicon-remove'></i></button> \
        var branch = $(li);
        branch.prepend("<i class='indicator glyphicon " + closedClass + "'></i>");
        branch.on('click', function (e) {
            if (this == e.target) {
                var icon = $(this).children('i:first');
                icon.toggleClass(openedClass + " " + closedClass);
                $(this).children('ul').toggle();
                $(this).children('span.new-element-form').toggle();
            }
        })
        branch.children('ul').hide();
        branch.children('span.new-element-form').hide();

        //fire event from the dynamically added icon
        branch.find('.indicator').each(function(){
           $( this).on('click', function () {
                $(this).closest('li').click();
            });
        });
        //fire event to open branch if the li contains an anchor instead of text
        branch.find('a').each(function () {
            $(this).on('click', function (e) {
                $(this).closest('li').click();
                e.preventDefault();
            });
        });
        //fire event to open branch if the li contains a button instead of text
        branch.find('button').each(function () {
            $(this).on('click', function (e) {
                $(this).closest('li').click();
                e.preventDefault();
            });
        });
        return branch
    };

    this.newElementForm = function(dot_path){
        var li = "\
            <li class='form-container' fullpath='"+dot_path+"'>\
            <span class='new-element-form' style='display: none;'>\
                <input class='new-element-input new-test-case' type='text'\
                    onblur='Project.addElement(event);' onkeyup='if(event.keyCode==13){Project.addElement(event)}'>\
            </span>\
            <span class='display-new-element-link'>\
                <a class='new-element-link' href='javascript:void(0)' onclick='Project.displayNewElementForm(this, \"file\")'><i class='glyphicon glyphicon-file'><i style='left: -3px' class='fa fa-plus-circle fa-stack-1x awesomeEntity sub-icon'/></i></a>\
                <a class='new-directory-link' href='javascript:void(0)' onclick='Project.displayNewElementForm(this, \"directory\")'><i class='glyphicon glyphicon-folder-close'><i style='left: 0px' class='fa fa-plus-circle fa-stack-1x awesomeEntity sub-icon'/></i></a>\
        </li>";
        //<a class='new-element-link' href='javascript:void(0)' onclick='Project.displayNewElementForm(this)'><i class='glyphicon glyphicon-plus-sign'></i> Add</a>\
        return li
    }

    this.loadTreeElements = function(rootElement, elements, elementType){
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
                Project.loadTreeElements(uiElement.find('ul'), element.sub_elements, elementType);
            }
            rootElement.children().last().before(uiElement);
        });
    }

    this.displayNewElementForm = function(elem, elemType){
        var parent = $(elem).parent().parent();
        parent.find(".new-element-form").show().find("input").attr('elem-type', elemType).focus();
        parent.find(".display-new-element-link").hide();
    }

    this.addElement = function(event){
        event.preventDefault();
        var input = $(event.target);
        var elementType = '';
        var urlPrefixForElementType = '';
        var isDir = input.attr('elem-type') == 'directory';

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
        //elementName = elementName.replace(/ /g, '_');
        
        var fullPath = Project.getElementFullPath(input, elementName);
        // var isDir = false;
        // if(elementName.indexOf('/') > -1){
        //     isDir = true;
        //     if(elementType == 'test') elementType = 'test_dir';
        //     else if(elementType == 'page') elementType = 'page_dir';
        // }
        // if(elementName[elementName.length-1] == '/'){
        //     isDir = true;
        //     if(elementType == 'test') elementType = 'test_dir';
        //     else if(elementType == 'page') elementType = 'page_dir';
        // }

        if(elementName.length == 0){
            input.val('');
            input.parent().hide();
            input.parent().parent().find(".display-new-element-link").show();
            return
        }

        // validate length
        if(elementName.length > 100){
            utils.displayErrorModal(['Maximum length is 100 characters']);
            return
        }

        // validate there is no more than 1 slash
        // if(elementName.split('/').length -1 > 1){
        //     displayErrorModal(['Only one slash character is allowed']);
        //     return   
        // }

        // validate there is no more than 1 slash
        // if(elementType == 'suite' &&  elementName.indexOf('/') > -1){ //elementName.split('/').length -1 == 1){
        //     displayErrorModal(['Suite names cannot contain slashes']);
        //     return   
        // }

        // validate if there is a slash it is trailing
        // if(isDir){
        //     if(elementName.indexOf('/') != elementName.length-1){
        //         displayErrorModal(['Directories should end with a trailing slash character']);
        //         return
        //     }
        // }
        
        $.ajax({
            url: "/new_tree_element/",
            data: {
                "project": project,
                "elementType": elementType,
                "isDir": isDir,
                "fullPath": fullPath,
                "addParents": false
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
                    utils.displayErrorModal(data.errors);
                }
            },
            error: function() {}
        });
    }


    this.getElementFullPath = function(elem, elementName){
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

    this.deleteElementConfirm = function(elementDeleteButton){
        var element =  $(elementDeleteButton).parent().parent();
        var elemFullPath = element.attr('fullpath');
        var elemType = element.attr('type');
        var message = 'Are you sure you want to delete <strong>' + elemFullPath + '</strong>?';
        var callback = function(){
            Project.deleteElement(element, elemFullPath, elemType);
        }
        utils.displayConfirmModal('Delete', message, callback);

    }


    this.deleteElement = function(element, fullPath, elemType){
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


    this.duplicateElementPrompt = function(elementDuplicateButton){
        var element =  $(elementDuplicateButton).parent().parent();
        var elemFullPath = element.attr('fullpath');
        var elemType = element.attr('type');
        var title = 'Duplicate file';
        var message = 'Create a duplicate of <i>'+elemFullPath+'</i>. Enter a name for the new file..';
        var inputValue = elemFullPath;
        var placeholderValue = '';
        var callback = function(newFileFullPath){
            Project.duplicateFile(elemFullPath, elemType, element, newFileFullPath);
        }
        utils.displayPromptModal(title, message, inputValue, placeholderValue, callback)
    }


    this.duplicateFile = function(elemFullPath, elemType, originalElement, newFileFullPath){
        //var newFileFullPath = $("#promptModalInput").val();
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

}