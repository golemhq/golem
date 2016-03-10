
$(document).ready(function() {

    $('#testCasesTree').treed();

    $('#pagesTree').treed();

});


function startAddNewTestCase(elem){
    var parent = $(elem).parent();
    var input = $("<input class='new-test-case-input' type='text'>");
    $(input).blur(function() {
        //alert('blur')
        addNewTestCase($(this))
    });

    $(input).keyup(function(e) {
        if (e.which == 13) // Enter key
            //alert('keyup')
        addNewTestCase($(this));
    });

    parent.html('');
    parent.append(input);
    input.focus();
}


function addNewTestCase(input){
    var dottedBranches = getDottedBranches(input);
    var testCaseName = input.val();
    if(testCaseName.length == 0){
        return
    }
    // validate spaces
    if(testCaseName.indexOf(' ') > -1){
        displayErrorModal(['Spaces are not allowed']);
        return
    }
    // validate length
    if(testCaseName.length > 40){
        displayErrorModal(['Maximum length is 40 characters']);
        return
    }
    // validate there is no more than 1 slash
    if(testCaseName.split('/').length -1 > 1){
        displayErrorModal(['Only one slash character is allowed']);
        return   
    }
    // validate if there is a slash it is trailing
    if(testCaseName.split('/').length -1 == 1){
        if(testCaseName.indexOf('/') != 0){
            displayErrorModal(['Directories should have a trailing slash character']);
            return
        }
    }
    if(testCaseName.indexOf('/') > -1){
        // is a new directory
        $.ajax({
            url: "/new_directory_test_case/",
            data: {
                "project": project,
                "parents": dottedBranches,
                "directoryName": testCaseName
            },
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                if(data.errors.length == 0){
                    var li = $(".new-test-case-input").parent();
                    var ul = $(".new-test-case-input").parent().parent();
                    addBranchToTree(li, data.directory_name, 'test_case');

                    ul.append(
                        "<li><i class='glyphicon glyphicon-plus-sign'></i><a href='#' \
                            onclick='startAddNewTestCase(this)'> Add New</a></li>");
                }
                else{
                    displayErrorModal(data.errors);
                }
            },
            error: function() {}
        });
    }
    else {
        $.ajax({
            url: "/nuevo_test_case/",
            data: {
                "project": project,
                "parents": dottedBranches,
                "testCaseName": testCaseName
            },
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                if(data.errors.length == 0){
                    var li = $(".new-test-case-input").parent();
                    var ul = $(".new-test-case-input").parent().parent();
                    if(dottedBranches.length > 0){
                        var urlForTC = dottedBranches+'.'+testCaseName;
                    }
                    else{
                        var urlForTC = testCaseName;
                    }
                    li.html(
                        "<a href='/p/"+data.project_name+"/tc/"+urlForTC+"/'>"+data.tc_name+"</a>");
                    ul.append(
                        "<li><i class='glyphicon glyphicon-plus-sign'></i><a href='#' \
                            onclick='startAddNewTestCase(this)'> Add New</a></li>");
                }
                else{
                    displayErrorModal(data.errors);
                }
            },
            error: function() {               
            }
        });

    }
}






function startAddNewPageObject(elem){
    var parent = $(elem).parent();
    console.log(parent);
    var input = $("<input class='new-page-object-input' type='text'>");
    $(input).blur(function() {
        //alert('blur')
        addNewPageObject($(this))
    });

    $(input).keyup(function(e) {
        if (e.which == 13) // Enter key
            //alert('keyup')
        addNewPageObject($(this));
    });

    parent.html('');
    parent.append(input);
    input.focus();
}


function addNewPageObject(input){
    var dottedBranches = getDottedBranches(input);
    var pageObjectName = input.val();
    if(pageObjectName.length == 0){
        return
    }
    // validate spaces
    if(pageObjectName.indexOf(' ') > -1){
        displayErrorModal(['Spaces are not allowed']);
        return
    }
    // validate length
    if(pageObjectName.length > 40){
        displayErrorModal(['Maximum length is 40 characters']);
        return
    }
    // validate there is no more than 1 slash
    if(pageObjectName.split('/').length -1 > 1){
        displayErrorModal(['Only one slash character is allowed']);
        return   
    }
    // validate if there is a slash it is trailing
    if(pageObjectName.split('/').length -1 == 1){
        if(pageObjectName.indexOf('/') != 0){
            displayErrorModal(['Directories should have a trailing slash character']);
            return
        }
    }
    if(pageObjectName.indexOf('/') > -1){
        // is a new directory
        $.ajax({
            url: "/new_directory_page_object/",
            data: {
                "project": project,
                "parents": dottedBranches,
                "directoryName": pageObjectName
            },
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                if(data.errors.length == 0){
                    var li = $(".new-page-object-input").parent();
                    var ul = $(".new-page-object-input").parent().parent();
                    addBranchToTree(li, data.directory_name, 'page_object');
                    ul.append(
                        "<li><i class='glyphicon glyphicon-plus-sign'></i><a href='#' \
                            onclick='startAddNewPageObject(this)'> Add New</a></li>");
                }
                else{
                    displayErrorModal(data.errors);
                }
            },
            error: function() {}
        });
    }
    else {
        $.ajax({
            url: "/new_page_object/",
            data: {
                "project": project,
                "parents": dottedBranches,
                "pageObjectName": pageObjectName
            },
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                if(data.errors.length == 0){
                    var li = $(".new-page-object-input").parent();
                    var ul = $(".new-page-object-input").parent().parent();
                    if(dottedBranches.length > 0){
                        var urlForPO = dottedBranches+'.'+pageObjectName;
                    }
                    else{
                        var urlForPO = pageObjectName;
                    }
                    li.html("<a href='/p/"+data.project_name+"/page/"+urlForPO+"/'>"+data.page_object_name+"</a>");
                    ul.append(
                        "<li><i class='glyphicon glyphicon-plus-sign'></i><a href='#' \
                            onclick='startAddNewPageObject(this)'> Add New</a></li>");
                }
                else{
                    displayErrorModal(data.errors);
                }

            },
            error: function() {
                
            }
        });

    }
}


function getDottedBranches(elem){
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


function displayErrorModal(errors){
    var ulContent = '';
    for(e in errors){
        ulContent += "<li>"+errors[e]+"</li>";
    } 
    $("#errorList").html(ulContent);
    $("#errorModal").modal("show");
    $("#errorModal .dismiss-modal").focus();
}