
$(document).ready(function() {      

    //$('#testCasesTree').treed();

    $('#testCasesTree').treed({openedClass : 'glyphicon-folder-open', closedClass : 'glyphicon-folder-close'});


    $('#pagesTree').treed({openedClass : 'glyphicon-folder-open', closedClass : 'glyphicon-folder-close'});

 //    $('#testCasesTree .branch').each(function(){

	// 	var icon = $(this).children('i:first');
	// 	icon.toggleClass('glyphicon-minus-sign glyphicon-plus-sign');
	// 	$(this).children().children().toggle();

	// });

});


function startAddNewTestCase(elem){
    var parent = $(elem).parent();
    console.log(parent);
    var input = $("<input class='new-test-case-input' type='text'>");
    $(input).blur(function() {
        //alert('blur')
        addNewTestCase($(this).val())
    });

    $(input).keyup(function(e) {
        if (e.which == 13) // Enter key
            //alert('keyup')
        addNewTestCase($(this).val());
    });

    parent.html('');
    parent.append(input);
    input.focus();
}


function addNewTestCase(testCaseName){

    if(testCaseName.length == 0){
        return
    }
    if(testCaseName.indexOf('/') > -1){
        // is a new directory
        $.ajax({
            url: "/new_directory/",
            data: {
                "project": project,
                "directoryName": testCaseName
            },
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                if(data.result == 'ok'){
                    var li = $(".new-test-case-input").parent();
                    li.addClass('branch');
                    li.html("<i class='indicator glyphicon glyphicon-folder-close'></i> \
                                <a href='#'>"+data.directory_name+"</a>");
                    //li.html("<a href='/p/"+data.project_name+"/tc/"+data.tc_name+"/'>"+data.tc_name+"</a>");
                }
            },
            error: function() {}
        });
    }
    else {
        $.ajax({
            url: "/nuevo_test_case/",
            data: {
                "project": project,
                "testCaseName": testCaseName
            },
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                if(data.result == 'ok'){
                    var li = $(".new-test-case-input").parent();
                    li.html("<a href='/p/"+data.project_name+"/tc/"+data.tc_name+"/'>"+data.tc_name+"</a>");
                }

            },
            error: function() {
                
            }
        });

    }
}






function startAddNewPageObject(elem){
    var parent = $(elem).parent();
    console.log(parent);
    var input = $("<input class='new-page-object-input' type='text'>");
    $(input).blur(function() {
        //alert('blur')
        addNewPageObject($(this).val())
    });

    $(input).keyup(function(e) {
        if (e.which == 13) // Enter key
            //alert('keyup')
        addNewPageObject($(this).val());
    });

    parent.html('');
    parent.append(input);
}


function addNewPageObject(pageObjectName){

    if(pageObjectName.indexOf('/') > -1){
        // is a new directory
        // $.ajax({
        //     url: "/new_directory/",
        //     data: {
        //         "project": project,
        //         "directoryName": testCaseName
        //     },
        //     dataType: 'json',
        //     type: 'POST',
        //     success: function(data) {
        //         if(data.result == 'ok'){
        //             var li = $(".new-test-case-input").parent();
        //             li.addClass('branch');
        //             li.html("<i class='indicator glyphicon glyphicon-folder-close'></i> \
        //                         <a href='#'>"+data.directory_name+"</a>");
        //             //li.html("<a href='/p/"+data.project_name+"/tc/"+data.tc_name+"/'>"+data.tc_name+"</a>");
        //         }
        //     },
        //     error: function() {}
        // });
    }
    else {
        $.ajax({
            url: "/new_page_object/",
            data: {
                "project": project,
                "pageObjectName": pageObjectName
            },
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                if(data.result == 'ok'){
                    var li = $(".new-page-object-input").parent();
                    li.html("<a href='/p/"+data.project_name+"/page/"+data.page_object_name+"/'>"+data.page_object_name+"</a>");
                }

            },
            error: function() {
                
            }
        });

    }
}