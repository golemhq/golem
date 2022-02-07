
var TestCommon = new function(){

    this.DataSource = new function() {

        this.loadData = function(csvData, jsonData, internalData) {
            if(csvData.length) {
                if(!this.DataTable.isPresent()) {
                    this.addDataSourceCsv();
                }
                this.DataTable.loadTable(csvData);
            } else if(jsonData.length) {
                if(!this.JsonEditor.isPresent()) {
                    this.addDataSourceJson();
                }
                this.JsonEditor.loadJson(jsonData);
            } else if(internalData.length) {
                if(!this.InternalEditor.isPresent()) {
                    this.addDataSourceInternal();
                }
                this.InternalEditor.load(internalData);
            }
        }

        this.getData = function() {
            let data = {
                csv: null,
                json: null,
                internal: null
            }
            if(this.DataTable.isPresent()) {
                data.csv = this.DataTable.getData()
            }
            if(this.JsonEditor.isPresent()) {
                data.json = this.JsonEditor.getData()
            }
            if(this.InternalEditor.isPresent()) {
                data.internal = this.InternalEditor.getData()
            }
            return data
        }

        this.addDataSourceCsv = function() {
            let csvTable = $(`
                <div id="dataTableOuterContainer">
                    <h4 style="display: inline-block">CSV</h4>
                    <div class="inline-remove-icon">
                        <a href="javascript:void(0)" onclick="TestCommon.DataSource.deleteCSVTable()">
                            <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>
                        </a>
                    </div>
                    <div id="dataTableContainer">
                        <table class="table table-bordered table-condensed" id="dataTable">
                            <thead>
                                <tr>
                                    <th class="index">#</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                    <div style="display: table-cell; position: relative;">
                        <a href="javascript:void(0)" onclick="TestCommon.DataSource.DataTable.addColumn();">
                            <img src="/static/img/plus_sign.png" class="add-new-icon" style="margin-left: 5px;">
                        </a>
                    </div>
                    <div class="text-right" style="width: 100%">
                        <a href="javascript:void(0)" onclick="TestCommon.DataSource.DataTable.addRow();">
                            <img src="/static/img/plus_sign.png" class="add-new-icon" style="margin-right: 30px;">
                        </a>
                    </div>
                </div>`);
            $('#dataContainerContainer').append(csvTable);
            this.DataTable.addColumns(3);
            this.DataTable.addRows(3);
            $("#dataSourceSelector").hide();
        }

        this.addDataSourceJson = function() {
            let jsonEditor = $(`
                <div id="jsonEditorContainerContainer">
                    <h4 style="display: inline-block">JSON</h4>
                    <div class="inline-remove-icon">
                        <a href="javascript:void(0)" onclick="TestCommon.DataSource.deleteJsonEditor()">
                            <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>
                        </a>
                    </div>
                    <div class="codeEditorContainer" id="jsonEditorContainer"></div>
                </div>`);
            $('#dataContainerContainer').append(jsonEditor);

            let editor = CodeMirror($("#jsonEditorContainer")[0], {
                value: '',
                mode: "application/ld+json",
                lineNumbers: true,
                styleActiveLine: true,
                matchBrackets: true,
                autoCloseBrackets: true,
                lineWrapping: true
            });

            this.JsonEditor.editor = editor;
            $("#dataSourceSelector").hide();
        }

        this.addDataSourceInternal = function() {
            let internalEditor = $(`
                <div id="internalEditorContainerContainer">
                    <h4 style="display: inline-block">Internal</h4>
                    <div class="inline-remove-icon">
                        <a href="javascript:void(0)" onclick="TestCommon.DataSource.deleteInternalEditor()">
                            <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>
                        </a>
                    </div>
                    <div class="codeEditorContainer" id="internalEditorContainer"></div>
                </div>`);
            $('#dataContainerContainer').append(internalEditor);

            let editor = CodeMirror($("#internalEditorContainer")[0], {
                value: 'data = []',
                mode: 'python',
                lineNumbers: true,
                styleActiveLine: true,
                matchBrackets: true,
                indentUnit: 4,
                indentWithTabs: false,
                extraKeys: {
                    Tab: TestCommon.Utils.convertTabToSpaces
                }
            });

            this.InternalEditor.editor = editor;
            $("#dataSourceSelector").hide();
        }

        this.deleteCSVTable = function() {
            this.deleteDataSection('Delete CSV table?', $('#dataTableOuterContainer'));
        }

        this.deleteJsonEditor = function() {
            this.deleteDataSection('Delete JSON data?', $('#jsonEditorContainerContainer'));
        }

        this.deleteInternalEditor = function() {
            this.deleteDataSection('Delete Internal data?', $('#internalEditorContainerContainer'));
        }

        this.deleteDataSection = function(msg, container) {
             Main.Utils.displayConfirmModal(msg, '', () => {
                container.remove();
                $("#dataSourceSelector").show();
                this.markAsUnsavedChanges();
            });
        }

        this.markAsUnsavedChanges = function() {
            if(typeof Test != 'undefined') {
                Test.unsavedChanges = true;
            }
            if(typeof TestCode !== 'undefined') {
                TestCode.unsavedChanges = true;
            }
        }


        this.DataTable = new function() {

            this.loadTable = function(csvValues) {
                let numberOfColumns = this.numberOfColumns();
                let numberOfRows = this.numberOfRows();
                let headers = Object.keys(csvValues[0]);

                // add extra columns and rows if needed
                if(csvValues.length > numberOfRows) {
                    this.addRows(csvValues.length - numberOfRows);
                }
                if(headers.length > numberOfRows) {
                    this.addColumns(headers.length - numberOfRows);
                }
                // load headers
                let index = 0
                for (const i in headers) {
                    this.setHeader(index, headers[i]);
                    index++;
                }
                // load rows
                for(let i=0; i<csvValues.length; i++) {
                    this.setRow(i, csvValues[i])
                }
            }

            this.numberOfColumns = function() {
                return $("#dataTable thead tr th").length -1;
            }

            this.numberOfRows = function() {
                return  $("#dataTable tbody tr").length;
            }

            this.addRows = function(n) {
                for(let i=1; i<=n; i++) {this.addRow()}
            }

            this.addColumns = function(n) {
                for(let i=1; i<=n; i++) {this.addColumn()}
            }

            this.addRow = function(){
                let numberOfColumns = this.numberOfColumns();
                let numberOfRows = this.numberOfRows();
                let newCells = "";
                for(var i = 0; i < numberOfColumns; i++){
                    newCells += "<td> \
                                    <div class='input-group'> \
                                        <input class='form-control' type='text'> \
                                    </div> \
                                </td>";
                }

                $("#dataTable tbody").append(
                    "<tr> \
                        <th scope='row' class='index'>"+(numberOfRows+1)+"</th> \
                        " + newCells + " \
                    </tr>");
            }

            this.addColumn = function(){
                $("#dataTable thead tr").append(
                    "<th> \
                        <div class='input-group'> \
                            <input class='form-control' type='text' onchange=''> \
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

            this.isPresent = function() {
                return $("#dataTableOuterContainer").length > 0;
            }

            this.getData = function() {
                let testData = [];
                let headerInputs = $("#dataTable thead input");
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

            this.setHeader = function(index, value) {
                $("#dataTable thead input")[index].value = value;
            }

            this.setRow = function(rowIndex, row) {
                let columnIndex = 0
                for (const i in row) {
                    this.setCell(rowIndex, columnIndex, row[i]);
                    columnIndex++;
                }
            }

            this.setCell = function(rowIndex, columnIndex, cellValue) {
                $("#dataTable tbody tr").eq(rowIndex).find("td input")[columnIndex].value = cellValue;
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

        this.JsonEditor = new function() {

            this.editor;

            this.isPresent = function() {
                return $("#jsonEditorContainer").length > 0;
            }

            this.loadJson = function(json) {
                this.editor.setValue(json)
            }

            this.getData = function() {
                return this.editor.getValue();
            }
        }

        this.InternalEditor = new function() {

            this.editor;

            this.isPresent = function() {
                return $("#internalEditorContainerContainer").length > 0;
            }

            this.load = function(data) {
                this.editor.setValue(data)
            }

            this.getData = function() {
                return this.editor.getValue();
            }
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
