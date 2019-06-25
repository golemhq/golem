
var TestCommon = new function(){

    this.DataTable = new function(){

        this.addRow = function(){
            let amountOfColumns = $("#dataTable thead tr th").length -1;
            let amountOfRows = $("#dataTable tbody tr").length;
            let newCells = "";
            for(var i = 0; i < amountOfColumns; i++){
                newCells += "<td> \
                                <div class='input-group'> \
                                    <input class='form-control' type='text'> \
                                </div> \
                            </td>";
            }

            $("#dataTable tbody").append(
                "<tr> \
                    <th scope='row' class='index'>"+(amountOfRows+1)+"</th> \
                    " + newCells + " \
                </tr>");
        }

        this.addColumn = function(){
            $("#dataTable thead tr").append(
                "<th> \
                    <div class='input-group'> \
                        <input class='form-control' type='text' onchange='dataTableHeaderInputChange()'> \
                    </div> \
                </th>"
            );

            $("#dataTable tbody tr").each(function(){
                $(this).append(
                    "<td> \
                        <div class='input-group'> \
                            <input class='form-control' type='text'> \
                        </div> \
                    </td>"
                );
            });
        }

        this.getData = function(){
            let testData = []
            let headerInputs = $("#dataTable thead input")
            let tableRows = $("#dataTable tbody tr");
            tableRows.each(function(){
                let currentRow = $(this);
                let rowCells = currentRow.find("td input");
                let rowDict = {}
                rowCells.each(function(i){
                    if($(headerInputs[i]).val().length > 0){
                        rowDict[$(headerInputs[i]).val()] = $(this).val();
                    }
                });
                if(!jQuery.isEmptyObject(rowDict)){
                    testData.push(rowDict)
                }
            });
            // empty values are allowed but only for one row of data
            let tempTestData = [];
            for(var i = 0; i <= testData.length - 1; i++){
                let allEmpty = true;
                for(key in testData[i]){
                    if(testData[i][key].length > 0){
                        allEmpty = false
                    }
                }
                if(!allEmpty){
                    tempTestData.push(testData[i])
                }
            }
            testData = tempTestData;
            return testData
        }

        this.getHeaders = function(){
            let headers = [];
            $("#dataTable thead input").each(function(){
                if($(this).val() != ''){
                    headers.push($(this).val())
                }
            });
            return headers;
        }
    }

    this.Header = new function(){

        this.startEditTestName = function(){
            $("#testNameInput input").val(Test.fullName);
            $("#testNameInput").show();
            $("#testName").hide();
            $("#testNameInput input").focus();
            $("#testNameInput input").unbind('blur');
            $("#testNameInput input").unbind('keyup');
            $("#testNameInput input").on('blur', function(e){
                TestCommon.Header.saveEdition();
            });
            $("#testNameInput input").on('keyup', function(e){
                if(e.keyCode == '13') $(this).blur();
            });
        };

        this.saveEdition = function(){
            let newTestNameValue = $("#testNameInput input").val().trim();
            if(newTestNameValue == Test.fullName){
                $("#testNameInput").hide();
                $("#testName").show();
                return
            }
            newTestNameValue = newTestNameValue.replace(' ', '_');

            let errors = Main.Utils.validateFilename(newTestNameValue);
            if(errors.length > 0){
                Main.Utils.displayErrorModal(errors);
                return
            }

            $.ajax({
                url: "/api/test/rename",
                data: JSON.stringify({
                     "project": Global.project,
                     "fullFilename": Test.fullName,
                     "newFullFilename": newTestNameValue,
                }),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                type: 'POST',
                success: function(result) {
                    if(result.errors.length == 0){
                        document.title = document.title.replace(Test.fullName, newTestNameValue);
                        Test.fullName = newTestNameValue;
                        $("#testNameInput input").val('');
                        $("#testNameInput").hide();
                        $("#testName").html(newTestNameValue).show();
                        let new_url = `/project/${Global.project}/test/${newTestNameValue}/`;
                        window.history.pushState("object or string", "", new_url);
                        Main.Utils.toast('success', 'File was renamed', 2000);
                    }
                    else{
                        result.errors.forEach(function(error){
                            Main.Utils.toast('error', error, 3000);
                        });
                        $("#testNameInput").hide();
                        $("#testName").show();
                    }
                },
             });
        };
    }

    this.Utils = new function(){

        this.convertTabToSpaces = function(cm) {
            if (cm.somethingSelected()) {
                cm.indentSelection("add");
            } else {
                cm.replaceSelection(cm.getOption("indentWithTabs")? "\t":
                Array(cm.getOption("indentUnit") + 1).join(" "), "end", "+input");
            }
        }
    }
}
