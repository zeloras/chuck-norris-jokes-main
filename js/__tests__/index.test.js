const request = require("supertest");
const nock = require("nock");

const app = require("../app");

describe("chuck norris server", () => {
	const scope = nock("https://api.chucknorris.io");
	describe("joke api", () => {
		it("should return 200", async () => {
			scope
				.get("/jokes/random")
				.once()
				.replyWithFile(200, __dirname + "/__mocks__/joke1.json");
			const response = await request(app)
				.get("/joke")
				.set("Authorization", "1111-2222-3333");
			expect(response.status).toEqual(200);
			expect(response.body).toMatchSnapshot();
		});
		it("should return 401", async () => {
			const response = await request(app).get("/joke");
			expect(response.status).toEqual(401);
		});
		it("should return 500", async () => {
			scope.get("/jokes/random").once().reply(500, {});
			const response = await request(app)
				.get("/joke")
				.set("Authorization", "1111-2222-3333");
			expect(response.status).toEqual(500);
		});
	});
});
