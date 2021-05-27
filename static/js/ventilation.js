const send = document.getElementById("send")

// disapper temperature form unless "measure"
// var rad = document.getElementsByName("radAnswer")
// var prev = null
// for (var i = 0; i < rad.length; i++) {
//     rad[i].addEventListener('change', function() {
//         // (prev) ? console.log(prev.value): null;
//         if (this !== prev) {
//             prev = this
//         }
//         if (this.value === "measure"){
//             document.getElementById("temp_div").style.display = "block"
//             document.getElementById("temp").required = true
//             document.getElementById("ventil_div").style.display = "none"
//         }
//         else if(this.value == "arrive"){
//             document.getElementById("temp_div").style.display = "none"
//             document.getElementById("temp").required = false
//             document.getElementById("ventil_div").style.display = "none"
//         }
//         else{
//             document.getElementById("temp_div").style.display = "none"
//             document.getElementById("temp").required = false
//             document.getElementById("ventil_div").style.display = "block"
//         }
//         console.log(this.value)
//     });
// }


var ventil = document.getElementById("ventil_table")
var all_ventil_s = document.getElementsByName("ventil_s")
var all_ventil_e = document.getElementsByName("ventil_e")
var part2_block = document.getElementById("part2")
var pre_ventil_s = [""]

function add_eventlister_to_ventil(){
    all_ventil_s = document.getElementsByName("ventil_s")
    console.log(all_ventil_s.length)
    for (var i = 0; i < all_ventil_s.length; i++){
        ventil_s = document.getElementById("ventil_s_" + i.toString())
        ventil_s.addEventListener('change', function(){
            idx = parseInt(this.id.split('_')[2])
            console.log(pre_ventil_s)
            if (pre_ventil_s[idx] === ""){
                console.log(this.value)
                console.log(idx)
                pre_ventil_s[idx] = this.value.toString()
                pre_ventil_s.push("")

                var today = new Date()
                h_m = this.value.split(":")
                today.setHours(h_m[0])
                today.setMinutes(h_m[1])
                today.setMinutes(today.getMinutes() + 10)
                ventil_e = document.getElementById("ventil_e_" + idx.toString())
                ventil_e.value = ("00" + today.getHours().toString()).slice(-2) + ":" + ("00" + today.getMinutes().toString()).slice(-2)
                ventil = document.getElementById("ventil_table")
    
                var ventil_s_element = document.createElement("input")
                ventil_s_element.setAttribute("type", "time")
                ventil_s_element.setAttribute("name", "ventil_s")
                ventil_s_element.setAttribute("class", "ventil")
                ventil_s_element.setAttribute("id", "ventil_s_" + (idx + 1).toString())
                var ventil_e_element = document.createElement("input")
                ventil_e_element.setAttribute("type", "time")
                ventil_e_element.setAttribute("name", "ventil_e")
                ventil_e_element.setAttribute("class", "ventil")
                ventil_e_element.setAttribute("id", "ventil_e_" + (idx + 1).toString())
                var del_element = document.createElement("input")
                del_element.setAttribute("type", "checkbox")
                del_element.setAttribute("id", "del_" + (idx + 1).toString())
                del_element.setAttribute("value", "del_" + (idx + 1).toString())
                del_element.setAttribute("name", "ventil_del")
                
    
                new_row = ventil.insertRow()
                var cell_0 = new_row.insertCell()
                var cell_1 = new_row.insertCell()
                var cell_2 = new_row.insertCell()
                var cell_3 = new_row.insertCell()
                cell_0.appendChild(ventil_s_element)
                cell_1.innerHTML = "-"
                cell_2.appendChild(ventil_e_element)
                cell_3.appendChild(del_element)
                add_eventlister_to_ventil()
                console.log(pre_ventil_s)
            }
        })
    }
}


for (var i = 0; i < VENTILS.length; i++){
    ventil_s = document.getElementById("ventil_s_" + i.toString())
    h_m = VENTILS[i][0].split(":")
    ventil_s.value = h_m[0] + ":" + h_m[1]
    ventil_e = document.getElementById("ventil_e_" + i.toString())
    h_m = VENTILS[i][1].split(":")
    ventil_e.value = h_m[0] + ":" + h_m[1]

    pre_ventil_s[i] = ventil_s.value.toString()
    pre_ventil_s.push("")

    var ventil_s_element = document.createElement("input")
    ventil_s_element.setAttribute("type", "time")
    ventil_s_element.setAttribute("name", "ventil_s")
    ventil_s_element.setAttribute("class", "ventil")
    ventil_s_element.setAttribute("id", "ventil_s_" + (i + 1).toString())
    var ventil_e_element = document.createElement("input")
    ventil_e_element.setAttribute("type", "time")
    ventil_e_element.setAttribute("name", "ventil_e")
    ventil_e_element.setAttribute("class", "ventil")
    ventil_e_element.setAttribute("id", "ventil_e_" + (i + 1).toString())
    var del_element = document.createElement("input")
    del_element.setAttribute("type", "checkbox")
    del_element.setAttribute("id", "del_" + (i + 1).toString())
    del_element.setAttribute("value", "del_" + (i + 1).toString())
    del_element.setAttribute("name", "ventil_del")
    
    new_row = ventil.insertRow()
    var cell_0 = new_row.insertCell()
    var cell_1 = new_row.insertCell()
    var cell_2 = new_row.insertCell()
    var cell_3 = new_row.insertCell()
    cell_0.appendChild(ventil_s_element)
    cell_1.innerHTML = "-"
    cell_2.appendChild(ventil_e_element)
    cell_3.appendChild(del_element)
} 

add_eventlister_to_ventil()
console.log(pre_ventil_s)