
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
