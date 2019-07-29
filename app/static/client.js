var el = x => document.getElementById(x);

function showPicker() {
  el("file-input").click();
}

function showPicked(input) {
  el("upload-label").innerHTML = input.files[0].name;
  var reader = new FileReader();
  reader.onload = function(e) {
    el("image-picked").src = e.target.result;
    el("image-picked").className = "";
  };
  reader.readAsDataURL(input.files[0]);
}

function show_button(input){
  var x = document.getElementById(input)
         if(x.style.display == 'none'){
          x.style.display = "block";
         }
         else{
          x.style.display = "none";
         }
}

function analyze() {
  var uploadFiles = el("file-input").files;
  var file = uploadFiles[0]

  if (uploadFiles.length !== 1){
    alert("Please select a file to analyze!");
  } 

  el("analyze-button").innerHTML = "Analyzing...";
  var xhr = new XMLHttpRequest();
  var loc = window.location;
  xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`,
    true);
  xhr.onerror = function() {
    alert(xhr.responseText);
    el("analyze-button").innerHTML = "Analyze";
  };
  xhr.onload = function(e) {
    if (this.readyState === 4) {
      var response = JSON.parse(e.target.responseText);
      el("result-label").innerHTML = `Result = ${response["result"]}`;
      show_button('right');
      show_button('wrong');
      var selectobject = document.getElementById('select-menu')
      for (var i=0; i<selectobject.length; i++){
        if (selectobject.options[i].value ==  response['result'])
           selectobject.remove(i);
        }
    }
    el("analyze-button").innerHTML = "Analyze";
  };

  var fileData = new FormData();
  fileData.append("file", file)
  xhr.send(fileData);
}


function submit(){
  var uploadFiles = el("file-input").files;
  el("right-button").innerHTML = "Submitting...";
  var pred = el('result-label').textContent.split('Result = ')[1];
  var xhr = new XMLHttpRequest();
  var loc = window.location;
  xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/submit`,
  true);

  xhr.onerror = function() {
    alert(xhr.responseText);
  };
  xhr.onload = function(e) {
    if (this.readyState === 4) {
    }
    el("right-button").innerHTML = "Right";
  };

  var fileData = new FormData();
  fileData.append(pred, uploadFiles[0]);
  fileData.append('pre', 'T')
  xhr.send(fileData);
}


function submit_wrong(){
  var newpred = el("select-menu").value;
  var uploadFiles = el("file-input").files
  el("submit-button").innerHTML = "Submitting...";
  var xhr = new XMLHttpRequest();
  var loc = window.location;
  xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/submit`,true);
  xhr.onerror = function() {
    alert(xhr.responseText);
  };
  xhr.onload = function(e) {
    if (this.readyState === 4) {
    }
    el("submit-button").innerHTML = "Submit";
  };

  var fileData = new FormData();
  fileData.append(newpred, uploadFiles[0]);
  fileData.append('pre','F');
  xhr.send(fileData);
  
}