import requests
import time

# Define the URL and parameters
url = "http://10.96.88.88"
params = {"key": "test"}

# Infinite loop to send the request repeatedly
while True:
    try:
        # Send the request
        response = requests.get(url, params=params)

        # Check the response content
        if response.text == "Echo server returns an error.\n":
            print("The response matches: Echo server returns an error.")
        else:
            print("The response does not match.")
            print("Response received:", response.text)

        # Wait for a short interval before sending the next request
        time.sleep(0.1)  # Adjust the interval as needed

    except requests.RequestException as e:
        print("An error occurred:", e)
        # Optionally, wait before retrying in case of an error
        time.sleep(5)
