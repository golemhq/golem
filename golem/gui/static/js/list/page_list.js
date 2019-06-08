
$(document).ready(function() {
    PageList.getPages(Global.project);
    $('#treeRoot').treed();
});


const PageList = new function(){

    this.getPages = function(projectName){
        $.ajax({
            url: "/api/project/page-tree",
            data: {
                "project": projectName
            },
            dataType: 'json',
            type: 'GET',
            success: function(pages) {
                let treeRoot = $("#treeRoot");
                Project.loadTreeElements(treeRoot, pages.sub_elements, 'page');
            },
        });
    }
}