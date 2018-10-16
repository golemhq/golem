
$(document).ready(function() {
    $("#projectCreationButton").click(function(){
        $("#projectCreationButton").hide();
        $("#projectCreationForm").show();
        $("#newProjectName").focus();
    });

    $("#createProjectCancel").click(function(){
        $("#projectCreationForm").hide();
        $("#projectCreationButton").show();
        $("#newProjectName").val('');
    });
});


function createProject(){
    var input = $("#newProjectName");
    var projectName = input.val();
    projectName = projectName.trim();

    if(projectName.length < 3){
        Main.Utils.displayErrorModal(['Project name is too short']);
        return
    }
    if(!/^[\w\s]+$/i.test(projectName)){
        Main.Utils.displayErrorModal(['Only letters, numbers and underscores are allowed']);
        return
    }
    // validate length
    if(projectName.length > 50){
        Main.Utils.displayErrorModal(['Maximum length is 50 characters']);
        return
    }
    // validate there is no more than 1 slash
    if(projectName.split('/').length -1 >= 1){
        Main.Utils.displayErrorModal(['Slashes are not allowed']);
        return   
    }
    
    $.ajax({
        url: "/new_project/",
        data: {
            "projectName": projectName,
        },
        dataType: 'json',
        type: 'POST',
        success: function(data) {
            if(data.errors.length == 0){
                // add new li for the element
                $("#projectList").append("<a href='/project/"+data.project_name+"/' class='list-group-item'>"+data.project_name+"</a>");      
                $("#projectCreationForm").hide();
                $("#projectCreationButton").show();
                $("#newProjectName").val('');
            }
            else{
                Main.Utils.displayErrorModal(data.errors);
            }
        }
    });

}