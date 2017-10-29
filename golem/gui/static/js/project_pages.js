
$(document).ready(function() {
    getPages(project);
    $('#pagesTree').treed();
});


function getPages(projectName){
    $.ajax({
        url: "/project/get_pages/",
        data: {
            "project": projectName
        },
        dataType: 'json',
        type: 'POST',
        success: function(pages) {
            $("#pagesTree").append(Project.newElementForm('.'));
            Project.loadTreeElements($("#pagesTree"), pages.sub_elements, 'page');
        },
    });
}
