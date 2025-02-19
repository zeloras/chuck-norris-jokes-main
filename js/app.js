const express = require("express");
const axios = require("axios");
const { auth } = require("./auth");
const { Joke } = require("./Joke");
const app = express();

app.get("/joke", auth, async (req, res) => {
	try {
		const { data } = await axios.get("https://api.chucknorris.io/jokes/random");
		const joke = new Joke(data);
		res.json(joke);
	} catch (err) {
		res.status(500).json({ error: 'failed to get your joke' });
	}
});

module.exports = app;
