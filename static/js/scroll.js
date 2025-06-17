// 保存滚动位置
document.addEventListener("DOMContentLoaded", function () {
  // 如果 localStorage 有滚动位置，就恢复它
  const savedY = localStorage.getItem("scrollY");
  if (savedY) {
    window.scrollTo(0, parseInt(savedY));
    localStorage.removeItem("scrollY");
  }

  // 表单提交前，保存当前 scrollY 到 localStorage
  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", function () {
      localStorage.setItem("scrollY", window.scrollY);
    });
  }
});


document.addEventListener("DOMContentLoaded", function () {
  const flash = document.getElementById("flash-popup");
  if (flash) {
    setTimeout(() => {
      flash.classList.add("hide");
    }, 3000);  // 显示3秒后自动隐藏
  }
});
