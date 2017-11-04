

window.onload = function () {

     $('#sidebarCollapse').on('click', function () {
         //$('#sidebar').toggleClass('active');
         $('#wrapper').toggleClass('sidebar-collapsed');
         if($('#wrapper').hasClass('sidebar-collapsed')){
            //document.cookie = "sidebarCollapsed=true";
            localStorage.setItem('sidebarCollapse', true);
         }
         else{
            // document.cookie = "sidebarCollapsed=false";
            localStorage.setItem('sidebarCollapse', false);
         }
         

     });
 };




function passIcon(){
    return '<span class="passed-green"><span class="glyphicon glyphicon-ok-circle" aria-hidden="true"></span></span>'
}


function failIcon(){
    return '<span class="failed-red"><span class="glyphicon glyphicon-remove-circle" aria-hidden="true"></span></span>';
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

    this.toast = function(type, msg, duration){
        toastr.options = {
            "positionClass": "toast-top-center",
            "timeOut": duration.toString(),
            "hideDuration": "100"
        }
        if(type == 'success')
            toastr.success(msg)
        else if(type == 'error')
            toastr.error(msg)
        else if(type == 'info')
            toastr.info(msg)
    }



    this.displayErrorModal = function(errors){
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
    // When the Confirm Modal is confirmed the callback is called.
    // Pass an anonymous function as callback in order to include parameters with it,
    // example:
    // var callback = function(){
    //     myCustomFunction(param1, param2);
    // }
    this.displayConfirmModal = function(title, message, callback){
        $("#confirmModal .modal-title").html(title);
        $("#confirmModal .modal-body").html(message);
        $("#confirmModal button.confirm").click(function(){
            $("#confirmModal .modal-title").html('');
            $("#confirmModal .modal-body").html('');
            $("#confirmModal button.confirm").unbind('click');
            $("#confirmModal").modal("hide");
            callback();
        })
        $("#confirmModal").modal("show");
        $('#confirmModal').on('shown.bs.modal', function () {
            $("#confirmModal button.confirm").focus();
        });
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
    this.displayPromptModal = function(title, description, inputValue, inputPlaceholder, callback){
        $("#promptModal .modal-title").html(title);
        $("#promptModal .modal-body .description").html(description);
        $("#promptModal .modal-body input").val(inputValue);
        
        $("#promptModal").modal("show");
        $('#promptModal').on('shown.bs.modal', function () {
            $('#promptModalInput').focus();
        });

        var sendValue = function(){
            var sentValue = $("#promptModalInput").val();
            callback(sentValue);
            $("#promptModal").modal("hide");
            $("#prompSaveButton").unbind('click');
        }

        $("#promptModal button.confirm").click(function(){
            sendValue();
        })
    }


    // How to use the select prompt modal:
    // Call displaySelectPromptModal(title, description, options, buttonLabel, callback),
    //
    // When the user selects an option from the select, the callback function is called.
    // Pass an anonymous function as callback in order to include parameters with it,
    // example:
    // var callback = function(){
    //     myCustomFunction(param1, param2);
    // }
    this.displaySelectPromptModal = function(title, description, options, buttonLabel, callback){
        buttonLabel = buttonLabel || 'Continue';
        $("#selectPromptModal .modal-title").html(title);
        $("#selectPromptModal .modal-body .description").html(description);
        
        $("#selectPromptContinueButton").html(buttonLabel);

        $("#selectPromptSelect").html('');
        $.each(options, function(i){
            var itemval = "<option value='"+options[i]+"'>"+options[i]+"</option>";
            $("#selectPromptSelect").append(itemval)
        });
        $("#selectPromptModal button.confirm").focus();
        $("#selectPromptModal").modal("show");
        $('#selectPromptModal').on('shown.bs.modal', function () {
            $("#selectPromptModal button.confirm").focus();
        });

        var confirm = function(){
            var selectedVal = $("#selectPromptSelect").val();
            callback(selectedVal);
            $("#selectPromptModal").modal("hide");
            $("#selectPromptSelect").unbind('change');
            $("#selectPromptSelect").unbind('change');
            $("#selectPromptModal button.confirm").unbind('click');
        }

        $("#selectPromptModal button.confirm").click(function(){
            confirm();
        })
    }


}


var reportUtils = new function(){

    this.generateProgressBars = function(){
        var progressBars = "\
            <div class='progress'>\
                <div aria-valuenow='20' style='width: 100%;' \
                    class='progress-bar pending-grey-background pending' data-transitiongoal='20'></div>\
                <div aria-valuenow='10' style='width: 0%;' \
                    class='progress-bar failed-red-background fail-bar' \
                    data-transitiongoal='10'></div>\
                <div aria-valuenow='20' style='width: 0%;' \
                    class='progress-bar passed-green-background ok-bar' data-transitiongoal='20'></div>\
            </div>";
        return progressBars
    }

    this.expandImg = function(e){
        $("#expandedScreenshot").attr('src', e.srcElement.src);
        $("#screenshotModal").modal('show');
    }
}




