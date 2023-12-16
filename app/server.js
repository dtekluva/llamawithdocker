const express = require("express");
const https = require("https");
const fs = require("fs");
const path = require("path");
const cors = require("cors");
//const fetch = require("node-fetch");

const app = express();
const port = 8004;

app.use(express.json());

// Routes
app.post("/api",(req, res) => {
  // Send message to Model API
  console.log(req.body)
  fetch("http://localhost:11434/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "mistral",
      prompt: "I am a boy of 20years, I am a graduate, and from african descent. Also I am married. What return the key metrics about me from this above text in a json object only return a json object",
      system: 'You are a very brilliant individual',
      stream: false,
      options: {
        temperature: 0.3,
      },
    }),
  })
   .then(response => response.json())
  .then(data=>{
    var strData = data["response"] ;

    // const extractedJSON = extractJSONFromMarkdown(strData);

        console.log(data);
        res.json({response:strData});
    });
});

function extractJSONFromMarkdown(markdownText) {
    const jsonPattern = /```json([\s\S]*?)```/g;
    const matches = markdownText.match(jsonPattern);

    if (matches) {
      return matches.map(match => match.replace(/```json/g, '').replace(/```/g, '').replace('/n', '').trim());
    }

    return [];
  };

app.listen(port, () => {
  console.log(`App listening on https://localhost:${port}`);
});