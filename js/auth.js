const accountes = require("../accounts.json");
const auth = (req, res, next) => {
	try {
        const token = req.headers.authorization;
        if(!accountes[token]){
            throw "Invalid user ID";
        }
        req.account = accountes[token];
        next();
	} catch {
		res.status(401).json({
			error: new Error("Invalid request!"),
		});
	}
};
module.exports = { auth };
