function myFunction() {
    var input, filter, table, tr, td, td2, i, txtValue, txtValue2;
    input = document.getElementById("inputbox");
    filter = input.value.toUpperCase();
    table = document.getElementById("timetable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[3];
      td2 = tr[i].getElementsByTagName("td")[1];
      if (td) {
        txtValue = td.textContent || td.innerText;
        txtValue2 = td2.textContent || td2.innerText;
        if (txtValue2 == "Calling at:" && txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i-1].style.display = "";
          tr[i].style.display = "";
        }
        else if (txtValue2 == "Calling at:") {
          tr[i].style.display = tr[i-1].style.display;
        }
        else if (txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        }
        else {
          tr[i].style.display = "none";
        }
      }       
    }
}
