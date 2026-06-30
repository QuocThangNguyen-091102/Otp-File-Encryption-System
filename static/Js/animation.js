
// Sao băng
const canvas = document.getElementById("shootingStars");
const ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
window.addEventListener("resize", () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});
class Star {
  constructor() { this.reset(); }
  reset() {
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height * 0.5;
    this.len = Math.random() * 80 + 10;
    this.speed = Math.random() * 10 + 6;
    this.angle = Math.PI / 4;
    this.opacity = Math.random() * 0.5 + 0.5;
  }
  draw() {
    ctx.beginPath();
    ctx.moveTo(this.x, this.y);
    ctx.lineTo(this.x - this.len * Math.cos(this.angle), this.y - this.len * Math.sin(this.angle));
    ctx.strokeStyle = `rgba(255,255,255,${this.opacity})`;
    ctx.lineWidth = 2;
    ctx.stroke();
  }
  update() {
    this.x += this.speed;
    this.y += this.speed;
    if (this.x > canvas.width || this.y > canvas.height) {
      this.reset();
      this.x = 0;
      this.y = Math.random() * canvas.height * 0.5;
    }
    this.draw();
  }
}
let stars = [];
for (let i = 0; i < 10; i++) stars.push(new Star());
function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  stars.forEach((s) => s.update());
  requestAnimationFrame(animate);
}
animate();
