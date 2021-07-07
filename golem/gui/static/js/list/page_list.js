
$(document).ready(function() {
    PageList.getPages(Global.project)
});


const PageList = new function(){

    this.getPages = function(projectName) {
        xhr.get('/api/project/page-tree', {'project': projectName}, pages => {
            FileExplorer.initialize(pages, 'page', $('#fileExporerContainer')[0]);
        })
    }
}