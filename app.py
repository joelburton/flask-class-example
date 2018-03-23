from flask import Flask, url_for, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///gamesdb"
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

modus = Modus(app)
db = SQLAlchemy(app)


class Game(db.Model):
    """Boardgame."""

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.Text, nullable=False, unique=True)
    description = db.Column(db.Text)
    imageUrl = db.Column(db.Text)

    @classmethod
    def add(cls, title, description=None, imageUrl=None):
        """Add a new game to the database."""

        game = cls(
            title=title,
            description=description,
            imageUrl=imageUrl,
        )
        db.session.add(game)
        db.session.commit()
        return game

    @property
    def url(self):
        """URL for this game."""

        return url_for('game_detail', game_id=self.id)

    def edit(self, title, description, imageUrl):
        """Update & save."""

        self.title = title
        self.description = description
        self.imageUrl = imageUrl
        db.session.commit()

    def remove(self):
        """Delete & save."""

        db.session.delete(self)
        db.session.commit()


from flask.views import MethodView


class GameView(MethodView):
    """RESTful views for Game."""

    def get(self, game_id=None):
        """Handle listing of games and listing of a single game."""

        if game_id is None:
            return self._listing()
        else:
            return self._detail(game_id)

    def _listing(self):
        """Show listing of games."""

        games = Game.query.all()
        return render_template("game_listing.html", games=games)

    def _detail(self, game_id):
        """Show detail of a single game."""

        game = Game.query.get_or_404(game_id)
        return render_template("game_detail.html", game=game)

    def post(self):
        """Handle adding of a new game."""

        title = request.form['title']
        description = request.form['description']
        imageUrl = request.form['imageUrl']

        game = Game.add(title, description, imageUrl)
        return redirect(game.url)

    def delete(self, game_id):
        """Handle deleting of a game."""

        game = Game.query.get_or_404(game_id)
        game.remove()
        db.session.commit()
        return redirect(url_for("games_listing"))

    def patch(self, game_id):
        """Handle updating of a game."""

        game = Game.query.get_or_404(game_id)
        game.edit(
            title=request.form['title'],
            description=request.form['description'],
            imageUrl=request.form['imageUrl'],
        )
        return redirect(game.url)


game_view = GameView.as_view("")

app.add_url_rule("/", "games_listing", game_view, methods=['GET'])
app.add_url_rule("/", "game_add", game_view, methods=["POST"])
app.add_url_rule("/<int:game_id>", "game_detail", game_view, methods=['GET'])
app.add_url_rule("/<int:game_id>", "game_del", game_view, methods=['DELETE'])
app.add_url_rule("/<int:game_id>", "game_edit", game_view, methods=['PATCH'])


@app.route("/new")
def game_add_form():
    """Show form for adding a game."""

    return render_template("game_add_form.html")


@app.route("/<int:game_id>/edit")
def game_edit_form(game_id):
    """Show edit form for editing a game."""

    game = Game.query.get_or_404(game_id)
    return render_template("game_edit_form.html", game=game)
