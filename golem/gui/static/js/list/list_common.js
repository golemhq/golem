
const FileExplorer = new function(){

    this.rootFolder;
    this.currentFolder;
    this.fileType;
    this.renderFinished = false;

    this.initialize = function(folder, fileType, container) {
        // bind this to the container element
        container.FileExplorer = this;

        this.fileType = fileType;
        this.rootFolder = new Folder(folder, null);
        this.navigateFromURL()
        // Hide bottom menu if user is read-only
        if(Global.user.projectWeight <= Main.PermissionWeightsEnum.readOnly){
            $("#bottomMenu").hide()
        }
        // Hide folder menus
        $('html').click(() => FileExplorer.hideAllFolderMenus())
    }

    this.navigateFromURL = function(){
        let pathname = window.location.pathname.split('/');
        if(pathname[0] == '') pathname.shift()
        if(pathname[pathname.length -1] == '') pathname.pop()
        pathname = pathname.slice(3);

        this.currentFolder = this.rootFolder;
        if(pathname.length){
            let _currentFolder = this.getFolder(pathname.join('.'));
            if(_currentFolder != null){ this.currentFolder = _currentFolder }
        }
        this.renderFolder(this.currentFolder);
    }

    this.navigateToFolder = function(folder){
        this.updateURL(folder);
        this.currentFolder = folder;
        this.renderFolder(folder)
    }

    this.renderFolder = function(folder){
        this.renderFinished = false;
        folder.render();
        this.renderFinished = true
    }

    this.updateURL = function(folder){
        let relpath = folder.folderpath().split('.').join('/');
        relpath = relpath.length ? `${relpath}/` : '';
        let pathName = `${this.baseURL()}${relpath}`;
        window.history.pushState({}, '', window.location.origin + pathName);
        window.onpopstate = () => { this.navigateFromURL() }
    }

    this.baseURL = function(){
        return `/project/${Global.project}/${this.fileType}s/`
    }

    this.getFolder = function(folderName, folder){
        folder = folder || this.rootFolder
        if(folderName == ''){
            return folder
        }
        let folderNameSplit = folderName.split('.');
        thisFolderName = folderNameSplit.shift();
        folderName = folderNameSplit.join('.')
        let childFolder = folder.getFolder(thisFolderName, folder);
        if(childFolder){
            if(folderName)
                return this.getFolder(folderName, childFolder)
            else
                return childFolder
        }
        else{
            return null
        }
    }

    this.getFile = function(filename){
        let filenameSplit = filename.split('.');
        filename = filenameSplit.pop();
        let folderName = filenameSplit.join('.');
        let folder = this.getFolder(folderName);
        if(folder)
            return folder.getFile(filename)
        else
            return null
    }

    this.addFile = function(folder){

        let callback = function(filename){
            if(filename.trim().length == 0) return
            if(folder.folderpath().length) filename = `${folder.folderpath()}.${filename}`
            $.ajax({
                url: Endpoints.createFile[FileExplorer.fileType],
                data: JSON.stringify({
                    "project": Global.project,
                    "fullPath": filename
                }),
                contentType: 'application/json;charset=utf-8',
                dataType: 'json',
                type: 'POST',
                success: function(data) {
                    if(data.errors.length == 0)
                        FileExplorer.rootFolder.addFile(filename)
                    else
                        Main.Utils.displayErrorModal(data.errors)
                },
                error: function(){
                    Main.Utils.toast('error', 'There was an error adding file', 4000)
                }
            })
        }
        Main.Utils.displayPromptModal('Add File', '', '', 'filename', callback)
    }

    this.renameFile = function(file){

        let callback = function(newFilepath){
            if(file.filepath() === newFilepath || newFilepath.trim().length == 0) return

            $.ajax({
                url: Endpoints.renameFile[FileExplorer.fileType],
                data: JSON.stringify({
                    "project": Global.project,
                    "fullFilename": file.filepath(),
                    "newFullFilename": newFilepath
                }),
                contentType: 'application/json;charset=utf-8',
                dataType: 'json',
                type: 'POST',
                success: function(result) {
                    if(result.errors.length == 0){
                        file.rename(newFilepath)
                        Main.Utils.toast('success', 'File was renamed', 2000);
                    }
                    else{
                        Main.Utils.displayErrorModal(result.errors)
                    }
                },
                error: function(){
                    Main.Utils.toast('error', 'There was an error renaming file', 4000)
                }
            })
        }
        Main.Utils.displayPromptModal('Rename file', 'Enter a new name for this file...',
            file.filepath(), 'new filename', callback)
    }

    this.duplicateFile = function(file){

        let callback = function(newFilepath){
            if(file.filepath() === newFilepath || newFilepath.trim().length == 0) return

            $.ajax({
                url: Endpoints.duplicateFile[FileExplorer.fileType],
                data: JSON.stringify({
                    "project": Global.project,
                    "fullPath": file.filepath(),
                    "newFileFullPath": newFilepath
                }),
                contentType: 'application/json;charset=utf-8',
                dataType: 'json',
                type: 'POST',
                success: function(errors) {
                    if(errors.length == 0){
                        FileExplorer.rootFolder.addFile(newFilepath)
                        if(FileExplorer.fileType == 'test'){
                            FileExplorer.getFile(newFilepath).addTags(file.tags)
                        }
                        Main.Utils.toast('success', 'File was copied', 2000);
                    }
                    else{
                        Main.Utils.displayErrorModal(errors)
                    }
                },
                error: function(){
                    Main.Utils.toast('error', 'There was an error duplicating file', 4000)
                }
            });
        }
        Main.Utils.displayPromptModal('Copy file', 'Enter a new file path...', file.filepath(), 'new filename', callback)
    }


    this.deleteFile = function(file){

        let callback = function(){
            $.ajax({
                url: Endpoints.deleteFile[FileExplorer.fileType],
                data: JSON.stringify({
                    "project": Global.project,
                    "fullPath": file.filepath()
                }),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                type: 'DELETE',
                success: function(errors) {
                    if(errors.length == 0){
                        file.parent.removeFile(file.name);
                        Main.Utils.toast('success', `File ${file.filepath()} was removed`, 2000)
                    }
                    else{
                        Main.Utils.toast('error', 'There was an error removing file', 4000)
                    }
                }
            })
        }
        let message = `<span style="word-break: break-all">Are you sure you want to delete <strong>${file.filepath()}</strong>?</span>`;
        Main.Utils.displayConfirmModal('Delete', message, callback);
    }


    this.addFolder = function(folder){

        let callback = function(folderName){
            if(folderName.trim().length == 0) return
            let fullpath = folderName;
            if(folder.folderpath().length) fullpath = `${folder.folderpath()}.${folderName}`

            $.ajax({
                url: Endpoints.createFolder[FileExplorer.fileType],
                data: JSON.stringify({
                    "project": Global.project,
                    "fullPath": fullpath
                }),
                contentType: 'application/json;charset=utf-8',
                dataType: 'json',
                type: 'POST',
                success: function(data) {
                    if(data.errors.length == 0){
                        folder.addFolder(folderName)
                    }
                    else{
                        Main.Utils.displayErrorModal(data.errors)
                    }
                },
                error: function() {
                    Main.Utils.toast('error', 'There was an error adding folder', 4000)
                }
            })
        }
        Main.Utils.displayPromptModal('Add Folder', '', '', 'folder name', callback)
    }

    this.renameFolder = function(folder){

        let callback = function(newFolderName){
            if(newFolderName.trim().length == 0) return
            $.ajax({
                url: Endpoints.renameFolder[FileExplorer.fileType],
                data: JSON.stringify({
                    "project": Global.project,
                    "fullDirname": folder.folderpath(),
                    "newFullDirname": newFolderName
                }),
                contentType: 'application/json;charset=utf-8',
                dataType: 'json',
                type: 'POST',
                success: function(data) {
                    if(data.errors.length == 0){
                        folder.rename(newFolderName)
                    }
                    else{
                        Main.Utils.displayErrorModal(data.errors);
                    }
                },
                error: function() {
                    Main.Utils.toast('error', 'There was an error renaming folder', 4000)
                }
            });
        }
        Main.Utils.displayPromptModal('Rename Folder', 'Enter a new name for this folder...', folder.folderpath(), '', callback)
    }

    this.deleteFolder = function(folder){

        let callback = function(){
            $.ajax({
                url: Endpoints.deleteFolder[FileExplorer.fileType],
                data: JSON.stringify({
                    "project": Global.project,
                    "fullDirname": folder.folderpath(),
                }),
                contentType: 'application/json;charset=utf-8',
                dataType: 'json',
                type: 'DELETE',
                success: function(data) {
                    if(data.errors.length == 0){
                        FileExplorer.renderFinished = false;
                        folder.parent.removeFolder(folder.name);
                        FileExplorer.renderFinished = true;
                    }
                    else{
                        Main.Utils.displayErrorModal(data.errors);
                    }
                },
                error: function() {
                    Main.Utils.toast('error', 'There was an error deleting folder', 4000)
                }
            });
        }
        let message = `<span style="">
            Are you sure you want to delete folder <strong>${folder.folderpath()}</strong> and all its contents?.
            <strong>This cannot be undone.</strong></span>`;
        Main.Utils.displayConfirmModal('Delete Folder', message, callback, true);
    }

    this.getBreadCrumb = function(folder, breadcrumb){
        if(breadcrumb === undefined){
            breadcrumb = $(`<div><span>${folder.name}</span> /</div>`)
        }
        else{
            let anchor = $(`<a href="javascript:void(0);">${folder.name}</a>`);
            anchor.on('click', () => this.navigateToFolder(folder) );
            breadcrumb.prepend(anchor, ' / ');
        }
        if(folder.parent != null){
            breadcrumb = this.getBreadCrumb(folder.parent, breadcrumb)
        }
        return breadcrumb
    }

    this.hideAllFolderMenus = function(){
        $(".folder-menu").removeClass('active')
    }
}


