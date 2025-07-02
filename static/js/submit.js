document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("message-form");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const fd = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: fd,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.error) {
          showFlash(data.error);
          return;
        }

        // 构造新留言
        const div = document.createElement("div");
        div.className = "message-bubble";
        div.innerHTML = `
          <div class="message-header">
            <strong>${data.username}</strong>
            <span class="timestamp">${data.timestamp.slice(0, 16)}</span>
          </div>
          <div class="message-text">${data.text}</div>
        `;
        document.querySelector(".showmessage").prepend(div);
        form.reset();

      })
      .catch(() => showFlash("网络错误，请重试"));
  });

  function showFlash(msg) {
    let popup = document.getElementById("flash-popup");
    if (!popup) {
      popup = document.createElement("div");
      popup.id = "flash-popup";
      popup.className = "flash-popup";
      document.body.appendChild(popup);
    }
    popup.innerHTML = `<p>${msg}</p>`;
    popup.classList.remove("hide");

    setTimeout(() => {
      popup.classList.add("hide");
    }, 3000);
  }
});