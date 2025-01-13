from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

data = { "Warning": None, "luminosity": 123.45, "CO2": 678.90,
        "X_axis": 12.34, "Y_axis": 56.78, "Z_axis": 90.12 }

message_received = 0
last_hazard = None

@app.route('/')
def home():
    global last_hazard, message_received

    message_received += 1

    if data['Warning'] is None:
        if last_hazard is not None and message_received > 5:
            last_hazard = None
            return render_template('allgood.html')
    elif data['Warning'] == 'Landslide':
        last_hazard = "Landslide"
        message_received = 0
        return render_template('landslide.html', data=data)
    # Data for the table
    last_hazard = "Fire"
    message_received = 0
    return render_template('fire.html', data=data)

@app.route("/info", methods=['POST'])
def refresh_info():
    message = request.json
    if not message:
        return jsonify({"error": "No JSON data received"}), 400

    info = message['message']

    data['Warning'] = info['Warning']
    data["luminosity"] = info["Luminosity"]
    data["CO2"] = info["CO2"]
    data["X_axis"], data['Y_axis'], data["Z_axis"] = info['X'], info['Y'], info['Z']

    home()

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert/CA/forestiot.local.crt', 'cert/CA/forestiot.local.key'), debug=True)
