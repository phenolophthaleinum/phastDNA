// document.addEventListener('DOMContentLoaded', (event) => {
console.log('renderer hello');
const {ipcRenderer} = require('electron');
var debug_btn = null;

// Communicate with main process
const dialogButtons = document.querySelectorAll('.btn-primary-dialog');
console.log(dialogButtons);
dialogButtons.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
        var btn_copy = btn;
        console.log('clicked dialog btn')
        ipcRenderer.send('open-dir-dialog');
    });
});
ipcRenderer.on('selected-dir', function (e, path) {
    var input_text_field = document.querySelector('.btn-primary-dialog:focus').previousElementSibling;
    input_text_field.value = path !== undefined ? path : '';
    // var tmp_arr_name = btn.id.split('-').slice(0,-1);
    // var input_text_field_name = tmp_arr_name.join('-');
    // console.log(input_text_field_name);
    // console.log(path);
    // var input_text_field = document.getElementById(input_text_field_name);
    // input_text_field.value = path;
})
// });