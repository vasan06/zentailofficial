document.addEventListener("mousemove", (e) => {
  const eyes = document.querySelectorAll(".dog-pupil");
  if (!eyes.length) return;

  eyes.forEach(pupil => {
    const eye = pupil.parentElement;
    const rect = eye.getBoundingClientRect();
    const eyeCenterX = rect.left + rect.width / 2;
    const eyeCenterY = rect.top + rect.height / 2;

    const dx = e.clientX - eyeCenterX;
    const dy = e.clientY - eyeCenterY;
    const angle = Math.atan2(dy, dx);

    const radius = 4; // max offset
    const offsetX = Math.cos(angle) * radius;
    const offsetY = Math.sin(angle) * radius;

    pupil.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
  });
});
