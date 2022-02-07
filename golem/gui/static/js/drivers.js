
$(document).ready(function() {
    Drivers.getDriverFiles()
});


const Drivers = new function(){

    this.getDriverFiles = function(){
        xhr.get('/api/drivers/files', {}, driverFiles => {
            if(driverFiles.length) {
                driverFiles.forEach(filename => {
                    let li = $(`
                        <li class="tree-element file" filename="${filename}">
                            <span>${filename}</span>
                            <span class="file-menu pull-right">
                                <button class="file-menu-button delete-button" onclick="Drivers.deleteFileConfirm(this)"><i class="glyphicon glyphicon-trash"></i></button>
                            </span
                        </li>`);
                    $('#rootFolderContent').append(li);
                })
            } else {
                $('#rootFolderContent').append('<li>no drivers</li>');
            }
        })
    }

    this.deleteFileConfirm = function(elem) {
        let filename = $(elem).closest('.file').attr('filename');
        Main.Utils.displayConfirmModal('Delete File', `Delete file <strong>${filename}</strong>?`, () => {
            xhr.delete('/api/drivers/delete', { filename }, errors => {
                if(errors.length) {
                    errors.forEach(error => {
                        Main.Utils.toast('error', `Error: ${error}`, 4000)
                    })
                } else {
                    location.reload();
                }
            })
        });
    }

    this.update = function(driverName) {
        xhr.post('/api/drivers/update', { driverName }, errors => {
            if(errors.length) {
                errors.forEach(error => {
                    Main.Utils.toast('error', `Error: ${error}`, 4000)
                })
            } else {
                location.reload();
            }
        })
    }
}
