

function displayErrorModal(errors){
    var ulContent = '';
    for(e in errors){
        ulContent += "<li>"+errors[e]+"</li>";
    } 
    $("#errorList").html(ulContent);
    $("#errorModal").modal("show");
    $("#errorModal .dismiss-modal").focus();
}


function passIcon(){
    return '<span class="pass-icon"><span class="glyphicon glyphicon-ok-circle" aria-hidden="true"></span></span>'
}


function failIcon(){
    return '<span class="fail-icon"><span class="glyphicon glyphicon-remove-circle" aria-hidden="true"></span></span>';
}