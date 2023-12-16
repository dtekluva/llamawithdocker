# llamawithdocker

Certainly! Here's a basic template for a README file for your code snippet:

---

# Express API with Model API Integration

This repository contains a simple Express API that integrates with a Model API. The API receives a request, logs the request body, and then forwards the request to a Model API endpoint. The response from the Model API is logged and sent back to the client.

## Prerequisites

- Node.js installed on your machine.

## Getting Started

1. Clone the repository:

    ```bash
    git clone git@github.com:dtekluva/llamawithdocker.git
    ```

2. Navigate to the project directory:

    ```bash
    cd llamawithdocker/app
    ```

3. Install dependencies:

    ```bash
    npm install
    ```

4. Start the server:

    ```bash
    npm start
    ```

    The server will be running on `http://localhost:8004`.

## Usage

Make a POST request to `http://localhost:8004/api` with the required payload. The API will log the request body, forward the request to the Model API, and log the response.

Example request payload:

```json
{
  "model": "mistral",
  "prompt": "I am a boy of 20 years, I am a graduate, and from African descent. Also, I am married. What return the key metrics about me from this above text in a json object only return a json object",
  "system": "You are a very brilliant individual",
  "stream": false,
  "options": {
    "temperature": 0.3
  }
}
```


## Sample

There is a python file (make_request.py) in the root directory for testing


## Dependencies

- Express
- node-fetch
- cors


# Scalable Language Model Deployment

This repository documents the efforts to deploy and scale a language model, specifically the Mistral model, on a GPU platform called Paperspace. The application is currently being served over a Node.js server, successfully integrating the Mistral model.

## Deployment Overview

### Successful Deployment

- **Model Deployment**: Mistral model deployed on a GPU platform.
- **Server Integration**: Application successfully served over a Node.js server.

### Current Challenges

1. **Containerization**: Exploring the containerization of the application for easier deployment and scaling.
2. **JSON Response**: Ensuring the Mistral model consistently returns JSON as the response.

## Getting Started


## Contributing

Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License

---