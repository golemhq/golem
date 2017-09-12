

function displayErrorModal(errors){
    var ulContent = '';
    for(e in errors){
        ulContent += "<li>"+errors[e]+"</li>";
    } 
    $("#errorList").html(ulContent);
    $("#errorModal").modal("show");
    window.setTimeout(function(){
        $("#errorModal .dismiss-modal").focus();
    }, 500);
}


function passIcon(){
    return '<span class="pass-icon"><span class="glyphicon glyphicon-ok-circle" aria-hidden="true"></span></span>'
}


function failIcon(){
    return '<span class="fail-icon"><span class="glyphicon glyphicon-remove-circle" aria-hidden="true"></span></span>';
}


const utils = new function(){

    this.getDateTimeFromTimestamp = function(timestamp){
        var sp = timestamp.split('.');
        var dateTimeString = sp[0]+'/'+sp[1]+'/'+sp[2]+' '+sp[3]+':'+sp[4];
        return dateTimeString
    }
}