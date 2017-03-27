
$(document).ready(function() {
    $('#testCasesTree').treed();

    $("#allTestCasesCheckbox").change(function(){
        checkAllTestCases($("#suiteTests ul"), this.checked);
    });

    $(".select-testcase-checkbox").change(function(){
        // is this a branch?
        var li = $(this).parent();
        if( li.hasClass('branch') ){
            checkAllTestCases(li.find('ul').first(), this.checked)
        }
    });


    // check the selected tests cases
    checkSelectedTests(selectedTests);


    // if a test is unchecked, all parent and grandparent branches must be unchecked too
    $(".select-testcase-checkbox").change(function(){
        if( !this.checked ){
            uncheckParentAndGrandParents($(this));
            // uncheck the root checkbox 
            $("#allTestCasesCheckbox").prop('checked', false);
        }
    });
});



function checkAllTestCases(elem, isChecked){
    elem.find("input").each(function(){
        $(this).prop('checked', isChecked);
    });
}


function checkSelectedTests(selectedTests){
    for(t in selectedTests){
        var splitTest = selectedTests[t].split('.');
        var rootUl = $("#testCasesTree");
        checkTest(rootUl, splitTest);
    }
}


function checkTest(rootUl, testPath){
    if(testPath.length == 1){
        // the test is in this level
        rootUl.children('li').find('label>.node-name').each(function(){
            if($(this).html() == testPath[0]){
                $(this).siblings('input').prop('checked', true);
                return
            }
        });
        //alert('There was an error loading test case list');
    }
    else if(testPath.length > 1){
        var branchName = testPath.shift();
        // find branch
        rootUl.children('li.branch').find('a.branch-name').each(function(){
            if($(this).html() == branchName){
                var newUl = $(this).parent().children('ul');
                checkTest(newUl, testPath);
                return
            }
        });
        //alert('There was an error loading test case list');
    }
}


function uncheckParentAndGrandParents(elem){
    var parents = elem.parents();
    parents.each(function(){
        // check if parent is li.branch
        if($(this).hasClass('branch')){
            // this is a branch, uncheck it
            $(this).children('input').prop('checked', false);
    }
    });
}


function saveTestSuite(){
    var browsers = [];
    if($("#browsers").val().length > 0){
        $($("#browsers").val().split(',')).each(function(){
            browsers.push(this.trim());
        });
    }

    var workers = $("#workers").val();
    var testCases = getAllCheckedTests();
    $.ajax({
        url: "/save_suite/",
        data: JSON.stringify({
                "project": project,
                "suite": suite,
                "browsers": browsers,
                "workers": workers,
                "testCases": testCases
            }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        success: function(data) {
            toastr.options = {
                "positionClass": "toast-top-center",
                "timeOut": "3000",
                "hideDuration": "100"}
            toastr.success("Suite "+suite+" saved");
        },
        error: function() {
        }
    });
}


function getAllCheckedTests(){
    var testCaseList = [];
    if($("#allTestCasesCheckbox").prop('checked')){
        testCaseList.push('*');
    }
    else{
        var rootUl = $("#testCasesTree");
        testCasesList = getAllCheckedTestsInALevel(rootUl, testCaseList);
    }
    return testCaseList
}

function getAllCheckedTestsInALevel(rootUl, testCaseList){
    var lis = rootUl.children('li');
    lis.each(function(){
        var thisLi = $(this);
        if(thisLi.hasClass('branch')){
            var thisBranchInput = thisLi.children('input');
            var thisBranchName = thisLi.children('a.branch-name').html();
            // is this branch checked?
            if(thisBranchInput.prop('checked')){
                var nodeWithFullPath = getNodeFullPath(thisLi, thisBranchName);
                testCaseList.push(nodeWithFullPath + '/');
            }
            else{
                var newRootUl = thisLi.children('ul');
                testCaseList = getAllCheckedTestsInALevel(newRootUl, testCaseList);
            }
        }
        else{
            var thisLiName = thisLi.find('span.node-name').html();
            var thisLiInput = thisLi.find('input');
            if(thisLiInput.prop('checked')){
                var nodeWithFullPath = getNodeFullPath(thisLi, thisLiName);
                testCaseList.push(nodeWithFullPath);
            }
        }
    });
    return testCaseList
}

function getNodeFullPath(thisLi, nodeName){
    var fullPath = [nodeName];
    var parents = thisLi.parents();
    parents.each(function(){
        // check if parent is li.branch
        if($(this).hasClass('branch')){
            console.log($(this));
            fullPath.splice(0, 0, $(this).children('a.branch-name').html());
        }
    });
    if(fullPath.length > 1){
        return fullPath.join('.')
    }
    else{
        return nodeName
    }
}

