// assets/js/countdown-timer.js

class CountdownTimer extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const dateAttr = this.getAttribute('date');
    this.targetDate = dateAttr ? new Date(dateAttr) : null;

    this.innerHTML = `
      <div class="countdown">
        <div class="unit"><div class="number" id="days">--</div><div class="label">Days</div></div>
        <div class="unit"><div class="number" id="hours">--</div><div class="label">Hours</div></div>
        <div class="unit"><div class="number" id="minutes">--</div><div class="label">Minutes</div></div>
        <div class="unit"><div class="number" id="seconds">--</div><div class="label">Seconds</div></div>
      </div>
    `;

    if (!this.targetDate || isNaN(this.targetDate)) {
      this.querySelector('.countdown').innerHTML = "<h3>⚠️ Invalid date</h3>";
      return;
    }

    this.updateTimer();
    this.timer = setInterval(() => this.updateTimer(), 1000);
  }

  disconnectedCallback() {
    clearInterval(this.timer);
  }

  updateTimer() {
    const now = new Date().getTime();
    const diff = this.targetDate.getTime() - now;

    if (diff <= 0) {
      this.querySelector('.countdown').innerHTML = `<h1>🎉 It's here!</h1>`;
      clearInterval(this.timer);
      return;
    }

    const sec = 1000, min = sec * 60, hr = min * 60, day = hr * 24;
    const days = Math.floor(diff / day),
          hours = Math.floor((diff % day) / hr),
          minutes = Math.floor((diff % hr) / min),
          seconds = Math.floor((diff % min) / sec);

    this.querySelector("#days").innerText = days;
    this.querySelector("#hours").innerText = hours.toString().padStart(2, '0');
    this.querySelector("#minutes").innerText = minutes.toString().padStart(2, '0');
    this.querySelector("#seconds").innerText = seconds.toString().padStart(2, '0');
  }
}

customElements.define('countdown-timer', CountdownTimer);


// Optional: export for test or bundling purposes
export default CountdownTimer;