class Folder {

    constructor(folder, parent) {
        this.name = folder.name;
        this.parent = parent;
        this.folders = [];
        this.files = [];
        this.dom = null;
        this.container = null;

        let folders = folder.sub_elements.filter(element => element.type == 'directory');
        let files = folder.sub_elements.filter(element => element.type == 'file');
        for(let folder of folders){
            this.folders.push(new Folder(folder, this))
        }
        for(let file of files){
            this.files.push(new File(file, this))
        }
    }

    path(){
        return this.parent == null ? '' : this.parent.folderpath()
    }

    folderpath(){
        if(this.parent == null)
            return ''
        if(this.parent.parent == null)
            return this.name
        return `${this.path()}.${this.name}`
    }

    generateDOM(){
        let thisFolder = this;
        let ul = $("<ul class='folder-content'>");
        this.folders.forEach(folder => ul.append(folder.template()))
        this.files.forEach(file => ul.append(file.template()))
        this.dom = ul
    }

    template(){
        let thisFolder = this;
        let openedClass = 'glyphicon-folder-open';
        let closedClass = 'glyphicon-folder-close';
        let folderLi = $(`
            <li class="tree-element folder" name="${thisFolder.name}">
                <i class="folder-icon glyphicon ${closedClass}"></i>
                <a href="#">${thisFolder.name}</a>
                <span class="dropdown-container"></span>
                <ul class='folder-content'></ul>
            </li>`);
        let dropdownToggle = thisFolder.folderMenuTemplate();
        folderLi.find(".dropdown-container").append(dropdownToggle);
        // Expand/collapse folder icon
        folderLi.find('.folder-icon')[0].addEventListener('click', function(){
            let ul = folderLi.find("ul.folder-content:first");
            if(this.classList.contains('glyphicon-folder-close')){
                this.classList.remove('glyphicon-folder-close');
                this.classList.add('glyphicon-folder-open');
                thisFolder.generateDOM();
                thisFolder.container = ul;
                ul.html(thisFolder.dom.children());
                ul.show()
            }
            else{
                this.classList.add('glyphicon-folder-close');
                this.classList.remove('glyphicon-folder-open');
                ul.hide()
            }
        })
        // Navigate to folder link
        folderLi.find('>a').each(function () {
            $(this).on('click', function (e) {
                FileExplorer.navigateToFolder(thisFolder)
                e.preventDefault();
            })
        })
        return folderLi
    }

