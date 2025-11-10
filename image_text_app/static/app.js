document.addEventListener("DOMContentLoaded", () => {
  const copyButtons = document.querySelectorAll(".copy-btn");

  const fallbackCopy = (text, button) => {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.top = "-1000px";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    try {
      document.execCommand("copy");
      indicateSuccess(button);
    } catch (err) {
      console.error("Copy failed", err);
      indicateFailure(button);
    } finally {
      document.body.removeChild(textarea);
    }
  };

  const indicateSuccess = (button) => {
    const originalText = button.textContent;
    button.textContent = "已复制";
    button.classList.add("copied");
    setTimeout(() => {
      button.textContent = originalText;
      button.classList.remove("copied");
    }, 2000);
  };

  const indicateFailure = (button) => {
    const originalText = button.textContent;
    button.textContent = "复制失败";
    button.classList.add("copy-error");
    setTimeout(() => {
      button.textContent = originalText;
      button.classList.remove("copy-error");
    }, 2000);
  };

  copyButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetId = button.dataset.copyTarget;
      const target = document.getElementById(targetId);
      if (!target) {
        indicateFailure(button);
        return;
      }
      const text = target.textContent || "";

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard
          .writeText(text)
          .then(() => indicateSuccess(button))
          .catch(() => fallbackCopy(text, button));
      } else {
        fallbackCopy(text, button);
      }
    });
  });
});
