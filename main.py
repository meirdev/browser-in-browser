import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from playwright.async_api import async_playwright


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get():
    with open("./static/index.html") as file:
        return HTMLResponse(file.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                args=[
                    "--remote-debugging-port=9222",
                    "--remote-allow-origins=*",
                ],
            )
            context = await browser.new_context()
            page = await context.new_page()
            client = await context.new_cdp_session(page)

            await page.add_init_script(path="./js/csspath.js")
            await page.add_init_script(path="./js/inject.js")

            async def set_element_to_inspect(css_path, position):
                await websocket.send_json(
                    {
                        "type": "inspect",
                        "css_path": css_path,
                        "position": position,
                    }
                )

            await context.expose_function("setElementToInspect", set_element_to_inspect)

            async def take_screenshot(event):
                await websocket.send_json(
                    {
                        "type": "screenshot",
                        "image": f"data:image/jpeg;base64,{event['data']}",
                    }
                )

                await client.send(
                    "Page.screencastFrameAck",
                    {
                        "sessionId": event["sessionId"],
                    },
                )

            client.on("Page.screencastFrame", take_screenshot)

            async def update_url(frame):
                if frame == page.main_frame:
                    await websocket.send_json({"type": "url", "url": frame.url})

            page.on("framenavigated", update_url)

            while True:
                try:
                    event = await websocket.receive_json()

                    match event["type"]:
                        case "init":
                            await page.set_viewport_size(
                                {"width": event["width"], "height": event["height"]}
                            )

                            await client.send(
                                "Page.startScreencast",
                                {
                                    "format": "jpeg",
                                    "quality": 75,
                                    "maxWidth": event["width"],
                                    "maxHeight": event["height"],
                                },
                            )
                        case "close":
                            await client.send("Page.stopScreencast")

                            break
                        case "go":
                            await page.goto(
                                url=event["url"], wait_until="domcontentloaded"
                            )
                        case "refresh":
                            await page.reload()
                        case "click":
                            await page.mouse.click(x=event["x"], y=event["y"])
                        case "dblclick":
                            await page.mouse.dblclick(x=event["x"], y=event["y"])
                        case "mousedown":
                            await page.mouse.down()
                        case "mouseup":
                            await page.mouse.up()
                        case "mousemove":
                            await page.mouse.move(x=event["x"], y=event["y"])
                        case "wheel":
                            await page.mouse.wheel(
                                delta_x=event["deltaX"], delta_y=event["deltaY"]
                            )
                        case "keyup":
                            await page.keyboard.up(key=event["key"])
                        case "keydown":
                            await page.keyboard.down(key=event["key"])
                        case "keydown":
                            await page.keyboard.down(key=event["key"])

                except (json.JSONDecodeError, KeyError) as error:
                    print("Event error:", error)

        await context.close()
        await browser.close()

    except WebSocketDisconnect:
        pass
