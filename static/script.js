function myFunction() {
    var x = document.getElementById("myTopnav");
    if (x.className === "topnav") {
      x.className += " responsive";
    } else {
      x.className = "topnav";
    }
}

async function deleteSubject(subjectid, subjectname) {
  var del = confirm("Are you sure want to delete subject "+subjectname);
  if (del){
    const res = await fetch("/admin/delete/" + subjectid, {
      method: "DELETE",
    }).then((response) => response.json());
    window.location.reload();
    }
  }

  async function deleteStudent(id) {
    var del = confirm("Are you sure want to delete student "+id);
    if (del){
      const res = await fetch("/admin/student/delete/" + id, {
        method: "DELETE",
      }).then((response) => response.json());
      window.location.reload();
      }
    }


