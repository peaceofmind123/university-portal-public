var courseSelect = document.querySelector('#id_course');
courseSelect.childNodes.forEach(function (option) {
    if(option.tagName === 'OPTION'){
        if(!option.selected){
            option.setAttribute('disabled','disabled');
        }
    }
});

var form = document.querySelector('form');
// form.addEventListener('submit',function (event) {
//     var req = new XMLHttpRequest();
//     req.open('POST','')
//     event.preventDefault();
// })
console.log(urlinfo);
console.log(username);
console.log(userinfo);
console.log(userinfo.username);