    folderMenuTemplate(){
        let folder = this;
        let userWeight = Global.user.projectWeight;
        let weights = Main.PermissionWeightsEnum;
        let dropdownMenu;
        if(userWeight >= weights.standard){
            dropdownMenu = $(`<ul class="dropdown-menu folder-menu"></ul>`);
            // New File menu
            let newFileMenu = $(`<a href="javascript:void(0);">Add New File</a>`);
            newFileMenu.on('click', () => FileExplorer.addFile(folder))
            dropdownMenu.append($(`<li></li>`).append(newFileMenu));
            // New Folder menu
            let newFolderMenu = $(`<a href="javascript:void(0);">Add New Folder</a>`);
            newFolderMenu.on('click', () => FileExplorer.addFolder(folder))
            dropdownMenu.append($(`<li></li>`).append(newFolderMenu));
            // Rename Folder menu
            let renameFolderMenu = $(`<a href="javascript:void(0);">Rename Folder</a>`);
            renameFolderMenu.on('click', () => FileExplorer.renameFolder(folder))
            dropdownMenu.append($(`<li></li>`).append(renameFolderMenu));
            if(userWeight >= weights.admin){
                // Delete Folder menu
                let deleteFolderMenu = $(`<a href="javascript:void(0);">Delete Folder</a>`);
                deleteFolderMenu.on('click', () => FileExplorer.deleteFolder(folder))
                dropdownMenu.append($(`<li></li>`).append(deleteFolderMenu));
            }
        }
        else{
            dropdownMenu = '';
        }
        $("body").append(dropdownMenu);

        let dropdownToggle = $(`<button class="btn btn-default dropdown-toggle folder-menu-button-toggle" type="button"><span class="caret"></span></button>`);
        dropdownToggle.on('click', function(e){
            let isActive = dropdownMenu.hasClass('active');
            FileExplorer.hideAllFolderMenus();
            dropdownMenu.css('top', dropdownToggle.offset().top + 17);
            dropdownMenu.css('left', dropdownToggle.offset().left)
            if(!isActive){ dropdownMenu.addClass('active') }
            return false
        });
        return dropdownToggle
    }

