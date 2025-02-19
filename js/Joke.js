class Joke{
    constructor(data){
        this.id = data.id;
        this.categories = data.categories;
        this.createdAt = data.created_at;
        this.joke = data.value;
    }
}

module.exports = { Joke };