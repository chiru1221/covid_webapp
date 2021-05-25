const send = document.getElementById("send")

// validate temperature value
var temp = document.getElementById("temp")
var temp_prev = null

temp.addEventListener('change', function(){
    if (this !== temp_prev){
        temp_prev = this
    }
    value_float = parseFloat(this.value)
    if (isNaN(value_float)){
        document.getElementById("temp_warning").style.display = "block"
        document.getElementById("date").style.display = "none"
        send.disabled = true
    }
    console.log(value_float)
})

// disapper temperature form unless "measure"
var rad = document.getElementsByName("radAnswer")
var prev = null
for (var i = 0; i < rad.length; i++) {
    rad[i].addEventListener('change', function() {
        // (prev) ? console.log(prev.value): null;
        if (this !== prev) {
            prev = this
        }
        if (this.value === "measure"){
            document.getElementById("temp_div").style.display = "block"
            document.getElementById("repair_date").style.display = "none"
            document.getElementById("temp").required = true
        }
        else if (this.value === "arrive"){
            document.getElementById("temp_div").style.display = "none"
            document.getElementById("repair_date").style.display = "none"
            document.getElementById("temp").required = false
        }
        else{
            document.getElementById("temp_div").style.display = "none"
            document.getElementById("repair_date").style.display = "block"
            document.getElementById("temp").required = false
        }
        console.log(this.value)
    });
}


