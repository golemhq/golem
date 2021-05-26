
const Suite = new function() {

    this.file;
    this.selectedTests = [];
    this.projectEnvironments;
    this.unsavedChanges = false;
    this.treeRoot = $('#treeRoot');

    this.initialize = function(file, selectedTests) {
        this.file = file;
        this.selectedTests = selectedTests;
        this.treeRoot.treed();
        this.getTestsTags(Suite.selectedTests);
        this.getSupportedBrowsers();
        this.getProjectEnvironments();
        this.checkSelectedTests(Suite.selectedTests);
        this.updateTestCount();
        this.watchForCheckboxChanges();
        this.watchForUnsavedChanges()
    }

    this.save = function(callback) {
        errors = []
        let browsers = Main.Utils.csvToArray($("#browsers").val());
        let environments = Main.Utils.csvToArray($("#environments").val());
        let tags = Main.Utils.csvToArray($("#tags").val());
        let processes = parseInt($("#processes").val());
        let testCases = this.getAllCheckedTests();

        environments.forEach(env => {
            if(!this.projectEnvironments.includes(env)){
                errors.push(`Environment <strong>${env}</strong> does not exist for project ${this.file.project}`)
            }
        });

        if(isNaN(processes))
            errors.push('Processes must be an integer')
        else if(processes < 1)
            errors.push('Processes must be at least one')

        if(errors.length > 0){
            errors.forEach(error => Main.Utils.toast('error', error, 4000))
        } else {
            xhr.put('/api/suite/save', {
                project: this.file.project,
                suite: this.file.fullName,
                browsers: browsers,
                environments: environments,
                tags: tags,
                processes: processes,
                tests: testCases
            }, result => {
                this.unsavedChanges = false;
                Main.Utils.toast('success', "Suite " + this.file.fullName + " saved", 3000)
            })
        }
    }

    this.run = function() {
        let project = this.file.project;
        let fullName = this.file.fullName;

        function _runSuite() {
            xhr.post('/api/suite/run', {
                project: project,
                suite: fullName,
            }, timestamp => {
                let url = `/report/${project}/${fullName}/${timestamp}/`;
                let msg = `Running suite ${fullName} - <a href="${url}"><strong>open</strong></a>`;
                Main.Utils.toast('info', msg, 15000)
            })
        }

        if(this.unsavedChanges)
            this.save(_runSuite())
        else
            _runSuite()
    }

    this.getTestsTags = function(tests) {
         xhr.get('/api/project/test-tags', {
            project: this.file.project
         }, testsTags => {
            let projectTags = Object.keys(testsTags).map( (key, index) => testsTags[key] ).flat();
            let uniqueProjectTags = ([...new Set(projectTags)]);
            this.startTagsAutocomplete(uniqueProjectTags);
            this.displayTags(testsTags)
         })
    }

    this.watchForUnsavedChanges = function() {
        $("input").on("change keyup paste input", () => this.unsavedChanges = true);
        window.addEventListener("beforeunload", e => {
            if(this.unsavedChanges) {
                let confirmationMessage = 'There are unsaved changes';
                (e || window.event).returnValue = confirmationMessage;
                return confirmationMessage;
            }
        })
    }

    this.getSupportedBrowsers = function() {
        xhr.get('/api/project/supported-browsers', {
            project: this.file.project
        }, browserSuggestions => {
            this.startBrowsersAutocomplete(browserSuggestions)
        })
    }

    this.getProjectEnvironments = function() {
        xhr.get('/api/project/environments', {
            project: this.file.project
        }, environments => {
            this.projectEnvironments = environments;
            this.startEnvironmentsAutocomplete(environments);
        })
    }

    this.startBrowsersAutocomplete = function(browserSuggestions) {
        $('#browsers').autocomplete({
            lookup: browserSuggestions,
            minChars: 0,
            delimiter: ', ',
            triggerSelectOnValidInput: false,
            onSelect: suggestion => {
                this.unsavedChanges = true;
                $('#browsers').val($('#browsers').val() + ', ');
            }
        })
    }

    this.startEnvironmentsAutocomplete = function(environments) {
        $('#environments').autocomplete({
            lookup: environments,
            minChars: 0,
            delimiter: ', ',
            triggerSelectOnValidInput: false,
            onSelect: suggestion => {
                this.unsavedChanges = true;
                $('#environments').val($('#environments').val() + ', ');
            }
        })
    }

    this.startTagsAutocomplete = function(tags) {
        $('#tags').autocomplete({
            lookup: tags,
            minChars: 0,
            delimiter: ', ',
            triggerSelectOnValidInput: false,
            onSelect: suggestion => {
                this.unsavedChanges = true;
                $('#tags').val($('#tags').val() + ', ');
            }
        })
    }

    this.displayTags = function(testsTags) {
        Object.keys(testsTags).forEach(test => {
            let timeout = 0;
            let tags = testsTags[test];
            setTimeout(() => {
                let testElement = $(`li[data-type='test'][full-name='${test}']`);
                let tagContainer = $(`<div class="tag-container"></div>`);
                tags.forEach(tag => {
                    let tagElement = $(`<span class="tag">${tag}</span>`);
                    tagContainer.append(tagElement)
                })
                testElement.append(tagContainer);
            }, timeout, tags)
        })
    }

    this.checkSelectedTests = function(selectedTests) {
        for(t in selectedTests) {
            this.checkTest(selectedTests[t]);
        }
    }

    this.watchForCheckboxChanges = function() {
        $(".select-testcase-checkbox").change((e) => {
            let elem = e.target;
            let node = $(elem).closest('li');
            let nodeName = node.attr('full-name');
            let isFolder = node.attr('data-type') == 'folder';
            if(elem.checked) {
                this.checkParentIfSiblingsAreChecked(nodeName);
                if(isFolder)
                    this.checkAllChildren(node, true)
            } else {
                this.uncheckAllParents(nodeName);
                if(isFolder)
                    this.checkAllChildren(node, false)
            }
            this.updateTestCount()
        })
    }

    this.checkTest = function(fullName) {
        let testLi = $(`li[data-type="test"][full-name="${fullName}"]`);
        testLi.find("input").prop('checked', true);
        this.checkParentIfSiblingsAreChecked(fullName)
    }

    this.checkParent = function(nodeFullName) {
        let parentName = this.parentFolderName(nodeFullName);
        let parentLi;
        if(parentName == '')
            parentLi = $("#suiteTests")
        else
            parentLi = $(`li[data-type="folder"][full-name="${parentName}"]`)
        parentLi.find("input").first().prop('checked', true);
        if(parentName != '')
            this.checkParentIfSiblingsAreChecked(parentName)
    }

    this.checkParentIfSiblingsAreChecked = function(nodeFullName) {
        if(this.allSiblingsAreChecked(nodeFullName))
            this.checkParent(nodeFullName)
    }

    this.updateTestCount = function() {
        let totalCheckedTests = this.getCheckedTestNumber();
        let totalTests = this.getAllTestAmount();
        $("#testCount").html(totalCheckedTests+"/"+totalTests);
    }

    this.checkAllChildren = function(folderNode, isChecked) {
        folderNode.find($(".select-testcase-checkbox")).each((i, element) => {
            $(element).prop('checked', isChecked)
        })
    }

    this.uncheckAllParents = function(nodeFullName) {
        let nodeLi = $(`li[full-name="${nodeFullName}"]`);
        let parents = nodeLi.parents('li');
        parents.each((i, elem) => {
            if($(elem).hasClass('branch') || $(elem).hasClass('tree'))
                $(elem).children('input').prop('checked', false)
        })
    }

    this.getAllCheckedTests = function() {
        let testCaseList = [];
        if($("#allTestCasesCheckbox").prop('checked'))
            testCaseList.push('*')
        else
            testCasesList = this.getAllCheckedTestsInALevel(Suite.treeRoot, testCaseList)
        return testCaseList
    }

    this.getAllTestAmount = function() {
        return $(".test-checkbox").length
    }

    this.getCheckedTestNumber = function() {
        return $(".test-checkbox:checked").length
    }

    this.getAllCheckedTestsInALevel = function(rootUl, testCaseList) {
        let lis = rootUl.children('li');
        lis.each((i, elem) => {
            let thisLi = $(elem);
            if(thisLi.hasClass('branch')) {
                let thisBranchInput = thisLi.children('input');
                let thisBranchName = thisLi.attr('full-name');
                if(thisBranchInput.prop('checked')) {
                    testCaseList.push(thisBranchName + '.*');
                } else {
                    let newRootUl = thisLi.children('ul');
                    testCaseList = this.getAllCheckedTestsInALevel(newRootUl, testCaseList);
                }
            } else {
                let thisLiName = thisLi.attr('full-name');
                let thisLiInput = thisLi.find('input');
                if(thisLiInput.prop('checked')) {
                    testCaseList.push(thisLiName)
                }
            }
        });
        return testCaseList
    }

    this.allSiblingsAreChecked = function(nodeFullName) {
        let siblings = this.getSiblings(nodeFullName);
        let result = true;
        siblings.each((i, elem) => {
            let thisCheckbox = $(elem).find('> input, > label > input').first();
            if(!thisCheckbox.prop('checked')) {
                result = false
                return false
            }
        })
        return result
    }

    this.getSiblings = function(nodeName) {
        let parentFolderName = this.parentFolderName(nodeName);
        let folderUl;
        if(parentFolderName == '')
            folderUl = this.treeRoot
        else
            folderUl = $(`li[data-type="folder"][full-name="${parentFolderName}"] > ul`)
        return folderUl.children("li")
    }

    this.parentFolderName = function(testFullName) {
        let splitted = testFullName.split('.');
        splitted.pop();
        return splitted.join('.');
    }
}
