document.addEventListener("DOMContentLoaded", function() {
  const form = document.getElementById("message-form");
  form.addEventListener("submit", function(e) {
    e.preventDefault();

    const formData = new FormData(form);
    fetch(form.action, {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      }
    })
    .then(res => {
      if (!res.ok) return res.json().then(err => { throw err; });
      return res.json();
    })
    .then(data => {
      const msg = document.createElement("div");
      msg.className = "message-bubble";
      msg.innerHTML = `
        <div class="message-header">
          <strong>${data.username}</strong>
          <span class="timestamp">${data.timestamp.slice(0, 16)}</span>
        </div>
        <div class="message-text">${data.text}</div>
      `;
      document.querySelector(".showmessage").prepend(msg);
      form.reset();
    })
    .catch(err => {
      alert(err.error || "提交失败");
    });
  });
});