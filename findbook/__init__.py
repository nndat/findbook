from flask import Flask, render_template, request, flash


from .goodreads import get_books


app = Flask(__name__)
app.config['SECRET_KEY'] = 'fb5524f179bc4dd364a2d22e4a0fc5af0'\
                            'fe6f17ba102bb7e6314ab19a3cd7d41'


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    books = None
    if request.method == 'POST':
        bookname = request.form.get('book').strip()
        books = get_books(bookname)
        if books is None:
            flash(f'Không tìm thấy tên sách: "{bookname}".'
                  ' Bạn hãy thử tìm kiếm với tên khác.')
    return render_template('index.html', books=books)
