
$(document).ready(function() {
    $('#testCasesTree').treed();
    $('#pagesTree').treed();
});


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
    var inputClass = '';
    if(input.hasClass('new-test-case')){
        elementType = 'test_case';
        urlPrefixForElementType = 'test';
        inputClass = 'new-test-case';
    }
    else if(input.hasClass('new-page-object')){
        elementType = 'page_object';
        urlPrefixForElementType = 'page';
        inputClass = 'new-page-object';
    }
    else if(input.hasClass('new-suite')){
        elementType = 'suite';
        urlPrefixForElementType = 'suite';
        inputClass = 'new-suite';
    }

    var parentsSeparetedByDots = getParentsSeparatedByDots(input);
    var elementName = input.val().trim();
    var isDir = false;
    if(elementName.indexOf('/') > -1){
        isDir = true;
    }

    if(elementName.length == 0){
        input.val('');
        input.parent().hide();
        input.parent().parent().find(".display-new-element-link").show();
        return
    }
    // validate spaces
    if(elementName.indexOf(' ') > -1){
        displayErrorModal(['Spaces are not allowed']);
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
            "parents": parentsSeparetedByDots,
            "elementName": elementName
        },
        dataType: 'json',
        type: 'POST',
        success: function(data) {
            if(data.errors.length == 0){

                // add new li for the element
                var lastLi = input.parent().parent().parent().find("li").last();
                lastLi.before("<li class='tree-element'></li>");
                var newLi = lastLi.prev();

                if(data.is_dir){
                    //var li = input.parent().parent();
                    addBranchToTree(newLi, data.element_name, inputClass);

                    // input.parent().hide();
                    // input.parent().parent().find(".display-new-element-link").show();
                }
                else{
                    if(parentsSeparetedByDots.length > 0){
                        var urlForTeseCase = parentsSeparetedByDots + '.' + data.element_name;
                    }
                    else{
                        var urlForTeseCase = data.element_name;
                    }
                    newLi.html("<a href='/p/"+data.project_name+"/"+urlPrefixForElementType+"/"+urlForTeseCase+"/'>"+data.element_name+"</a> \
                                <span class='pull-right tree-element-buttons'> \
                                    <button><i class='glyphicon glyphicon-edit'></i></button> \
                                    <button><i class='glyphicon glyphicon-copy'></i></button> \
                                    <button><i class='glyphicon glyphicon-remove'></i></button> \
                                </span>");
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






// function startAddNewPageObject(elem){
//     var parent = $(elem).parent();
//     console.log(parent);
//     var input = $("<input class='new-page-object-input' type='text'>");
//     $(input).blur(function() {
//         //alert('blur')
//         addNewPageObject($(this))
//     });

//     $(input).keyup(function(e) {
//         if (e.which == 13) // Enter key
//             //alert('keyup')
//         addNewPageObject($(this));
//     });

//     parent.html('');
//     parent.append(input);
//     input.focus();
// }


// function addNewPageObject(input){
//     var dottedBranches = getDottedBranches(input);
//     var pageObjectName = input.val();
//     if(pageObjectName.length == 0){
//         console.log(input);
//         input.get(0).parentElement.remove();
//         return
//     }
//     // validate spaces
//     if(pageObjectName.indexOf(' ') > -1){
//         displayErrorModal(['Spaces are not allowed']);
//         return
//     }
//     // validate length
//     if(pageObjectName.length > 60){
//         displayErrorModal(['Maximum length is 60 characters']);
//         return
//     }
//     // validate there is no more than 1 slash
//     if(pageObjectName.split('/').length -1 > 1){
//         displayErrorModal(['Only one slash character is allowed']);
//         return   
//     }
//     // validate if there is a slash it is trailing
//     if(pageObjectName.split('/').length -1 == 1){
//         if(pageObjectName.indexOf('/') != 0){
//             displayErrorModal(['Directories should have a trailing slash character']);
//             return
//         }
//     }
//     if(pageObjectName.indexOf('/') > -1){
//         // is a new directory
//         $.ajax({
//             url: "/new_directory_page_object/",
//             data: {
//                 "project": project,
//                 "parents": dottedBranches,
//                 "directoryName": pageObjectName
//             },
//             dataType: 'json',
//             type: 'POST',
//             success: function(data) {
//                 if(data.errors.length == 0){
//                     var li = $(".new-page-object-input").parent();
//                     var ul = $(".new-page-object-input").parent().parent();
//                     addBranchToTree(li, data.directory_name, 'page_object');
//                     ul.append(
//                         "<li><i class='glyphicon glyphicon-plus-sign'></i><a href='#' \
//                             onclick='startAddNewPageObject(this)'> Add New</a></li>");
//                 }
//                 else{
//                     displayErrorModal(data.errors);
//                 }
//             },
//             error: function() {}
//         });
//     }
//     else {
//         $.ajax({
//             url: "/new_page_object/",
//             data: {
//                 "project": project,
//                 "parents": dottedBranches,
//                 "pageObjectName": pageObjectName
//             },
//             dataType: 'json',
//             type: 'POST',
//             success: function(data) {
//                 if(data.errors.length == 0){
//                     var li = $(".new-page-object-input").parent();
//                     var ul = $(".new-page-object-input").parent().parent();
//                     if(dottedBranches.length > 0){
//                         var urlForPO = dottedBranches+'.'+pageObjectName;
//                     }
//                     else{
//                         var urlForPO = pageObjectName;
//                     }
//                     li.html("<a href='/p/"+data.project_name+"/page/"+urlForPO+"/'>"+data.page_object_name+"</a>");
//                     ul.append(
//                         "<li><i class='glyphicon glyphicon-plus-sign'></i><a href='#' \
//                             onclick='startAddNewPageObject(this)'> Add New</a></li>");
//                 }
//                 else{
//                     displayErrorModal(data.errors);
//                 }

//             },
//             error: function() {
                
//             }
//         });

//     }
// }


function getParentsSeparatedByDots(elem){
    var dotted_branches = '';
    elem.parents('.branch').each(function(){
        if(dotted_branches.length == 0){
            dotted_branches = $(this).find('a').html();    
        }
        else {
            dotted_branches = $(this).find('a').html() + '.' + dotted_branches;
        }
    });
    return dotted_branches
}


function removeTreeElement(elem){
    console.log(elem);
    var parent = $(elem).parent().parent();
    console.log(parent)
}

