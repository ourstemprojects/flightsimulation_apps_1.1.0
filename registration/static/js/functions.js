
    // DISPLAY / STORE SELECTED IMAGE FILENAME
    function getFileName(id, file) {

        // CLEAR SELECTED IMAGE HIGHLIGHTING
        for (var i = 1; i < 22; i++) {
            document.getElementById('img'+i).style.borderColor = '#ccc'; 
        }
        // STORE FILENAME / HIGHLIGHT SELECTION
        document.getElementById('image_name').value = file;
        document.getElementById(id).style.border = '1px solid red'; 
    }