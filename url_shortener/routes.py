from flask import Blueprint, render_template, request, redirect, jsonify
import validators
from .extensions import db
from .models import Link
from flask_cors import CORS
from urllib.parse import urlparse
short = Blueprint('short', __name__)

CORS(short)


@short.route('/<short_url>')
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    link.visits = link.visits + 1
    db.session.commit()
    return redirect(link.original_url)


@short.route('/')
def index():
    return render_template('index.html')


@short.route('/add_link', methods=['POST'])
def add_link():
    data = request.get_json()
    original_url = data.get('original_url', None)
    if not original_url:
        return jsonify({"Error": "please supply an original url!"}), 400
    link = Link(original_url=original_url['url'])
    db.session.add(link)
    db.session.commit()
    return jsonify({"new_link": request.url_root+link.short_url, "original_url": link.original_url})


@short.route('/stats')
def stats():
    links = Link.query.all()
    json_data = []
    for link in links:
        newLink = {"visits": link.visits,
                   "original": link.original_url, "short": request.url_root+link.short_url}
        json_data.append(newLink)

    return jsonify({"stats": json_data})


@short.errorhandler(404)
def page_not_found(e):
    return jsonify('not found'), 404
