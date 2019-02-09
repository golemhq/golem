
$(document).ready(function() {
    getTests(project);
    $('#testCasesTree').treed();
});


function getTests(projectName){
    $.ajax({
        url: "/project/get_tests/",
        data: {
            "project": projectName
        },
        dataType: 'json',
        type: 'POST',
        success: function(tests) {
            $("#testCasesTree").append(Project.newElementForm('.'));
            Project.loadTreeElements($("#testCasesTree"), tests.sub_elements, 'test');
            getTestTags(tests);
        },
    });
}


function getTestTags(tests){
    $.ajax({
        url: "/project/tests/tags/",
        data: {
            "project": project
        },
        dataType: 'json',
        type: 'POST',
        success: function(testsTags) {
            displayTags(testsTags)
        },
    });
}


function displayTags(testsTags){
    Object.keys(testsTags).forEach(test => {
        let timeout = 0;
        let tags = testsTags[test];
        setTimeout(function(){
            let testElement = $(`li.tree-element[type='test'][fullpath='${test}']`);
            let tagContainer = $(`<div class="tag-container"></div>`);
            tags.forEach(function(tag){
                let tagElement = $(`<span class="tag">${tag}</span>`);
                tagContainer.append(tagElement)
            })
            testElement.find('.tree-element-buttons').before(tagContainer);
            }, timeout, tags)
    });
}
