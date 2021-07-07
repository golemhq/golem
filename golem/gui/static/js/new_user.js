
$(document).ready(function() {
    getProjects()
    getProjectPermissionsOptions()
});


function getProjects() {
    xhr.get('/api/projects', {}, projects => {
        projects.push('all projects');
        autocomplete = $("#project").autocomplete({
            lookup: projects,
            minChars: 0,
            triggerSelectOnValidInput: false
        });
    })
}


function getProjectPermissionsOptions(){
    xhr.get('/api/golem/project-permissions', {}, permissions => {
        autocomplete = $("#permission").autocomplete({
            lookup: permissions,
            minChars: 0,
            triggerSelectOnValidInput: false
        })
    })
}


function addPermissionToList() {
    let project = $("#project").val().trim();
    let permission = $("#permission").val().trim();
    if(project.length && permission.length) {
        if(project == 'all projects') {
            project = '*'
        }
        // if a permission with same project already exists
        // in the list remove it first
        $("#projectPermissionList>tbody>.permission-row").each(function() {
            let tds = $(this).find('td');
            let p = $(tds[0]).html();
            if(p == project) {
                $(this).remove()
            }
        })
        addPermission(project, permission);
        $("#project").val('');
        $("#permission").val('')
    }
}


function addPermission(project, permission){
    let projectPermission = `
        <tr class="permission-row">
            <td>${project}</td>
            <td>${permission}</td>
            <td><button type="button" class="close" onclick="removePermissionRow(event)"><span aria-hidden="true">&times;</span></button></td>
        </tr>`;
    $("#projectPermissionList>tbody").append(projectPermission);
}


function createOrUpdateUser() {
    let username = $("#username").val().trim();
    let email = $("#email").val().trim();
    let isSuperuser = $("#isSuperuser").prop('checked');
    let projectPermissions = getSelectedProjectPermissions();
    if(editionMode) {
        updateUser(EditUser.username, username, email, isSuperuser, projectPermissions)
    } else {
        let password = $("#password").val();
        createUser(username, email, password, isSuperuser, projectPermissions)
    }
}


function createUser(username, email, password, isSuperuser, projectPermissions){
    xhr.put('/api/users/new', {
        username,
        email,
        password,
        isSuperuser,
        projectPermissions
    }, errors => {
        if(errors.length) {
            errors.forEach(error => Main.Utils.toast('error', error, 4000))
        } else {
            window.location.replace('/users/');
        }
    })
}


function updateUser(oldUsername, newUsername, email, isSuperuser, projectPermissions){
    xhr.post('/api/users/edit', {
        oldUsername,
        newUsername,
        email,
        isSuperuser,
        projectPermissions
    }, errors => {
        if(errors.length) {
            errors.forEach(error => Main.Utils.toast('error', error, 4000))
        } else {
            window.location.replace('/users/');
        }
    })
}


function removePermissionRow(event){
    $(event.srcElement).closest('.permission-row' ).remove();
}


function getSelectedProjectPermissions(){
    let projectPermissions = [];
    $("#projectPermissionList>tbody>.permission-row").each(function(){
        let tds = $(this).find('td');
        let project = $(tds[0]).html();
        let permission = $(tds[1]).html();
        projectPermissions.push({'project': project, 'permission': permission})
    })
    return projectPermissions
}


function openResetPassword(){
    $("#resetPasswordInput").val('');
    $("#resetPasswordModal").modal("show");
    $('#resetPasswordModal').on('shown.bs.modal', function (){ $('#resetPasswordInput').focus() });
}


function resetPassword() {
    let newPassword = $("#resetPasswordInput").val();
    if(newPassword.length == 0) {
        return
    }
    xhr.post('/api/users/reset-password', {
        'username': EditUser.username,
        'newPassword': newPassword
    }, result => {
        $("#resetPasswordModal").modal("hide");
        if(result.errors.length) {
            result.errors.forEach(error => Main.Utils.toast('error', error, 4000))
        } else {
            Main.Utils.toast('success', 'Password reset', 2000);
        }
    })
}