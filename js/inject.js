document.addEventListener("DOMContentLoaded", () => {
  let prevElement = null;

  document.body.addEventListener("mousemove", async (event) => {
    const currentElement = document.elementFromPoint(
      event.clientX,
      event.clientY
    );

    if (currentElement !== prevElement) {
      await window.setElementToInspect(
        UTILS.cssPath(currentElement),
        currentElement.getBoundingClientRect()
      );

      prevElement = currentElement;
    }
  });
});
