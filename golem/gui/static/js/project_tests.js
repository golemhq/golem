
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
        },
    });
}