

function displayErrorModal(errors){
    var ulContent = '';
    for(e in errors){
        ulContent += "<li>"+errors[e]+"</li>";
    } 
    $("#errorList").html(ulContent);
    $("#errorModal").modal("show");
    $("#errorModal .dismiss-modal").focus();
}