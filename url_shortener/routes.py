from flask import Blueprint, render_template, request, redirect, jsonify
import validators
from .extensions import db
from .models import Link
from flask_cors import CORS
from urllib.parse import urlparse
import validators
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
    return jsonify({"message":"welcome to the api service"})


@short.route('/add_link', methods=['POST'])
def add_link():
    data = request.get_json()
    original_url = data.get('original_url', None)
    if not original_url:
        return jsonify({"Error": "please supply an original url!"}), 400

    link = Link.query.filter_by(original_url=original_url).first()
    if link:
        return jsonify({"Error": "Already a shortened link"}), 400
    if not validators.url(original_url):
        return jsonify({"Error": "The link is Invalid"}), 400

    link = Link(original_url=original_url)
    db.session.add(link)
    db.session.commit()
    return jsonify({"new_link": request.url_root+link.short_url, "original_url": link.original_url}), 201


@short.route('/stats')
def stats():
    links = Link.query.all()
    json_data = []
    for link in links:
        newLink = {"visits": link.visits,
                   "original": link.original_url, "short": request.url_root+link.short_url, "id": link.id}
        json_data.append(newLink)

    return jsonify({"stats": json_data})


@short.errorhandler(404)
def page_not_found(e):
    return jsonify({"Error": 'not found'}), 404
