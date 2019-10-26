class Book():
    def __init__(self, title, author, rating, image_url):
        self.title = title
        self.author = author
        self.rating = rating
        self.image_url = image_url

    def __str__(self):
        return self.title