    render(){
        // Update breadcrumb
        let breadCrumb = FileExplorer.getBreadCrumb(this);
        $("#breadcrumb").html(breadCrumb);
        // Update root folder content
        this.generateDOM()
        this.container = $("#rootFolderContent");
        this.container.html(this.dom.children());
        // Update bottom menu
        $("#bottomMenu").html(this.bottomNewElementButtons())
    }

    getFile(fileName){
        for (let file of this.files) {
          if(file.name == fileName) return file
        }
        return null
    }

    getFolder(folderName){
        for (let _folder of this.folders) {
            if(_folder.name == folderName) return _folder
        }
        return null
    }

    addFolder(folderName, folderObj){
        let folderNameArray = folderName.split('.');
        if(folderNameArray.length > 1){
            let childFolderName = folderNameArray.shift();
            let childFolder = this.getFolder(childFolderName, folderObj);
            if(childFolder){
                return childFolder.addFolder(folderNameArray.join('.'), folderObj)
            }
            else{
                return this.addFolder(childFolderName).addFolder(folderNameArray.join('.'), folderObj)
            }
        }
        else{
            if(folderObj === undefined){
                let tempFolder = {
                    "dot_path": "",
                    "name": folderName,
                    "sub_elements": [],
                    "type": "directory"
                }
                folderObj = new Folder(tempFolder, this);
            }
            else if(folderObj.parent === null){
                folderObj.parent = this
            }
            this.folders.push(folderObj);
            this._addFolderToUI(folderObj)
            return folderObj
        }
    }

