const body = document.body;

const canvas = document.getElementById("screenshot");
const context = canvas.getContext("2d");

const go = document.querySelector("#go");
const url = document.querySelector("#url");
const refresh = document.querySelector("#refresh");

const wsUrl = "ws://localhost:8000/ws";

const width = 1280;
const height = 1024;

const ws = new WebSocket(wsUrl);

let lastInspected;

const sendEvent = (type, data) => {
  if (data === undefined) {
    data = {};
  }

  ws.send(JSON.stringify({ type, ...data }));
};

const mousePosition = (event, element) => {
  const { left, top } = element.getBoundingClientRect();
  const { clientX, clientY } = event;

  return { x: clientX - left, y: clientY - top };
};

ws.onopen = () => {
  sendEvent("init", { width, height });
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case "screenshot":
      {
        const img = new Image();

        img.onload = () => {
          context.drawImage(img, 0, 0, canvas.width, canvas.height);

          if (lastInspected) {
            const { x, y, width, height } = lastInspected.position;

            context.fillStyle = "rgba(255, 0, 0, 0.3)";
            context.fillRect(x, y, width, height);

            context.font = "10px";
            context.fillStyle = "#000";

            const textWidth = context.measureText(lastInspected.css_path).width;

            context.fillText(lastInspected.css_path, x, y, textWidth, 12);
          }
        };

        img.src = data.image;
      }
      break;
    case "url":
      {
        url.value = data.url;
      }
      break;
    case "inspect":
      {
        lastInspected = data;
      }
      break;
  }
};

ws.onclose = () => {
  sendEvent("close");
};

go.addEventListener("click", () => {
  sendEvent("go", { url: url.value });
});

canvas.addEventListener("click", (event) => {
  sendEvent("click", mousePosition(event, canvas));
});

canvas.addEventListener("dblclick", (event) => {
  sendEvent("dblclick", mousePosition(event, canvas));
});

canvas.addEventListener("wheel", (event) => {
  sendEvent("wheel", { deltaX: event.deltaX, deltaY: event.deltaY });
});

canvas.addEventListener("mousemove", (event) => {
  sendEvent("mousemove", mousePosition(event, canvas));
});

canvas.addEventListener("mouseup", () => {
  sendEvent("mouseup");
});

canvas.addEventListener("mousedown", () => {
  sendEvent("mousedown");
});

body.addEventListener("keyup", (event) => {
  if (event.target !== url) {
    sendEvent("keyup", { key: event.key });
  }
});

body.addEventListener("keydown", (event) => {
  if (event.target !== url) {
    sendEvent("keydown", { key: event.key });
  }
});
