
$(document).ready(function() {
    PageList.getPages(Global.project)
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
                FileExplorer.initialize(pages, 'page', $('#fileExporerContainer')[0]);
            },
        });
    }
}