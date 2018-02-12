document.getElementById("nav-expand-btn").addEventListener("click", expand);
function expand() {
    var btn = document.getElementById("nav-expand-arrow");
    if (btn.classList.contains("fa-chevron-left")) {
        btn.classList.remove("fa-chevron-left");
        btn.classList.add("fa-chevron-right");
        document.getElementById("nav").style.display = "none";
        document.getElementById("nav-menu").style.width = "auto";
        document.getElementById("header").style.width = "100%";
        document.getElementById("content").style.width = "100%";
    } else if (btn.classList.contains("fa-chevron-right")) {
        btn.classList.remove("fa-chevron-right");
        btn.classList.add("fa-chevron-left");
        document.getElementById("nav").style.display = "block";
        document.getElementById("nav-menu").style.width = "20%";
        document.getElementById("header").style.width = "80%";
        document.getElementById("content").style.width = "80%";
    }
}
