function w3_open() {
    $("#ptMain").removeClass("slide-left").addClass("slide-right");
    $("#ptSidebar").removeClass("invisible").addClass("visible");
    $("#ptHamburger").removeClass("visible").addClass("invisible");
}
function w3_close() {
    $("#ptMain").removeClass("slide-right").addClass("slide-left");
    $("#ptSidebar").removeClass("visible").addClass("invisible");
    $("#ptHamburger").removeClass("invisible").addClass("visible");
}