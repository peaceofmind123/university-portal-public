var idfield = document.getElementById('id_profilepic');
var coursepic = document.querySelector('.coursepicture');
var form = document.querySelector('form');

function preview(file){
    var reader = new FileReader();
    if(file){
        reader.readAsDataURL(file);
    }
    reader.addEventListener('load',function (ev) {
        coursepic.src = reader.result;
    });
}

if(idfield.files) {
    preview(idfield.files[0]);
}

idfield.addEventListener('change',function (event) {
    var file = this.files[0];
    preview(file);
});
