
$(document).ready(function() {
    $('#testCasesTree').treed();
    $('#pagesTree').treed();

    generateHealthChart(project);
});


function displayNewElementForm(elem){
    var parent = $(elem).parent().parent();
    parent.find(".new-element-form").show().find("input").focus();
    parent.find(".display-new-element-link").hide();
}


function addElement(event){
    event.preventDefault();
    var input = $(event.target);
    var elementType = '';
    var urlPrefixForElementType = '';
    var inputClass = '';
    if(input.hasClass('new-test-case')){
        elementType = 'test';
        urlPrefixForElementType = 'test';
        inputClass = 'new-test-case';
    }
    else if(input.hasClass('new-page-object')){
        elementType = 'page';
        urlPrefixForElementType = 'page';
        inputClass = 'new-page-object';
    }
    else if(input.hasClass('new-suite')){
        elementType = 'suite';
        urlPrefixForElementType = 'suite';
        inputClass = 'new-suite';
    }

    var parentsSeparetedByDots = getParentsSeparatedByDots(input);
    var elementName = input.val().trim();
    var isDir = false;
    if(elementName.indexOf('/') > -1){
        isDir = true;
        if(elementType == 'test') elementType = 'test_dir';
        else if(elementType == 'page') elementType = 'page_dir';
    }

    if(elementName.length == 0){
        input.val('');
        input.parent().hide();
        input.parent().parent().find(".display-new-element-link").show();
        return
    }
    // validate spaces
    if(elementName.indexOf(' ') > -1){
        displayErrorModal(['Spaces are not allowed']);
        return
    }
    // validate length
    if(elementName.length > 60){
        displayErrorModal(['Maximum length is 60 characters']);
        return
    }
    // validate there is no more than 1 slash
    if(elementName.split('/').length -1 > 1){
        displayErrorModal(['Only one slash character is allowed']);
        return   
    }
    // validate there is no more than 1 slash
    if(elementType == 'suite' &&  elementName.split('/').length -1 == 1){
        displayErrorModal(['Suite names cannot contain slashes']);
        return   
    }
    // validate if there is a slash it is trailing
    if(isDir){
        if(elementName.indexOf('/') != elementName.length-1){
            displayErrorModal(['Directories should end with a trailing slash character']);
            return
        }
    }
    
    $.ajax({
        url: "/new_tree_element/",
        data: {
            "project": project,
            "elementType": elementType,
            "isDir": isDir,
            "parents": parentsSeparetedByDots,
            "elementName": elementName
        },
        dataType: 'json',
        type: 'POST',
        success: function(data) {
            if(data.errors.length == 0){

                // add new li for the element
                var lastLi = input.parent().parent().parent().find("li").last();
                lastLi.before("<li class='tree-element'></li>");
                var newLi = lastLi.prev();

                if(data.is_dir){
                    //var li = input.parent().parent();
                    addBranchToTree(newLi, data.element_name, inputClass);

                    // input.parent().hide();
                    // input.parent().parent().find(".display-new-element-link").show();
                }
                else{
                    if(parentsSeparetedByDots.length > 0){
                        var urlForTeseCase = parentsSeparetedByDots + '.' + data.element_name;
                    }
                    else{
                        var urlForTeseCase = data.element_name;
                    }
                    newLi.html("<a href='/p/"+data.project_name+"/"+urlPrefixForElementType+"/"+urlForTeseCase+"/'>"+data.element_name+"</a> \
                                <span class='pull-right tree-element-buttons'> \
                                    <button><i class='glyphicon glyphicon-edit'></i></button> \
                                    <button><i class='glyphicon glyphicon-copy'></i></button> \
                                    <button><i class='glyphicon glyphicon-remove'></i></button> \
                                </span>");
                }

                // reset the form, hide the form and display the add new link
                input.val("");
                input.parent().hide();
                input.parent().parent().find(".display-new-element-link").show();
                
            }
            else{
                displayErrorModal(data.errors);
            }
        },
        error: function() {}
    });

}


function getParentsSeparatedByDots(elem){
    var dotted_branches = '';
    elem.parents('.branch').each(function(){
        if(dotted_branches.length == 0){
            dotted_branches = $(this).find('a').html();    
        }
        else {
            dotted_branches = $(this).find('a').html() + '.' + dotted_branches;
        }
    });
    return dotted_branches
}


function removeTreeElement(elem){
    var parent = $(elem).parent().parent();
}


function generateHealthChart(projectName){
    $.ajax({
        url: "/report/get_project_health_data/",
        data: {
            "project": projectName,
        },
        dataType: 'json',
        type: 'POST',
        success: function( healthData ) { 
            if($.isEmptyObject(healthData)){
                $("#healthContainer").html("<div class='text-center' style='padding-top: 55px'>no data</div>");
            }
            else{
                loadHealthData(healthData);
            }
        }
    });
}


function loadHealthData(healthData){

    var totalOk = 0;
    var totalFail = 0;

    var table = "\
        <table id='healthTable' class='table no-margin-bottom last-execution-table'>\
            <thead>\
                <tr>\
                    <th>Suite</th>\
                    <th>Date &amp; Time</th>\
                    <th>Result</th>\
                </tr>\
            </thead>\
            <tbody>\
            </tbody>\
        </table>";
    $("#healthTableContainer").append(table);

    $.each(healthData, function(suite){
        var okPercentage = healthData[suite].total_ok * 100 / healthData[suite].total;
        totalOk += healthData[suite].total_ok;
        totalFail += healthData[suite].total_fail;

        var newRow = "\
            <tr class='last-execution-row' onclick=''>\
                <td class=''>"+suite+"</td>\
                <td class=''>"+utils.getDateTimeFromTimestamp(healthData[suite].execution)+"</td>\
                <td class=''>\
                    <div class='progress progress-bar-container'>\
                    <div aria-valuenow='10' style='width: 100%;' class='progress-bar progress-bar-danger barra-roja' data-transitiongoal='10'></div>\
                    <div aria-valuenow='20' style='width: 50%;' class='progress-bar barra-azul' data-transitiongoal='"+okPercentage+"'></div>\
                    </div>\
                </td>\
            </tr>";
        newRow = $(newRow);

        newRow.attr('onclick', "document.location.href='/report/project/"+project+"/"+suite+"/"+healthData[suite].execution+"/'");

        $("#healthTable tbody").append(newRow);

        setTimeout(function(){
            newRow.find('.progress-bar.barra-azul').css('width', okPercentage+'%');
        }, 1, newRow);

    });

    var ctx = document.getElementById('healthChartCanvas').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Passed', 'Failed'],
            datasets: [
                {
                    data: [totalOk, totalFail],
                    backgroundColor: [
                        "rgb(66, 139, 202)",
                        "rgb(217, 83, 79)",
                    ],
                    hoverBackgroundColor: [
                        "rgb(66, 139, 202)",
                        "rgb(217, 83, 79)"
                    ]
                }
            ]
        },
        options: {
            animation: {
                animateScale: true,
                animateRotate: true
            },
            responsive: true,
            maintainAspectRatio : true,
        }
    });

    
    

}