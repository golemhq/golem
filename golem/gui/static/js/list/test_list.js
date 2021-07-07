
$(document).ready(function() {
    TestList.getTests(Global.project)
});


const TestList = new function() {

    this.getTests = function(projectName) {
        xhr.get('/api/project/test-tree', {'project': projectName}, tests => {
            FileExplorer.initialize(tests, 'test', $('#fileExporerContainer')[0]);
            TestList.getTestsTags();
        })
    }

    this.getTestsTags = function() {
        xhr.get('/api/project/test-tags', {'project': Global.project}, testsTags => {
            TestList.displayTags(testsTags)
        })
    }

    this.displayTags = function(testsTags) {
        Object.keys(testsTags).forEach(test => {
            let file = FileExplorer.getFile(test);
            if(file) {
                FileExplorer.getFile(test).addTags(testsTags[test])
            }
        });
    }
}
