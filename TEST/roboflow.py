from flask import Flask, render_template, Response, jsonify
import requests
import cv2
import numpy as np

app = Flask(__name__)

ESP32_IP = "192.168.1.08"  
ROBOFLOW_URL = "http://localhost:9001/snowies-workspace/workflows/bike-vehicle-detection-logger-1779314546977"
API_KEY = "Kno6UrEbmrpiEYq3SLBW"

COLORS = {
    "Car":        (0, 255, 0),
    "Motorcycle": (255, 0, 0),
    "Truck":      (0, 0, 255),
    "Bus":        (255, 165, 0),
    "Bicycle":    (255, 0, 255)
}

car_status = {"car": False}

def get_frame_with_boxes():
    # image from esp
    img_resp = requests.get(f"http://{ESP32_IP}/image", timeout=5)
    img_arr  = np.frombuffer(img_resp.content, np.uint8)
    frame    = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

    # calls roboflow API (sends image URL, gets back predictions)
    payload = {
        "api_key": API_KEY,
        "inputs": {
            "image": {"type": "url", "value": f"http://{ESP32_IP}/image"}
        }
    }
    result = requests.post(ROBOFLOW_URL, json=payload, timeout=10).json()

    # 3. draw bounding boxes
    try:
        predictions = result[0]["outputs"]["predictions"]["predictions"]
        car_found   = False

        for pred in predictions:
            x, y  = int(pred["x"]), int(pred["y"])
            w, h  = int(pred["width"]), int(pred["height"])
            x1, y1 = x - w // 2, y - h // 2
            x2, y2 = x + w // 2, y + h // 2
            label  = pred["class"]
            conf   = pred["confidence"]
            color  = COLORS.get(label, (255, 255, 255))

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {conf:.0%}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if label == "Car":
                car_found = True

        # 4. status updates
        car_status["car"] = car_found
        led_state = "on" if car_found else "off"
        try:
            requests.get(f"http://{ESP32_IP}/led/{led_state}", timeout=1)
        except:
            pass

    except Exception as e:
        print("Parse error:", e)

    _, jpeg = cv2.imencode(".jpg", frame)
    return jpeg.tobytes()


def generate():
    while True:
        try:
            frame = get_frame_with_boxes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        except Exception as e:
            print("Frame error:", e)



@app.route("/")
def index():
    return render_template("test_v4.html")

@app.route("/stream")
def stream():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/status")
def status():
    return jsonify(car_status)


if __name__ == "__main__":
    print("A iniciar servidor Flask...")
    print("Abre o browser em: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True)