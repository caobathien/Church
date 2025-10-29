document.addEventListener("DOMContentLoaded", function () {
  const images = [
    "/static/img/church2.png",
    "/static/img/church3.png",
    "/static/img/church4.png",
    "/static/img/church5.png"
  ];

  let index = 0;
  const img = document.getElementById("churchImage");

  if (img) {
    function changeImage() {
      index = (index + 1) % images.length;
      img.style.opacity = 0; // hiệu ứng mờ dần
      setTimeout(() => {
        img.src = images[index];
        img.style.opacity = 1;
      }, 500);
    }

    // Chuyển ảnh mỗi 3 giây
    setInterval(changeImage, 3000);
  }
});
