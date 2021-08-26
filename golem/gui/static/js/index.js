
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
	$("#projectImportButton").click(function(){
        $("#projectImportButton").hide();
        $("#projectImportForm").show();
        $("#file").focus();
    });

    $("#ProjectImportCancel").click(function(){
        $("#projectImportForm").hide();
        $("#projectImportButton").show();
		$("#file").val(null);
    });
});


function createProject() {
    let input = $("#newProjectName");
    let projectName = input.val();
    projectName = projectName.trim();

    if(projectName.length < 3) {
        Main.Utils.displayErrorModal(['Project name is too short']);
        return
    }
    if(!/^[\w\s]+$/i.test(projectName)) {
        Main.Utils.displayErrorModal(['Only letters, numbers and underscores are allowed']);
        return
    }
    if(projectName.length > 50) {
        Main.Utils.displayErrorModal(['Maximum length is 50 characters']);
        return
    }
    xhr.post('/api/project', {
        'project': projectName
    }, data => {
        if(data.errors.length == 0) {
            $("#projectList").append(`<a href="/project/${data.project_name}/" class="list-group-item">${data.project_name}</a>`);
            $("#projectCreationForm").hide();
            $("#projectCreationButton").show();
            $("#newProjectName").val('');
        } else {
            Main.Utils.displayErrorModal(data.errors);
        }
    })
}

function importProject() {
    var form_data = new FormData($('#upload-file')[0]);
	var countfile = document.getElementById('file').files.length;
	
	if(countfile == 0) {
					Main.Utils.displayErrorModal(['Select at least one side file']);
					return;
				}
	var file_name = document.getElementById('file').files[0].name
	if(file_name.includes(".side") ==  false)
	{
		Main.Utils.displayErrorModal(['file should be .side extension']);
					return;
	}
        $.ajax({
            type: 'POST',
            url: '/api/uploadside',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success: function(data) {	
				if(data.errors.length == 0) {
            $("#projectList").append(`<a href="/project/${data.project_name}/" class="list-group-item">${data.project_name}</a>`);
            $("#projectImportForm").hide();
        $("#projectImportButton").show();
		$("#file").val(null);
		Main.Utils.toast('success', `project ${data.project_name} successfully imported`, 3000)
        } else {
            Main.Utils.displayErrorModal(data.errors);
        }
            },
			error: function (XMLHttpRequest, textStatus, errorThrown) {
				alert(textStatus,errorThrown);
			}
        });
}
