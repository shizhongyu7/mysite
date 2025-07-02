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
        if (data.error) return alert(data.error);

        // 构造新留言
        const div = document.createElement("div");
        div.className = "message-bubble";
        div.innerHTML = `
          <div class="message-header">
            <strong>${data.username}</strong>
            <span class="tamp">${data.timestamp.slice(0, 16)}</span>u
          </div>
          <div class="message-text">${data.text}</div>
        `;
        document.querySelector(".showmessage").prepend(div);
        form.reset();
      })
      .catch(() => alert("Network error"));
  });
});