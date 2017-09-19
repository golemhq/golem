


$(document).ready(function() {

    $('#testCasesTree').treed();

    $("#allTestCasesCheckbox").change(function(){
        checkUncheckAllTestCases(this.checked);
    });

    // check the selected tests cases
    checkSelectedTests(selectedTests);

    // if a test is unchecked, all parent and grandparent branches must be unchecked too
    // if a test is checked, and all it's siblings are checked, the parent must be checked
    $(".select-testcase-checkbox").change(function(){
        if( this.checked ){
            // a checkbox was checked, check if this level and n parent
            // levels must be checked as well
            verifyIfAllCheckboxesAreCheckedInLevelAndCheckParent(
                $(this).closest('ul').parent());
        }
        else{
            // a checkbox was unhecked
            uncheckParentAndGrandParents($(this));
            // uncheck the root checkbox 
            $("#allTestCasesCheckbox").prop('checked', false);
        }

        // is this a branch?
        var li = $(this).parent();
        if( li.hasClass('branch') ){
            checkBranchTestCases(li, this.checked)
        }
    });


    $.ajax({
        url: "/get_supported_browsers/",
        data: {},
        dataType: 'json',
        type: 'POST',
        success: function(browserSuggestions) {
            startBrowsersAutocomplete(browserSuggestions);
        },
        error: function() {
        }
    });

});


function checkSelectedTests(selectedTests){
    // if '*' is in selectedTests, check all test cases regardless
    if(selectedTests.indexOf('*') > -1){
        checkUncheckAllTestCases(true);
    }
    else{
        for(t in selectedTests){
            var splitTest = selectedTests[t].split('.');
            var isDir = false;
            var lastChar = splitTest[splitTest.length-1].substr(-1);
            if (lastChar == '/') {
                branchLi = findBranchAndCheckDescendents(splitTest, $("#testCasesTree"));

            }
            else{
                var rootUl = $("#testCasesTree");
                checkTest(rootUl, splitTest);
            }
        }
    }
}


function checkUncheckAllTestCases(isChecked){
    $("#allTestCasesCheckbox").prop('checked', isChecked);
    $(".select-testcase-checkbox").each(function(){
        $(this).prop('checked', isChecked);
    });
}


function checkTest(rootUl, testPath){
    if(testPath.length == 1){
        // the test is in this level
        rootUl.children('li').find('label>.node-name').each(function(){
            if($(this).html() == testPath[0]){
                $(this).siblings('input').prop('checked', true);
                verifyIfAllCheckboxesAreCheckedInLevelAndCheckParent(
                    $(this).closest('ul').parent());
                return
            }
        });
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
    }
}


function checkBranchTestCases(branch, isChecked){
    branch.find($(".select-testcase-checkbox")).each(function(){
        $(this).prop('checked', isChecked);
    });

}


var findBranchAndCheckDescendents = function(testPath, rootUl){
    if(testPath.length == 1){
        // the branch is in this level
        rootUl.find('>li.branch').each(function(){
            if($(this).find('>a').html()+'/' == testPath[0]){
                console.log('returning this', $(this).find('>ul'));
                var branchUl = $(this).find('>ul');
                $(this).find('>input').prop('checked', true);
                checkBranchTestCases(branchUl, true);
            }
        });
    }
    else if(testPath.length > 1){
        var branchName = testPath.shift();
        // find branch
        var newUl;
        rootUl.children('li.branch').find('a.branch-name').each(function(){
            if($(this).html() == branchName){
                newUl = $(this).parent().children('ul');
            }
        });
        findBranchAndCheckDescendents(testPath, newUl);
    }
}



function verifyIfAllCheckboxesAreCheckedInLevelAndCheckParent(branch){
    var testCaseList = [];
    var branches = branch.find('>ul>li>input');
    var nodes = branch.find('>ul>li>label>input');
    var allChecked = true;
    branches.each(function(){
        if(!$(this).prop('checked')){
            allChecked = false;
        }
    });
    nodes.each(function(){
        if(!$(this).prop('checked')){
            allChecked = false;
        }
    });
    if(allChecked){
        if(branch[0].id == 'suiteTests'){
            $("#allTestCasesCheckbox").prop('checked', true);
            return
        }
        else{
            branch.find('>input').prop('checked', true);
        }
        
        var parentBranch;
        if(branch.parent().closest('.branch').length == 1){
            parentBranch = branch.parent().closest('.branch');
        }
        else{
            parentBranch = $("#suiteTests");
        }

        if(parentBranch.length == 1){
            verifyIfAllCheckboxesAreCheckedInLevelAndCheckParent(parentBranch);
        }
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
            if(this.trim().length > 0){
                browsers.push(this.trim());
            }
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
                testCaseList.push(nodeWithFullPath + '.*');
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


function runSuite(){

    toastr.options = {
        "positionClass": "toast-top-center",
        "timeOut": "15000",
        "hideDuration": "100"}    
    $.ajax({
        url: "/run_suite/",
        data: {
             "project": project,
             "suite": suite,
         },
         dataType: 'json',
         type: 'POST',
         success: function(data) {
            var url = '/report/project/' + project + '/' + suite + '/' + data + '/';
            toastr.info('Running suite ' + suite + " - <a href='" + url + "'>open</a>");
         },
         error: function() {}
     });

}


function startBrowsersAutocomplete(browserSuggestions){
    console.log(browserSuggestions);
    $('#browsers').autocomplete({
        lookup: browserSuggestions,
        minChars: 0,
        delimiter: ', ',
        triggerSelectOnValidInput: false,
        onSelect: function (suggestion) {
            $('#browsers').val($('#browsers').val()+', ');
        }
    });
}

