

var selectors = [
    'id',
    'name',
    'text',
    'link_text',
    'partial_link_text',
    'css',
    'xpath',
    'tag_name',];

$(document).ready(function() {      

    startAllSelectorInputAutocomplete();

    $(".element-name").keyup(function(){
        $(this).parent().parent().parent().find('.element-display-name').val($(this).val());
    });

});



function startAllSelectorInputAutocomplete(){
    var lookup = []

    for(sel in selectors){
        lookup.push({
            'value': selectors[sel],
            'data': selectors[sel]
        })        
    }

    $(".element-selector").each(function(){

        autocomplete = $(this).autocomplete({
            lookup: lookup,
            minChars: 0,
            onSelect: function (suggestion) {
                //stepFirstInputChange($(this));
            },
            onSearchStart: function () {},
            beforeRender: function (container) {},
            onSearchComplete: function (query, suggestions) {
            }
        });
    })

}

function addPageObjectInput(){
    $("#elements").append(
        "<div class='element col-md-12'> \
            <div class='col-sm-3'> \
                <div class='input-group'> \
                    <input type='text' class='form-control element-name' value='' \
                        placeholder='name'> \
                </div> \
            </div> \
            <div class='col-sm-3'> \
                <div class='input-group'> \
                    <input type='text' class='form-control element-selector' \
                        value='' placeholder='selector'> \
                </div> \
            </div> \
            <div class='col-sm-3'> \
                <div class='input-group'> \
                    <input type='text' class='form-control element-value' \
                        value='' placeholder='value'> \
                </div> \
            </div> \
            <div class='col-sm-3'> \
                <div class='input-group'> \
                    <input type='text' class='form-control element-display-name' \
                        value='' placeholder='display name'> \
                </div> \
            </div> \
        </div>");

    startAllSelectorInputAutocomplete();

    $(".element-name").keyup(function(){
        $(this).parent().parent().parent().find('.element-display-name').val($(this).val());
    });
}


function savePageObject(){

    var elements = [];

    $(".element").each(function(){
        elements.push({
            'name': $(this).find('.element-name').val(),
            'selector': $(this).find('.element-selector').val(),
            'value': $(this).find('.element-value').val(),
            'display_name': $(this).find('.element-display-name').val()
        });
    });

    $.ajax({
        url: "/save_page_object/",
        data: JSON.stringify({
                "project": project,
                "pageObjectName": pageObjectName,
                "elements": elements
            }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        success: function(data) {
        },
        error: function() {
        }
    });
}