    _addFolderToUI(newFolder){
        if(this.container != null){
            let folderLi = this.container.find('>li.folder')
            if(folderLi.length > 0){
                folderLi.last().after(newFolder.template())
            }
            else{
                this.container.prepend(newFolder.template())
            }
        }
    }

    removeFolder(folderName){
        if(this.getFolder(folderName)){
            this.folders = this.folders.filter((value, index, arr) => value.name != folderName);
            let folderLi = this.container.find(`>li.folder[name="${folderName}"]`);
            if(folderLi.length > 0){ folderLi.remove() }
        }
    }

    rename(newFolderpath){
        let newFolderpathArray = newFolderpath.split('.');
        let newFoldername = newFolderpathArray.pop();
        let newPath = newFolderpathArray.join('.');

        if(this.path() == newPath){
            this.parent.renameFolder(this, newFoldername)
        }
        else{
            this.parent.removeFolder(this.name)
            this.name = newFoldername;
            this.parent = null;
            FileExplorer.rootFolder.addFolder(newFolderpath, this)
        }

    }

    renameFolder(childFolder, newName){
        let childFolderLi = this.container.find(`>li.folder[name='${childFolder.name}']`);
        childFolder.name = newName;
        childFolderLi.attr('name', newName);
        childFolderLi.find('>a').html(newName)
    }

    addFile(filename, fileObj){
        let filenameArray = filename.split('.');
        if(filenameArray.length > 1){
            let childFolderName = filenameArray.shift();
            let childFolder = this.getFolder(childFolderName);
            if(childFolder){
                childFolder.addFile(filenameArray.join('.'))
            }
            else{
                this.addFolder(childFolderName).addFile(filenameArray.join('.'), fileObj)
            }
        }
        else{
            if(fileObj === undefined){
                let tempFile = {
                    "dot_path": "",
                    "name": filename,
                    "sub_elements": [],
                    "type": "file"
                }
                fileObj = new File(tempFile, this);
            }
            this.files.push(fileObj);
            this._addFileToUI(fileObj)
        }
    }

    _addFileToUI(file){
        if(this.container != null){
            this.container.append(file.template())
        }
    }

    removeFile(filename){
        if(this.getFile(filename)){
            this.files = this.files.filter((value, index, arr) => value.name != filename);
            let fileLi = this.container.find(">li.file")
                .filter(function(i){ return $(this).find('a.file-link').text() === filename });
            if(fileLi.length > 0){ fileLi.remove() }
        }
    }

    bottomNewElementButtons(){
        let folder = this;
        let newFileButton = $(`<a class="new-file-link" href="javascript:void(0)">
                <i class="glyphicon glyphicon-file"><i style="left: -3px" class="fa fa-plus-circle fa-stack-1x awesomeEntity sub-icon"/></i>
            </a>`);
        newFileButton.on('click', function(){
            FileExplorer.addFile(folder)
        })
        let newFolderButton = $(`<a class="new-directory-link" href="javascript:void(0)">
                <i class="glyphicon glyphicon-folder-close"><i style="left: 0px" class="fa fa-plus-circle fa-stack-1x awesomeEntity sub-icon"/></i>
            </a>`);
        newFolderButton.on('click', function(){
            FileExplorer.addFolder(folder)
        })
        return $().add(newFileButton).add(newFolderButton)
    }
}


class File {

    constructor(file, parent) {
        this.name = file.name;
        this.parent = parent;
        this.tags = [];
        this.dom = null
    }

    path(){ return this.parent.folderpath()}

    filepath(){
        return this.path().length > 0 ? `${this.path()}.${this.name}` : this.name
    }

