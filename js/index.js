require('dotenv').config();
const app = require('./app');

const start = (port) => {
    try {
        app.listen(port, () => {
          console.log(`Api running on port ${port}`);
        });
      } catch (err) {
        console.error(err);
        process.exit();
      }
}

start(process.env.PORT || 8000);
