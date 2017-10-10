
var Project = new function(){

    this.generateNewElement = function(element){
        var li = "\
            <li class='tree-element' fullpath='"+element.dotPath+"' name='"+element.name+"' type='"+element.type+"'>\
                <a href='"+element.url+"'>"+element.name+"</a> \
                <span class='pull-right tree-element-buttons'> \
                    <button onclick='duplicateElementPrompt(this)'><i class='glyphicon glyphicon-copy'></i></button> \
                    <button onclick='deleteElementConfirm(this)'><i class='glyphicon glyphicon-remove'></i></button> \
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
                    onblur='addElement(event);' onkeyup='if(event.keyCode==13){addElement(event)}'>\
            </span>\
            <span class='display-new-element-link'>\
                <a class='new-element-link' href='javascript:void(0)' onclick='displayNewElementForm(this)'><i class='glyphicon glyphicon-plus-sign'></i> Add</a>\
            </span>\
        </li>";
        return li
    }
}