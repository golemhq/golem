
$(document).ready(function() {
    TestList.getTests(Global.project)
});


const TestList = new function(){

    this.getTests = function(projectName){
        $.ajax({
            url: "/api/project/test-tree",
            data: {
                "project": projectName
            },
            dataType: 'json',
            type: 'GET',
            success: function(tests) {
                FileExplorer.initialize(tests, 'test', $('#fileExporerContainer')[0]);
                TestList.getTestsTags(tests);
            }
        })
    }

    this.getTestsTags = function(tests){
        $.ajax({
            url: "/api/project/test-tags",
            data: {
                "project": Global.project
            },
            dataType: 'json',
            type: 'GET',
            success: function(testsTags) {
                TestList.displayTags(testsTags)
            },
        });
    }

    this.displayTags = function(testsTags){
        Object.keys(testsTags).forEach(test => {
            let file = FileExplorer.getFile(test);
            if(file){ FileExplorer.getFile(test).addTags(testsTags[test]) }
        });
    }
}
