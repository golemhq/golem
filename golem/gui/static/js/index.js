
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
    let input = $("#newProjectName");
    let projectName = input.val();
    projectName = projectName.trim();

    if(projectName.length < 3){
        Main.Utils.displayErrorModal(['Project name is too short']);
        return
    }
    if(!/^[\w\s]+$/i.test(projectName)){
        Main.Utils.displayErrorModal(['Only letters, numbers and underscores are allowed']);
        return
    }
    if(projectName.length > 50){
        Main.Utils.displayErrorModal(['Maximum length is 50 characters']);
        return
    }
    $.ajax({
        url: "/api/project",
        data: JSON.stringify({
            "project": projectName,
        }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        success: function(data) {
            if(data.errors.length == 0){
                $("#projectList").append(`<a href="/project/${data.project_name}/" class="list-group-item">${data.project_name}</a>`);
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