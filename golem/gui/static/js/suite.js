
$(document).ready(function() {
    Suite.initialize(Global.project, suite, selectedTests);
});


const Suite = new function(){

    this.project;
    this.name;
    this.selectedTests = [];
    this.unsavedChanges = false;
    this.treeRoot = $('#treeRoot');

    this.initialize = function(project, suiteName, selectedTests){
        Suite.project = project;
        Suite.name = suiteName;
        Suite.selectedTests = selectedTests
        Suite.treeRoot.treed();
        Suite.Utils.getTestsTags(Suite.selectedTests);
        Suite.Utils.getSupportedBrowsers();
        Suite.Utils.getProjectEnvironments();
        Suite.TestTree.checkSelectedTests(Suite.selectedTests);
        Suite.TestTree.updateTestCount();
        Suite.TestTree.watchForCheckboxChanges();
        Suite.Utils.watchForUnsavedChanges()
    }

    this.save = function(callback){
        errors = []
        let browsers = Main.Utils.csvToArray($("#browsers").val());
        let environments = Main.Utils.csvToArray($("#environments").val());
        let tags = Main.Utils.csvToArray($("#tags").val());
        let processes = parseInt($("#processes").val());
        let testCases = Suite.TestTree.getAllCheckedTests();

        environments.forEach(function(env){
            if(!Suite.projectEnvironments.includes(env)){
                errors.push(`Environment <strong>${env}</strong> does not exist for project ${Suite.project}`)
            }
        });

        if(isNaN(processes)){
            errors.push('Processes must be an integer')
        }
        else if(processes < 1){
            errors.push('Processes must be at least one')
        }

        if(errors.length > 0){
            errors.forEach(error => Main.Utils.toast('error', error, 4000))
        }
        else{
            $.ajax({
                url: "/api/suite/save",
                data: JSON.stringify({
                        "project": Global.project,
                        "suite": suite,
                        "browsers": browsers,
                        "environments": environments,
                        "tags": tags,
                        "processes": processes,
                        "tests": testCases
                    }),
                dataType: 'json',
                contentType: 'application/json; charset=utf-8',
                type: 'PUT',
                success: function(data) {
                    Suite.unsavedChanges = false;
                    Main.Utils.toast('success', "Suite "+suite+" saved", 3000)
                }
            });
        }
    }

    this.run = function(){
        function _runSuite(){
            $.ajax({
                url: "/api/suite/run",
                data: JSON.stringify({
                    "project": Global.project,
                    "suite": suite,
                }),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                type: 'POST',
                success: function(timestamp) {
                    let url = `/report/project/${Global.project}/suite/${suite}/${timestamp}/`;
                    let msg = `Running suite ${suite} - <a href="${url}"><strong>open</strong></a>`;
                    Main.Utils.toast('info', msg, 15000)
                }
            });
        }
        if(Suite.unsavedChanges){
            Suite.save(_runSuite())
        }
        else{
            _runSuite()
        }
    }

    this.Utils = new function(){

        this.getTestsTags = function(tests){
            $.ajax({
                url: "/api/project/test-tags",
                data: {
                    "project": Suite.project
                },
                dataType: 'json',
                type: 'GET',
                success: function(testsTags) {
                    let projectTags = Object.keys(testsTags).map( (key, index) => testsTags[key] ).flat();
                    let uniqueProjectTags = ([...new Set(projectTags)]);
                    Suite.Utils.startTagsAutocomplete(uniqueProjectTags);

                    Suite.TestTree.displayTags(testsTags)
                },
            });
        }

        this.watchForUnsavedChanges = function(){
            $("input").on("change keyup paste input", function(){
                Suite.unsavedChanges = true;
            });
            window.addEventListener("beforeunload", function (e) {
                if(Suite.unsavedChanges){
                    let confirmationMessage = 'There are unsaved changes';
                    (e || window.event).returnValue = confirmationMessage;
                    return confirmationMessage;
                }
            });
        }

        this.getSupportedBrowsers = function(){
            $.ajax({
                url: "/api/project/supported-browsers",
                data: {
                    project: Suite.project
                },
                dataType: 'json',
                type: 'GET',
                success: function(browserSuggestions) {
                    Suite.Utils.startBrowsersAutocomplete(browserSuggestions);
                }
            });
        }

        this.getProjectEnvironments = function(){
            $.ajax({
                url: "/api/project/environments",
                data: {
                    project: Suite.project
                },
                dataType: 'json',
                type: 'GET',
                success: function(environments) {
                    Suite.projectEnvironments = environments;
                    Suite.Utils.startEnvironmentsAutocomplete(environments);
                }
            });
        }

        this.startBrowsersAutocomplete = function(browserSuggestions){
            $('#browsers').autocomplete({
                lookup: browserSuggestions,
                minChars: 0,
                delimiter: ', ',
                triggerSelectOnValidInput: false,
                onSelect: function (suggestion) {
                    Suite.unsavedChanges = true;
                    $('#browsers').val($('#browsers').val()+', ');
                }
            });
        }

        this.startEnvironmentsAutocomplete = function(environments){
            $('#environments').autocomplete({
                lookup: environments,
                minChars: 0,
                delimiter: ', ',
                triggerSelectOnValidInput: false,
                onSelect: function (suggestion) {
                    Suite.unsavedChanges = true;
                    $('#environments').val($('#environments').val()+', ');
                }
            });
        }

        this.startTagsAutocomplete = function(tags){
            $('#tags').autocomplete({
                lookup: tags,
                minChars: 0,
                delimiter: ', ',
                triggerSelectOnValidInput: false,
                onSelect: function (suggestion) {
                    Suite.unsavedChanges = true;
                    $('#tags').val($('#tags').val()+', ');
                }
            });
        }
    }

    this.TestTree = new function(){

        this.displayTags = function(testsTags){
            Object.keys(testsTags).forEach(test => {
                let timeout = 0;
                let tags = testsTags[test];
                setTimeout(function(){
                    let testElement = $(`li[data-type='test'][full-name='${test}']`);
                    let tagContainer = $(`<div class="tag-container"></div>`);
                    tags.forEach(function(tag){
                        let tagElement = $(`<span class="tag">${tag}</span>`);
                        tagContainer.append(tagElement)
                    })
                    testElement.append(tagContainer);
                    }, timeout, tags)
            });
        }

        this.checkSelectedTests = function(selectedTests){
            for(t in selectedTests){
                Suite.TestTree.checkTest(selectedTests[t]);
            }
        }

        this.watchForCheckboxChanges = function(){
            $(".select-testcase-checkbox").change(function(){
                let node = $(this).closest('li');
                let nodeName = node.attr('full-name');
                let isFolder = node.attr('data-type') == 'folder';
                if( this.checked ){
                    Suite.TestTree.checkParentIfSiblingsAreChecked(nodeName);
                    if(isFolder){
                        Suite.TestTree.checkAllChildren(node, true);
                    }
                }
                else{
                    Suite.TestTree.uncheckAllParents(nodeName);
                    if(isFolder){
                        Suite.TestTree.checkAllChildren(node, false);
                    }
                }
                Suite.TestTree.updateTestCount()
            });
        }

        this.checkTest = function(fullName){
            let testLi = $(`li[data-type="test"][full-name="${fullName}"]`);
            testLi.find("input").prop('checked', true);
            Suite.TestTree.checkParentIfSiblingsAreChecked(fullName);
        }

        this.checkParent = function(nodeFullName){
            let parentName = Suite.TestTree.parentFolderName(nodeFullName);
            let parentLi;
            if(parentName == ''){
                parentLi = $("#suiteTests")
            }
            else{
                parentLi = $(`li[data-type="folder"][full-name="${parentName}"]`)
            }
            parentLi.find("input").first().prop('checked', true);
            if(parentName != ''){
                Suite.TestTree.checkParentIfSiblingsAreChecked(parentName);
            }
        }

        this.checkParentIfSiblingsAreChecked = function(nodeFullName){
            if(Suite.TestTree.allSiblingsAreChecked(nodeFullName)){
                Suite.TestTree.checkParent(nodeFullName)
            }
        }

        this.updateTestCount = function(){
            let totalCheckedTests = Suite.TestTree.getCheckedTestNumber();
            let totalTests = Suite.TestTree.getAllTestAmount();
            $("#testCount").html(totalCheckedTests+"/"+totalTests);
        }

        this.checkAllChildren = function(folderNode, isChecked){
            folderNode.find($(".select-testcase-checkbox")).each(function(){
                $(this).prop('checked', isChecked);
            });
        }

        this.uncheckAllParents = function(nodeFullName){
            let nodeLi = $(`li[full-name="${nodeFullName}"]`);
            let parents = nodeLi.parents('li');
            parents.each(function(){
                if($(this).hasClass('branch') || $(this).hasClass('tree')){
                    $(this).children('input').prop('checked', false);
                }
            });
        }

        this.getAllCheckedTests = function(){
            let testCaseList = [];
            if($("#allTestCasesCheckbox").prop('checked')){
                testCaseList.push('*');
            }
            else{
                testCasesList = Suite.TestTree.getAllCheckedTestsInALevel(Suite.treeRoot, testCaseList);
            }
            return testCaseList
        }

        this.getAllTestAmount = function(){
            let len = $(".test-checkbox").length;
            return len
        }

        this.getCheckedTestNumber = function(){
            return $(".test-checkbox:checked").length;
        }

        this.getAllCheckedTestsInALevel = function(rootUl, testCaseList){
            let lis = rootUl.children('li');
            lis.each(function(){
                let thisLi = $(this);
                if(thisLi.hasClass('branch')){
                    let thisBranchInput = thisLi.children('input');
                    let thisBranchName = thisLi.attr('full-name');
                    if(thisBranchInput.prop('checked')){
                        testCaseList.push(thisBranchName + '.*');
                    }
                    else{
                        let newRootUl = thisLi.children('ul');
                        testCaseList = Suite.TestTree.getAllCheckedTestsInALevel(newRootUl, testCaseList);
                    }
                }
                else{
                    let thisLiName = thisLi.attr('full-name');
                    let thisLiInput = thisLi.find('input');
                    if(thisLiInput.prop('checked')){
                        testCaseList.push(thisLiName);
                    }
                }
            });
            return testCaseList
        }

        this.allSiblingsAreChecked = function(nodeFullName){
            let siblings = Suite.TestTree.getSiblings(nodeFullName);
            let result = true;
            siblings.each(function(){
                let thisCheckbox = $(this).find('> input, > label > input').first();
                if(!thisCheckbox.prop('checked')){
                    result = false
                    return false
                }
            })
            return result
        }

        this.getSiblings = function(nodeName){
            let parentFolderName = Suite.TestTree.parentFolderName(nodeName);
            let folderUl;
            if(parentFolderName == ''){
                folderUl = Suite.treeRoot
            }
            else{
                folderUl = $(`li[data-type="folder"][full-name="${parentFolderName}"] > ul`)
            }
            return folderUl.children("li")
        }

        this.parentFolderName = function(testFullName){
            let splitted = testFullName.split('.');
            splitted.pop();
            return splitted.join('.');
        }
    }
}