    template(){
        let thisFile = this;
        let buttonsSpan = $('<span class="file-menu pull-right"></span');

        let userWeight = Global.user.projectWeight;
        let weights = Main.PermissionWeightsEnum;

        if(userWeight >= weights.standard){
            // Rename button
            let renameButton = $(`<button class="file-menu-button rename-button"><i class="glyphicon glyphicon-edit"></i></button>`);
            renameButton.on('click', e => FileExplorer.renameFile(thisFile))
            buttonsSpan.append(renameButton);
            // Duplicate button
            let duplicateButton = $(`<button class="file-menu-button duplicate-button"><i class="glyphicon glyphicon-duplicate"></i></button>`);
            duplicateButton.on('click', e => FileExplorer.duplicateFile(thisFile));
            buttonsSpan.append(duplicateButton);
            if(userWeight >= weights.admin){
                // Delete button
                let deleteButton = $(`<button class="file-menu-button delete-button"><i class="glyphicon glyphicon-trash"></i></button>`);
                deleteButton.on('click', e => FileExplorer.deleteFile(thisFile));
                buttonsSpan.append(deleteButton);
            }
        }
        if(FileExplorer.fileType == 'test' || FileExplorer.fileType == 'page'){
            // Code View button
            let codeIcon = `<i class="glyphicon glyphicon-chevron-left" style="-webkit-text-stroke: 0.5px white;"></i><i class="glyphicon glyphicon-chevron-right" style="margin-left: -8px; -webkit-text-stroke: 0.5px white;"></i>`;
            let codeLink = $(`<a href="${this.url()}code" class="file-menu-button code-button" style="margin-right: -3px; margin-left:-3px">${codeIcon}</a>`);
            buttonsSpan.prepend(codeLink);
            if(userWeight >= weights.standard && FileExplorer.fileType == 'test'){
                // Run test button
                let runButton = $(`<button class="file-menu-button run-test-button"><i class="glyphicon glyphicon-play-circle"></i></button>`);
                runButton.on('click', e => Main.TestRunner.openConfigModal(Global.project, thisFile.filepath()));
                buttonsSpan.prepend(runButton);
            }
        }
        let li = $(`
            <li class="tree-element file">
                <a class="file-link" href="${this.url()}">${this.name}</a>
                <div class="tag-container"></div>
            </li>`);
        li.append(buttonsSpan);

        this.dom = li;
        this.displayTags();
        return li
    }

    rename(newFilepath){
        let newFilepathArray = newFilepath.split('.');
        let newFilename = newFilepathArray.pop();
        if(this.path() == newFilepathArray.join('.')){
            this.name = newFilename;
            this.dom.find('>a').html(newFilename)
        }
        else{
            this.parent.removeFile(this.name);
            FileExplorer.rootFolder.addFile(newFilepath, this)
        }
    }

    url(){
        return `/project/${Global.project}/${FileExplorer.fileType}/${this.filepath()}/`
    }

    addTags(tags){
        this.tags = tags;
        this.displayTags()
    }

    displayTags(){
        if(this.dom){
            let tagContainer = this.dom.find(".tag-container");
            this.tags.forEach(function(tag){
                let tagElement = $(`<span class="tag">${tag}</span>`);
                tagContainer.append(tagElement)
            })
        }
    }
}


const Endpoints = {
    createFile: {
        test: '/api/project/test',
        page: '/api/project/page',
        suite: '/api/project/suite'
    },
    renameFile: {
        test: '/api/test/rename',
        page: '/api/page/rename',
        suite: '/api/suite/rename'
    },
    duplicateFile: {
        test: '/api/test/duplicate',
        page: '/api/page/duplicate',
        suite: '/api/suite/duplicate'
    },
    deleteFile: {
        test: '/api/test/delete',
        page: '/api/page/delete',
        suite: '/api/suite/delete'
    },
    createFolder: {
        test: '/api/project/test/directory',
        page: '/api/project/page/directory',
        suite: '/api/project/suite/directory'
    },
    renameFolder: {
        test: '/api/test/directory/rename',
        page: '/api/page/directory/rename',
        suite: '/api/suite/directory/rename'
    },
    deleteFolder: {
        test: '/api/test/directory/delete',
        page: '/api/page/directory/delete',
        suite: '/api/suite/directory/delete'
    }
}