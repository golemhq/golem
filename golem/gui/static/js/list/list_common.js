
const Project = new function(){

    this.generateNewElement = function(element){
        let li = $(`<li class="tree-element"fullpath="${element.dotPath}" name="${element.name}" type="${element.type}">
                        <a class="list-item-link" href="${element.url}">${element.name}</a>
                <span class="pull-right tree-element-buttons">
                    <button class="rename-button" onclick="Project.renameFilePrompt(this)"><i class="glyphicon glyphicon-edit"></i></button>
                    <button class="duplicate-button" onclick="Project.duplicateElementPrompt(this)"><i class="glyphicon glyphicon-duplicate"></i></button>
                    <button class="delete-button" onclick="Project.deleteElementConfirm(this)"><i class="glyphicon glyphicon-trash"></i></button>
                </span>
            </li>`);
        if(element.type == 'test' || element.type == 'page'){
            let codeIcon = '<i class="glyphicon glyphicon-chevron-left" style="-webkit-text-stroke: 0.5px white;"></i><i class="glyphicon glyphicon-chevron-right" style="margin-left: -8px; -webkit-text-stroke: 0.5px white;"></i>';
            let codeLink = `<a href="${element.url}code" class="code-button" style="margin-right: -2px;">${codeIcon}</a>`;
            li.find("span.tree-element-buttons").prepend(codeLink);
            if(element.type == 'test'){
                let runButton = `<button class="run-test-button" onclick="Main.TestRunner.openConfigModal(project, '${element.dotPath}')"><is class="glyphicon glyphicon-play-circle"></span></button>`;
                li.find("span.tree-element-buttons").prepend(runButton);
            }
        }
        return li
    }

    this.generateNewBranch = function(branchName, dot_path){
        let openedClass = 'glyphicon-folder-open';
        let closedClass = 'glyphicon-folder-close';
        let li = `
            <li class="tree-element branch" name="${branchName}" fullpath="${dot_path}">
                <a href="#">${branchName}</a>
                <span class="pull-right tree-element-buttons">
                </span>
                <ul>${this.newElementForm(dot_path)}</ul>
            </li>`;
        let branch = $(li);
        branch.prepend(`<i class="indicator glyphicon ${closedClass}"></i>`);
        branch.on('click', function (e) {
            if (this == e.target) {
                let icon = $(this).children('i:first');
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
        let li = `
            <li class="form-container" fullpath="${dot_path}">
            <span class="new-element-form" style="display: none;">
                <input class="new-element-input new-test-case form-control" type="text"
                    onblur="Project.addElement(event);" onkeyup="if(event.keyCode==13){Project.addElement(event)}">
            </span>
            <span class="display-new-element-link">
                <a class="new-element-link" href="javascript:void(0)" onclick="Project.displayNewElementForm(this, 'file')">
                    <i class="glyphicon glyphicon-file"><i style="left: -3px" class="fa fa-plus-circle fa-stack-1x awesomeEntity sub-icon"/></i>
                </a>
                <a class="new-directory-link" href="javascript:void(0)" onclick="Project.displayNewElementForm(this, 'directory')">
                    <i class="glyphicon glyphicon-folder-close"><i style="left: 0px" class="fa fa-plus-circle fa-stack-1x awesomeEntity sub-icon"/></i>
                </a>
        </li>`;
        return li
    }

    this.loadTreeElements = function(rootElement, elements, elementType){
        elements.forEach(function(element){
            let uiElement;
            if(element.type == 'file'){
                let elementUrl = `/project/${project}/${elementType}/${element.dot_path}/`;
                uiElement = Project.generateNewElement({
                    name: element.name,
                    url: elementUrl,
                    dotPath: element.dot_path, 
                    type: elementType});
            }
            else { // element.type == 'directory'
                uiElement = Project.generateNewBranch(element.name, element.dot_path);
                Project.loadTreeElements(uiElement.find('ul'), element.sub_elements, elementType);
            }
            rootElement.children().last().before(uiElement);
        });
    }

    this.addFileToTree = function(fullPath, elementType){
        let rootElement = $("#treeRoot")
        let pathList = fullPath.split('.')
        let fileName = pathList.pop();
        let loadedPath = []
        // add directories if they don't exist already
        let length_ = pathList.length;
        for(let i=0; i <= length_-1; i++){
            let dirName = pathList.shift();
            loadedPath.push(dirName);
            let thisDirFullPath = loadedPath.join('.');
            let branch;
            if(!Project.dirExists(thisDirFullPath)){
                branch= Project.generateNewBranch(dirName, thisDirFullPath);
                rootElement.children().last().before(branch)
            }
            else{
                branch = Project.getDirElement(thisDirFullPath)
            }
            rootElement = branch.find('>ul');
        }
        // add file
        loadedPath.push(fileName);
        let testFullPath = loadedPath.join('.');
        let elementUrl = `/project/${project}/${elementType}/${testFullPath}/`;
        let uiElement = Project.generateNewElement({
            name: fileName,
            url: elementUrl,
            dotPath: testFullPath,
            type: elementType});
        rootElement.children().last().before(uiElement);
    }

    this.displayNewElementForm = function(elem, elemType){
        let parent = $(elem).parent().parent();
        parent.find(".new-element-form").show().find("input").attr('elem-type', elemType).focus();
        parent.find(".display-new-element-link").hide();
    }

    this.addElement = function(event){
        event.preventDefault();
        let input = $(event.target);
        let elementType = '';
        let urlPrefixForElementType = '';
        let isDir = input.attr('elem-type') == 'directory';
        let closestTree = input.closest('.tree')
        if(closestTree.hasClass('test-tree')){
            elementType = 'test';
        }
        else if(closestTree.hasClass('page-tree')){
            elementType = 'page';
        }
        else if(closestTree.hasClass('suite-tree')){
            elementType = 'suite';
        }
        let elementName = input.val().trim().replace(/\s/g, '_');
        let fullPath = Project.getElementFullPath(input, elementName)

        if(elementName.length == 0){
            input.val('');
            input.parent().hide();
            input.parent().parent().find(".display-new-element-link").show();
            return
        }

        let errors = Main.Utils.validateFilename(elementName, isDir);
        if(errors.length > 0){
            Main.Utils.displayErrorModal(errors);
            return
        }
        let endpointURL;
        if(elementType == 'test')
            endpointURL = '/api/project/test'
        else if(elementType == 'page')
            endpointURL = '/api/project/page'
        else
            endpointURL = '/api/project/suite'

        $.ajax({
            url: endpointURL,
            data: JSON.stringify({
                "project": project,
                "isDir": isDir,
                "fullPath": fullPath
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                if(data.errors.length == 0){
                    let parentUl = input.closest('ul');
                    if(data.element.is_directory){
                        let branch = Project.generateNewBranch(data.element.name, data.element.full_path);
                        parentUl.children().last().before(branch);
                    }
                    else{
                        Project.addFileToTree(data.element.full_path, data.element.type);
                    }
                    // reset the form, hide the form and display the add new link
                    input.val("");
                    input.parent().hide();
                    input.parent().parent().find(".display-new-element-link").show();
                }
                else{
                    Main.Utils.displayErrorModal(data.errors);
                }
            },
            error: function() {}
        });
    }

    this.getElementFullPath = function(elem, elementName){
        let dotted_branches = '';
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
        let element =  $(elementDeleteButton).parent().parent();
        let elemFullPath = element.attr('fullpath');
        let elemType = element.attr('type');
        let message = `<span style="word-break: break-all">Are you sure you want to delete <strong>${elemFullPath}</strong>?</span>`;
        let callback = function(){
            Project.deleteElement(element, elemFullPath, elemType);
        }
        Main.Utils.displayConfirmModal('Delete', message, callback);
    }

    this.deleteElement = function(element, fullPath, elemType){
        let endpointURL;
        if(elemType == 'test')
            endpointURL = '/api/test/delete'
        else if(elemType == 'page')
            endpointURL = '/api/page/delete'
        else
            endpointURL = '/api/suite/delete'
        $.ajax({
            url: endpointURL,
            data: JSON.stringify({
                "project": project,
                "fullPath": fullPath
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            type: 'DELETE',
            success: function(errors) {
                if(errors.length == 0){
                    element.remove();
                    Main.Utils.toast('success', `File ${fullPath} was removed`, 2000)
                }
                else{
                    Main.Utils.toast('error', 'There was an error removing file', 2000)
                }
            },
        });
    }

    this.duplicateElementPrompt = function(elementDuplicateButton){
        let element =  $(elementDuplicateButton).parent().parent();
        let elemFullPath = element.attr('fullpath');
        let elemType = element.attr('type');
        let title = 'Copy file';
        let message = `<span style="word-break: break-all">Create a copy of <i>${elemFullPath}</i>. Enter a name for the new file...</span>`;
        let inputValue = elemFullPath;
        let placeholderValue = '';
        let callback = function(newFileFullPath){
            Project.duplicateFile(elemFullPath, elemType, element, newFileFullPath);
        }
        Main.Utils.displayPromptModal(title, message, inputValue, placeholderValue, callback)
    }

    this.duplicateFile = function(elemFullPath, elemType, originalElement, newFileFullPath){
        if(newFileFullPath === elemFullPath){
            // new file name is the same as original
            // don't show error message, do nothing
            return
        }

        let errors = Main.Utils.validateFilename(newFileFullPath);
        if(errors.length > 0){
            Main.Utils.displayErrorModal(errors);
            return
        }
        let endpointURL;
        if(elemType == 'test') { endpointURL = '/api/test/duplicate' }
        else if(elemType == 'page') { endpointURL = '/api/page/duplicate' }
        else { endpointURL = '/api/suite/duplicate' }
        $.ajax({
            url: endpointURL,
            data: JSON.stringify({
                "project": project,
                "fullPath": elemFullPath,
                "newFileFullPath": newFileFullPath
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            type: 'POST',
            success: function(errors) {
                if(errors.length == 0){
                    Project.addFileToTree(newFileFullPath, elemType);
                    if(elemType == 'test'){
                        let tags = TestList.getDisplayedTestTags(elemFullPath);
                        TestList.displayTestTags(newFileFullPath, tags)
                    }
                    Main.Utils.toast('success', 'File was copied', 2000)
                }
                else{
                    Main.Utils.displayErrorModal(errors);
                }
            },
            error: function(){
                Main.Utils.toast('error', 'There was an error duplicating the file', 3000)
            }
        });
    }

    this.renameFilePrompt = function(elementDuplicateButton){
        let element =  $(elementDuplicateButton).parent().parent();
        let elemFullPath = element.attr('fullpath');
        let elemType = element.attr('type');
        let title = 'Rename file';
        let message = 'Enter a new name for this file...';
        let inputValue = elemFullPath;
        let placeholderValue = '';
        let callback = function(newFileFullPath){
            Project.renameFile(elemFullPath, elemType, element, newFileFullPath);
        }
        Main.Utils.displayPromptModal(title, message, inputValue, placeholderValue, callback)
    }

    this.renameFile = function(fullFilename, elemType, originalElement, newFullFilename){
        if(newFullFilename === fullFilename){
            // new file name is the same as original
            // don't show error message, do nothing
            return
        }

        newFullFilename =  newFullFilename.trim().replace(' ', '_');
        let errors = Main.Utils.validateFilename(newFullFilename);
        if(errors.length > 0){
            Main.Utils.displayErrorModal(errors);
            return
        }
        let endpointURL;
        if(elemType == 'test') { endpointURL = '/api/test/rename' }
        else if(elemType == 'page') { endpointURL = '/api/page/rename' }
        else { endpointURL = '/api/suite/rename' }

        $.ajax({
            url: endpointURL,
            data: JSON.stringify({
                "project": project,
                "fullFilename": fullFilename,
                "newFullFilename": newFullFilename
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            type: 'POST',
            success: function(result) {
                if(result.error.length == 0){
                    originalElement.remove();
                    Project.addFileToTree(newFullFilename, elemType);
                    if(elemType == 'test'){
                        let tagContainer = originalElement.find('.tag-container');
                        if(tagContainer.length > 0){
                            Project.getFileElement(newFullFilename).append(tagContainer);
                        }
                    }
                    Main.Utils.toast('success', 'File was renamed', 2000);
                }
                else{
                    Main.Utils.displayErrorModal([result.error])
                }
            },
            error: function(){
                Main.Utils.toast('error', 'There was an error duplicating the file', 4000)
            }
        });
    }

    this.getDirElement = function(dirPath){
        return $(`li.branch[fullpath="${dirPath}"]`)
    }

    this.dirExists = function(dirPath){
        return Project.getDirElement(dirPath).length > 0
    }

    this.getFileElement = function(filePath){
        return $(`li.tree-element[fullpath="${filePath}"]`)
    }
}