// Show the button when the user scrolls down 100px from the top of the document
window.addEventListener("scroll", function () {
    const toTopButton = document.getElementById("toTopButton");
    if (!toTopButton) return;
    const threshold = window.innerWidth <= 600 ? 50 : 100;
    if (document.body.scrollTop > threshold || document.documentElement.scrollTop > threshold) {
        toTopButton.style.display = "block";
    } else {
        toTopButton.style.display = "none";
    }
});
window.addEventListener("scroll", function () {
    const toBottomButton = document.getElementById("toBottomButton");
    const scrollableHeight =
        document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const currentScrollPosition = window.scrollY;
    if (!toBottomButton) return;

    // Show the button if not at the bottom of the page
    if (currentScrollPosition < scrollableHeight) {
        toBottomButton.style.display = "block";
    } else {
        toBottomButton.style.display = "none";
    }
});
// Scroll smoothly
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}
function scrollToBottom() {
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth"
    });
}