document.addEventListener("DOMContentLoaded", function () {
  const timerElement = document.getElementById("live-timer").querySelector("span");

  let seconds = 0;

  setInterval(() => {
    seconds++;
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    timerElement.textContent = `${min}:${sec < 10 ? "0" + sec : sec}`;
  }, 1000);
});
