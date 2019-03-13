
$(document).ready(function() {
    PageList.getPages(project);
    $('#treeRoot').treed();
});


const PageList = new function(){

    this.getPages = function(projectName){
        $.ajax({
            url: "/project/get_pages/",
            data: {
                "project": projectName
            },
            dataType: 'json',
            type: 'POST',
            success: function(pages) {
                let treeRoot = $("#treeRoot");
                treeRoot.append(Project.newElementForm('.'));
                Project.loadTreeElements(treeRoot, pages.sub_elements, 'page');
            },
        });
    }
}