

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


// How to use the confirm modal:
// Call displayConfirmModal(title, message, callback),
//
// The confirmModalIsConfirmed function resets and hides the modal, then 
// runs the callback function.
// Pass an anonymous function as callback in order to include parameters with it,
// example:
// var callback = function(){
//     myCustomFunction(param1, param2);
// }
function displayConfirmModal(title, message, callback){
    $("#confirmModal .modal-title").html(title);
    $("#confirmModal .modal-body").html(message);
    $("#confirmModal button.confirm").click(function(){
        confirmModalIsConfirmed(callback);
    })
    $("#confirmModal").modal("show");
}

function confirmModalIsConfirmed(callback){
    $("#confirmModal .modal-title").html('');
    $("#confirmModal .modal-body").html('');
    $("#confirmModal button.confirm").unbind('click');
    $("#confirmModal").modal("hide");
    callback();
}


// How to use the prompt modal:
// Call displayPromptModal(title, description, inputValue, callback),
//
// When the 'Save' button is clicked, the callback function is called.
// Pass an anonymous function as callback in order to include parameters with it,
// example:
// var callback = function(){
//     myCustomFunction(param1, param2);
// }
function displayPromptModal(title, description, inputValue, callback){
    $("#promptModal .modal-title").html(title);
    $("#promptModal .modal-body .description").html(description);
    $("#promptModal .modal-body input").val(inputValue);
    $("#promptModal button.confirm").click(function(){
        callback();
    })
    $("#promptModal").modal("show");
    $('#promptModal').on('shown.bs.modal', function () {
        $('#promptModalInput').focus();
    });
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

    this.animateProgressBar = function(bar, percentage){
        setTimeout(function(){
            bar.css('width', percentage+'%');
        }, 100);
    }
}


var reportUtils = new function(){

    this.generateProgressBars = function(){
        var progressBars = "\
            <div class='progress'>\
                <div aria-valuenow='20' style='width: 100%;' \
                    class='progress-bar pending' data-transitiongoal='20'></div>\
                <div aria-valuenow='10' style='width: 0%;' \
                    class='progress-bar progress-bar-danger fail-bar' \
                    data-transitiongoal='10'></div>\
                <div aria-valuenow='20' style='width: 0%;' \
                    class='progress-bar ok-bar' data-transitiongoal='20'></div>\
            </div>";
        return progressBars
    }
}




