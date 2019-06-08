
$(document).ready(function() {
    getUsers()
});


function getUsers(){
    $.ajax({
        url: "/api/users",
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'GET',
        success: function(users) {
            users.forEach(function(user){
                let isSuperuser = '';
                if(user.is_superuser){
                    isSuperuser = 'yes'
                }
                let email = '';
                if(user.email){
                    email = user.email
                }
                let projects = $('<div></div>');
                Object.keys(user.projects).forEach(project => {
                    let permission = user.projects[project];
                    if(project == '*'){
                        project = 'all projects'
                    }
                    projects.append(`<span class="project-permission-label tag">${project} - ${permission}</span>`)
                });
                let tr = `<tr>
                    <td>${user.username}</td>
                    <td>${email}</td>
                    <td>${isSuperuser}</td>
                    <td style="max-width:350px">${projects.html()}</td>
                    <td>
                        <a class="btn btn-default btn-sm edit-user-button" href="/users/edit/${user.username}/">Edit</a>
                        <button class="btn btn-default btn-sm delete-user-button" onclick="deleteUser('${user.username}')">Delete</button>
                    </td>
                </tr>`
                $("#userTable>tbody").append(tr)
            });
            $("#usersTableLoadingIconContainer").hide()
        }
    });
}


function deleteUser(username){
    if(username == Global.user.username){
        Main.Utils.toast('error', 'Cannot delete current user', 3000)
        return
    }
    let callback = function(){
        deleteUserConfirmed(username);
    }
    Main.Utils.displayConfirmModal('Delete', `Are you sure you want to delete user <strong>${username}</strong>?`, callback);
}

function deleteUserConfirmed(username){
    $.ajax({
        url: "/api/users/delete",
        data: JSON.stringify({"username": username}),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'DELETE',
        success: function(result) {
            if(result.errors.length){
                result.errors.forEach(error => Main.Utils.toast('error', error, 3000))
            }
            else{
                Main.Utils.toast('success', "User deleted", 2000);
                $("#userTable>tbody").html('');
                getUsers()
            }
        }
    });
}